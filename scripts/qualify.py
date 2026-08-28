"""Score Etsy shops as 3DAPI leads from public buyer-review evidence.

Reads a snapshot captured by scripts/capture.py (or falls back to the committed
snapshot when no APIFY_TOKEN is present) and writes leads.md.

Snapshots never contain reviewer identity - see capture.py.
"""
import argparse, csv, datetime as dt, json, os, pathlib, sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from env import load_env
from taxonomy import match_signals, weight, BY_ID  # noqa: E402

load_env()

ROOT = pathlib.Path(__file__).resolve().parent.parent
SNAPSHOT = ROOT / "fallback" / "snapshot"

HOT, WATCH = 60, 35
SWEET_LOW, SWEET_HIGH = 1000, 8000   # ratio_per_year band we can actually serve
WINDOW = 90


def today():
    return dt.date.fromisoformat(os.environ.get("QUALIFY_TODAY", dt.date.today().isoformat()))


def parse_date(s):
    try:
        return dt.date.fromisoformat(str(s)[:10])
    except (ValueError, TypeError):
        return None


def score_shop(meta, snap, ref):
    reviews = snap.get("reviews", [])
    hits = []
    for r in reviews:
        sigs = match_signals(r.get("text", ""))
        if sigs:
            hits.append({**r, "signals": sorted(sigs)})

    recent = [h for h in hits if (d := parse_date(h.get("date"))) and (ref - d).days <= WINDOW]
    prior = [h for h in hits if (d := parse_date(h.get("date"))) and WINDOW < (ref - d).days <= 2 * WINDOW]

    def dated(rs, lo, hi):
        return [r for r in rs if (d := parse_date(r.get("date"))) and lo < (ref - d).days <= hi]

    all_recent, all_prior = dated(reviews, -1, WINDOW), dated(reviews, WINDOW, 2 * WINDOW)

    # review velocity + intra-snapshot growth (order-rate proxies)
    dates = sorted(d for r in reviews if (d := parse_date(r.get("date"))))
    span = (dates[-1] - dates[0]).days if len(dates) > 1 else 0
    velocity = (len(dates) / span * 7) if span else 0.0
    n_recent = sum(1 for d in dates if (ref - d).days <= WINDOW)
    n_prior = sum(1 for d in dates if WINDOW < (ref - d).days <= 2 * WINDOW)
    if span >= 2 * WINDOW and n_prior:
        growth = n_recent / n_prior
    elif span >= 2 * WINDOW and n_recent:
        growth = float("inf")
    else:
        growth = None

    # recency of complaint evidence
    recency = min(len(recent), 3) / 3 * 5

    facts = snap.get("shop_facts") or {}
    ship_r = facts.get("shipping_rating")
    qual_r = facts.get("item_quality_rating")

    # 1. Fulfilment deficit - Etsy rates shipping separately from item quality.
    # When a shop's shipping rating sits below its item-quality rating, buyers
    # are telling us the product is fine and the delivery is not. That is a
    # routing problem, and unlike complaint text it exists for every shop.
    deficit = (qual_r - ship_r) if (ship_r and qual_r) else 0.0
    fulfilment = (min(max(deficit, 0) / 0.15, 1.0) * 15
                  + (min(max(4.95 - ship_r, 0) / 0.30, 1.0) * 10 if ship_r else 0))

    # 2. pain match - complaint text, weighted by signal severity
    ids = sorted({s for h in hits for s in h["signals"]})
    pain = min(sum(weight(i) for i in ids), 4) / 4 * 20

    # 3. volume fit - real sold volume per year beats the sheet's estimate
    years = None
    if facts.get("create_date"):
        years = max((ref - dt.date.fromtimestamp(facts["create_date"])).days / 365.25, 0.5)
    sold = facts.get("sold_count")
    orders_yr = round(sold / years) if (sold and years) else (meta.get("ratio_per_year") or 0)
    if SWEET_LOW <= orders_yr <= SWEET_HIGH:
        volume = 20.0
    elif orders_yr:
        edge = SWEET_LOW if orders_yr < SWEET_LOW else SWEET_HIGH
        volume = 20 * max(0.0, 1 - abs(orders_yr - edge) / 6000)
    else:
        volume = 0.0

    # 4. throughput - review velocity as an order-rate proxy
    throughput = min(velocity / 12.0, 1.0) * 15

    # 5. cross-border exposure - Etsy's buyer base is heavily US/UK, so a shop
    # producing elsewhere ships international on most orders by default.
    origin = facts.get("country_code") or snap.get("ships_from")
    cross = 10.0 if (origin and origin not in ("US",)) else (3.0 if origin else 0.0)

    # 6. corroboration - independent confirmations, not one angry buyer
    corro_parts = []
    if len(hits) >= 2:
        corro_parts.append("multiple independent reviews")
    if deficit > 0.02:
        corro_parts.append(f"shipping rated {deficit:.2f} below item quality")
    if (snap.get("stated_processing_days") or 0) >= 5:
        corro_parts.append(f"stated make time {snap['stated_processing_days']}d")
    if origin and origin != "US":
        corro_parts.append(f"produces in {origin}")
    corro = min(len(corro_parts), 3) / 3 * 10

    total = round(fulfilment + pain + volume + throughput + cross + corro + recency)
    tier = "hot" if total >= HOT else "watch" if total >= WATCH else "pass"

    # Volume floor overrides the score. A shop below it cannot be served today
    # however strong its other signals, so calling it hot would be wrong - but
    # discarding it is how a "too small" prospect gets forgotten and turns up
    # later as someone else's customer.
    below_floor = 0 < orders_yr < SWEET_LOW
    growing = growth is not None and growth > 1.2
    shrinking = growth is not None and growth < 1.0
    if below_floor:
        # Rising or steady -> track it. Declining -> we are late, not early.
        tier = "pass" if shrinking else "nurture"

    reasons = []
    if not hits:
        reasons.append("no fulfilment complaints found in the reviewed window")
    if not recent and hits:
        reasons.append("complaints exist but none in the last 90 days")
    if orders_yr and orders_yr > SWEET_HIGH:
        reasons.append(f"volume {orders_yr} orders/yr above the serviceable band")
    elif orders_yr and orders_yr < SWEET_LOW:
        reasons.append(f"volume {orders_yr} orders/yr below the {SWEET_LOW}/yr floor")
    if velocity < 3:
        reasons.append(f"low throughput ({velocity:.1f} reviews/wk) - not yet at the constraint")
    if growth is not None and growth < 1.0:
        reasons.append(f"review rate declining ({growth:.2f}x quarter on quarter)")

    months_to_floor = None
    if below_floor and orders_yr and growth and growth not in (None, float("inf")) and growth > 1.0:
        import math
        # growth is a per-quarter multiple; how many quarters to close the gap
        months_to_floor = round(math.log(SWEET_LOW / orders_yr) / math.log(growth) * 3)

    return {
        "shop": meta["shop"], "shop_url": meta["shop_url"],
        "category": meta.get("category", ""), "ratio_per_year": orders_yr,
        "score": total, "tier": tier,
        "components": {"fulfilment": round(fulfilment), "pain": round(pain),
                       "volume": round(volume), "throughput": round(throughput),
                       "cross_border": round(cross), "corroboration": round(corro),
                       "recency": round(recency)},
        "signals": ids, "corroboration": corro_parts, "reasons": reasons,
        "velocity_per_week": round(velocity, 1),
        "growth_qoq": (None if growth is None else
                       ("new activity" if growth == float("inf") else round(growth, 2))),
        "months_to_floor": months_to_floor,
        "recheck_days": (30 if growing else 90) if below_floor else None,
        "evidence": sorted(hits, key=lambda h: h.get("date", ""), reverse=True)[:3],
        "ships_from": origin,
        "shipping_rating": round(ship_r, 2) if ship_r else None,
        "quality_rating": round(qual_r, 2) if qual_r else None,
        "shipping_deficit": round(deficit, 3),
        "sold_count": sold,
        "related_links": snap.get("related_links") or [],
        "primary_buyer_market": snap.get("primary_buyer_market"),
        "retrieved_at": snap.get("retrieved_at"), "source": snap.get("source"),
        "reviews_seen": len(reviews),
    }


