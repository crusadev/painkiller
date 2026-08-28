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

    # 1. pain match - how many distinct failure modes appear at all
    ids = sorted({s for h in hits for s in h["signals"]})
    pain = min(sum(weight(i) for i in ids), 4) / 4 * 30

    # 2. recency - is the pain live, or history
    recency = min(len(recent), 3) / 3 * 15

    # 3. throughput - how fast the shop is actually shipping orders.
    # Review dates are the only public proxy for order volume, and on this
    # corpus they spread across two orders of magnitude. A shop clearing 20
    # orders a week from one workshop is scaling into the constraint; a shop
    # clearing one is not, whatever its reviews say.
    dates = sorted(d for r in reviews if (d := parse_date(r.get("date"))))
    span = (dates[-1] - dates[0]).days if len(dates) > 1 else 0
    velocity = (len(dates) / span * 7) if span else 0.0
    throughput = min(velocity / 12.0, 1.0) * 20

    # Growth from one capture: review rate in the last 90 days vs the 90 before
    # it. Only meaningful when the snapshot actually spans both windows - a
    # 60-review cap on a fast shop covers weeks, not months, so we say unknown
    # rather than guessing.
    n_recent = sum(1 for d in dates if (ref - d).days <= WINDOW)
    n_prior = sum(1 for d in dates if WINDOW < (ref - d).days <= 2 * WINDOW)
    if span >= 2 * WINDOW and n_prior:
        growth = n_recent / n_prior
    elif span >= 2 * WINDOW and n_recent:
        growth = float("inf")
    else:
        growth = None

    # 4. volume fit - big enough to matter, small enough to need us
    ratio = meta.get("ratio_per_year") or 0
    if SWEET_LOW <= ratio <= SWEET_HIGH:
        volume = 20.0
    elif ratio:
        volume = 20 * max(0.0, 1 - (abs(ratio - (SWEET_LOW if ratio < SWEET_LOW else SWEET_HIGH)) / 6000))
    else:
        volume = 0.0

    # 5. corroboration - independent confirmations, not one angry buyer
    corro_parts = []
    if len(hits) >= 2:
        corro_parts.append("multiple independent reviews")
    if (snap.get("stated_processing_days") or 0) >= 5:
        corro_parts.append(f"stated make time {snap['stated_processing_days']}d")
    if snap.get("ships_from") and snap.get("primary_buyer_market") and \
            snap["ships_from"] != snap["primary_buyer_market"]:
        corro_parts.append(f"ships {snap['ships_from']}->{snap['primary_buyer_market']}")
    corro = min(len(corro_parts), 3) / 3 * 15

    total = round(pain + recency + throughput + volume + corro)
    tier = "hot" if total >= HOT else "watch" if total >= WATCH else "pass"

    # A shop below the serviceable floor is not a rejection - it is a lead we
    # are early for. Losing those is how a "too small" prospect gets forgotten
    # and shows up later as someone else's customer.
    below_floor = 0 < ratio < SWEET_LOW
    growing = growth is not None and growth > 1.2
    shrinking = growth is not None and growth < 1.0
    # Track the small-but-rising. A shop below the floor and *declining* is not
    # a lead we are early for, it is one we are late for.
    if tier == "pass" and below_floor and not shrinking and (growing or velocity >= 1.0):
        tier = "nurture"

    reasons = []
    if not hits:
        reasons.append("no fulfilment complaints found in the reviewed window")
    if not recent and hits:
        reasons.append("complaints exist but none in the last 90 days")
    if ratio and ratio > SWEET_HIGH:
        reasons.append(f"volume {ratio}/yr above the serviceable band")
    elif ratio and ratio < SWEET_LOW:
        reasons.append(f"volume {ratio}/yr below the {SWEET_LOW}/yr floor")
    if velocity < 3:
        reasons.append(f"low throughput ({velocity:.1f} reviews/wk) - not yet at the constraint")
    if growth is not None and growth < 1.0:
        reasons.append(f"review rate declining ({growth:.2f}x quarter on quarter)")

    months_to_floor = None
    if below_floor and growth and growth not in (None, float("inf")) and growth > 1.0:
        import math
        # growth is a per-quarter multiple; how many quarters to close the gap
        months_to_floor = round(math.log(SWEET_LOW / ratio) / math.log(growth) * 3)

    return {
        "shop": meta["shop"], "shop_url": meta["shop_url"],
        "category": meta.get("category", ""), "ratio_per_year": ratio,
        "score": total, "tier": tier,
        "components": {"pain": round(pain), "recency": round(recency),
                       "throughput": round(throughput), "volume": round(volume),
                       "corroboration": round(corro)},
        "signals": ids, "corroboration": corro_parts, "reasons": reasons,
        "velocity_per_week": round(velocity, 1),
        "growth_qoq": (None if growth is None else
                       ("new activity" if growth == float("inf") else round(growth, 2))),
        "months_to_floor": months_to_floor,
        "recheck_days": (30 if growing else 90) if below_floor else None,
        "evidence": sorted(hits, key=lambda h: h.get("date", ""), reverse=True)[:3],
        "ships_from": snap.get("ships_from"),
        "primary_buyer_market": snap.get("primary_buyer_market"),
        "retrieved_at": snap.get("retrieved_at"), "source": snap.get("source"),
        "reviews_seen": len(reviews),
    }


def opener(lead):
    # lead with the sharpest signal, not the alphabetically first one
    sig = max(lead["signals"], key=weight, default=None)
    pain = BY_ID[sig]["label"].lower() if sig else "fulfilment"
    route = ""
    if lead.get("ships_from") and lead.get("primary_buyer_market"):
        route = f" You print in {lead['ships_from']} and most of these buyers are in {lead['primary_buyer_market']}."
    return (f"Your recent Etsy reviews keep landing on the same thing - {pain}.{route} "
            f"3DAPI routes each order to a print farm near the customer, so the same "
            f"product ships domestically instead of crossing a border.")


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
            L.append(f"- **Ships from:** {l['ships_from']} -> mostly {l['primary_buyer_market']}")
        L.append(f"- **Score breakdown:** " + ", ".join(f"{k} {v}" for k, v in l["components"].items()))
        L.append(f"\n**Mapped pain**\n")
        for s in l["signals"]:
            t = BY_ID[s]
            L.append(f"- *{t['label']}* - {t['means']} -> {t['fix']}")
        L.append(f"\n**Evidence** (retrieved {l['retrieved_at']}, source: {l['source']})\n")
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
        r["ratio_per_year"] = int(r["ratio_per_year"]) if r["ratio_per_year"] else 0

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