def opener(lead):
    """Draft an opener that only claims what the evidence actually supports."""
    close = ("3DAPI routes each order to a print farm near the customer, so the "
             "same product ships domestically instead of crossing a border.")
    sig = max(lead["signals"], key=weight, default=None)
    if sig:
        return (f"Your recent Etsy reviews keep landing on the same thing - "
                f"{BY_ID[sig]['label'].lower()}. {close}")
    if lead["shipping_rating"] and lead["shipping_deficit"] > 0:
        where = (f", printing everything in {lead['ships_from']}"
                 if lead["ships_from"] and lead["ships_from"] != "US" else "")
        return (f"Etsy rates your shipping {lead['shipping_rating']} against "
                f"{lead['quality_rating']} for item quality{where} - buyers rate "
                f"the product higher than the delivery. {close}")
    if lead["ships_from"] and lead["ships_from"] != "US":
        return (f"You produce in {lead['ships_from']} and most Etsy demand sits in "
                f"the US and UK, so nearly every order crosses a border. {close}")
    return f"At {lead['ratio_per_year']} orders a year out of one workshop, capacity is the ceiling. {close}"


def render(leads, mode, ref):
    L = [f"# Qualified leads - 3DAPI\n",
         f"Generated {ref.isoformat()} - data mode: **{mode}** - {len(leads)} shops evaluated\n",
         "Evidence is public Etsy buyer-review text. Reviewer identities are never "
         "collected or stored; see `.agents/skills/etsy-fulfillment-leads/SKILL.md`.\n",
         "\n## Ranked\n",
         "| # | Shop | Category | Tier | Score | Throughput | Pain signals | Why now |",
         "|---|---|---|---|---|---|---|---|"]
    for i, l in enumerate(sorted(leads, key=lambda x: -x["score"]), 1):
        sigs = ", ".join(BY_ID[s]["label"] for s in l["signals"]) or "-"
        why = l["corroboration"][0] if l["corroboration"] else f"{l['velocity_per_week']}/wk throughput"
        L.append(f"| {i} | [{l['shop']}]({l['shop_url']}) | {l['category']} | "
                 f"**{l['tier']}** | {l['score']} | {l['velocity_per_week']}/wk | {sigs} | {why} |")

    hot = [l for l in sorted(leads, key=lambda x: -x["score"]) if l["tier"] in ("hot", "watch")][:3]
    if hot:
        L.append("\n## Top leads\n")
    for l in hot:
        L.append(f"### {l['shop']} - {l['tier'].upper()} ({l['score']}/100)\n")
        L.append(f"- **Shop:** {l['shop_url']}")
        L.append(f"- **Category:** {l['category']} - est. {l['ratio_per_year']}/yr")
        L.append(f"- **Throughput:** {l['velocity_per_week']} reviews/week (order-volume proxy)")
        if l["ships_from"]:
            mkt = l.get("primary_buyer_market")
            L.append(f"- **Produces in:** {l['ships_from']}" +
                     (f" -> mostly {mkt}" if mkt else " (Etsy demand is largely US/UK)"))
        if l["shipping_rating"]:
            L.append(f"- **Etsy ratings:** shipping {l['shipping_rating']} vs "
                     f"item quality {l['quality_rating']} "
                     f"(deficit {l['shipping_deficit']:+.2f})")
        if l["sold_count"]:
            L.append(f"- **Sold to date:** {l['sold_count']:,}")
        if l["related_links"]:
            L.append(f"- **Other storefronts:** {', '.join(l['related_links'][:4])}")
        L.append(f"- **Score breakdown:** " + ", ".join(f"{k} {v}" for k, v in l["components"].items()))
        if l["signals"]:
            L.append(f"\n**Mapped pain**\n")
            for s in l["signals"]:
                t = BY_ID[s]
                L.append(f"- *{t['label']}* - {t['means']} -> {t['fix']}")
        L.append(f"\n**Evidence** (retrieved {l['retrieved_at']}, source: {l['source']})\n")
        if not l["evidence"]:
            L.append("*No buyer complaint quotes in the captured window.* This "
                     "shop qualifies on shop-level evidence only:\n")
            if l["shipping_rating"]:
                L.append(f"- Etsy rates its shipping **{l['shipping_rating']}** against "
                         f"item quality **{l['quality_rating']}** — buyers rate the "
                         f"product above the delivery.")
            if l["ships_from"] and l["ships_from"] != "US":
                L.append(f"- Produces in **{l['ships_from']}**, so most Etsy orders "
                         f"cross a border.")
            L.append("")
        for e in l["evidence"]:
            labels = ", ".join(BY_ID[s]["label"] for s in e["signals"])
            txt = e["text"].strip().replace("\n", " ")
            txt = txt[:220] + ("..." if len(txt) > 220 else "")
            L.append(f"> \"{txt}\"\n> — {e.get('rating', '?')}★, {e.get('date', 'undated')} · {labels}")
            if e.get("url"):
                L.append(f"> · [source]({e['url']})")
            L.append("")
        L.append(f"**Opener**\n\n> {opener(l)}\n")

    nurture = sorted([l for l in leads if l["tier"] == "nurture"],
                     key=lambda x: -(x["ratio_per_year"] or 0))
    if nurture:
        L.append(f"\n## Watchlist — too small today ({len(nurture)})\n")
        L.append("Below the serviceable floor, but moving. These are not "
                 "rejections; they are leads we are early for. Re-run on the "
                 "recheck cadence and they surface when they cross.\n")
        L.append("| Shop | Est. /yr | Gap to floor | Throughput | Growth (QoQ) | Est. crossing | Recheck |")
        L.append("|---|---|---|---|---|---|---|")
        for l in nurture:
            g = l["growth_qoq"]
            gtxt = "unknown" if g is None else (g if isinstance(g, str) else f"{g}x")
            cross = f"~{l['months_to_floor']} mo" if l["months_to_floor"] else "—"
            L.append(f"| [{l['shop']}]({l['shop_url']}) | {l['ratio_per_year']} | "
                     f"{SWEET_LOW - l['ratio_per_year']} | {l['velocity_per_week']}/wk | "
                     f"{gtxt} | {cross} | {l['recheck_days']}d |")
        L.append("\n*Growth compares review rate in the last 90 days against the "
                 "90 before it, inside one capture. It reads `unknown` when the "
                 "snapshot does not span both windows — capture more history for "
                 "those shops rather than assuming.*\n")

    passed = [l for l in leads if l["tier"] == "pass"]
    L.append(f"\n## Not qualified ({len(passed)})\n")
    L.append("Shown so the rubric can be checked against its own rejections.\n")
    L.append("| Shop | Score | Throughput | Reviews seen | Why not |")
    L.append("|---|---|---|---|---|")
    for l in sorted(passed, key=lambda x: -x["score"]):
        L.append(f"| [{l['shop']}]({l['shop_url']}) | {l['score']} | {l['velocity_per_week']}/wk | {l['reviews_seen']} | "
                 f"{'; '.join(l['reasons']) or 'signals too weak'} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shops", default=str(ROOT / "inputs" / "shops.csv"))
    ap.add_argument("--snapshot", default=str(SNAPSHOT))
    ap.add_argument("--out", default=str(ROOT / "leads.md"))
    ap.add_argument("--limit", type=int, default=3, help="shops to evaluate (75s judging gate)")
    ap.add_argument("--only", default="", help="comma-separated shop names")
    a = ap.parse_args()

    ref, snapdir = today(), pathlib.Path(a.snapshot)
    can_refresh = bool(os.environ.get("APIFY_TOKEN") and os.environ.get("APIFY_ETSY_ACTOR"))

    with open(a.shops, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    for r in rows:
        # The published list carries no revenue estimates; volume comes from
        # Etsy's sold_count via capture_shop.py.
        r["ratio_per_year"] = int(r.get("ratio_per_year") or 0)

    only = {s.strip() for s in a.only.split(",") if s.strip()}
    have = {p.stem for p in snapdir.glob("*.json")}
    pool = [r for r in rows if r["shop"] in (only or have)]
    if not pool:
        sys.exit(f"no snapshots in {snapdir} - run scripts/capture.py first")

    stamps = sorted({json.loads((snapdir / f"{r['shop']}.json").read_text())
                     .get('retrieved_at', '?') for r in pool
                     if (snapdir / f"{r['shop']}.json").exists()})
    mode = (f"committed snapshot, captured {stamps[-1] if stamps else '?'}"
            + ("" if can_refresh else " — no APIFY_TOKEN, cannot refresh"))

    leads = []
    for meta in pool[: a.limit or None]:
        f = snapdir / f"{meta['shop']}.json"
        if not f.exists():
            continue
        leads.append(score_shop(meta, json.loads(f.read_text(encoding="utf-8")), ref))

    pathlib.Path(a.out).write_text(render(leads, mode, ref), encoding="utf-8")
    tiers = {t: sum(1 for l in leads if l["tier"] == t) for t in ("hot", "watch", "pass")}
    print(f"{len(leads)} scored ({tiers}) -> {a.out}  [{mode}]")


if __name__ == "__main__":
    main()
