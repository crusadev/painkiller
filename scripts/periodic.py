#!/usr/bin/env python3
"""Stage 3 - the periodic run.

Sweeps the watchlist produced by Stage 1/2 and reports which prospects are ripe
now, and why. The output is a ripeness likelihood, not a yes/no: a prospect sits
somewhere between "not yet" and "call today", and the report says where, what
moved it there, and how much of the rubric it could actually evaluate.

Runs with no credentials, against committed evidence.

    python3 scripts/periodic.py
    python3 scripts/periodic.py --profile state/profile.json --limit 5
"""
import argparse
import datetime
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

try:
    from taxonomy import match_signals
except Exception:  # metric-only path still works without the taxonomy
    match_signals = None

# Where a real deployment keeps its own profile and watchlist. Falls back to the
# committed demo so the skill is runnable by anyone, on any machine, with no
# local data of their own.
STATE = ("state/profile.json", "state/watchlist.json")
DEMO = ("demo/input/profile.json", "demo/input/watchlist.json")


def resolve(p):
    """Accept an absolute path, a cwd-relative path, or a repo-relative one."""
    path = pathlib.Path(p).expanduser()
    if path.is_absolute() or path.exists():
        return path
    return ROOT / p


def default_pair():
    """Prefer this deployment's own state; fall back to the shipped demo."""
    prof, watch = (resolve(x) for x in STATE)
    if prof.exists() and watch.exists():
        return STATE
    return DEMO


def progress(done, total, label):
    """Emit a decile marker so a long sweep stays legible while it runs."""
    if not total:
        return
    pct = done * 100 // total
    prev = (done - 1) * 100 // total if done else 0
    if done == total or pct // 10 > prev // 10:
        print("  [%3d%%] %d/%d %s" % (pct, done, total, label), flush=True)


def band_fit(x, lo, hi):
    """1.0 inside the band, tapering off outside it. None if unmeasurable."""
    if x is None:
        return None
    if lo <= x <= hi:
        return 1.0
    if x < lo:
        return max(0.0, float(x) / lo) * 0.6
    return max(0.0, float(hi) / x) * 0.6


def keyword_hits(shop_name, snap_dir):
    """Taxonomy signals in this shop's captured reviews, with up to two quotes.

    Returns (signals, quotes, available). `available` is False when there is no
    review corpus for this prospect at all — a deployment that tracks metrics
    only, or a prospect not yet captured. That is reported as unassessed rather
    than scored as zero.
    """
    if match_signals is None or snap_dir is None:
        return [], [], False
    snap = snap_dir / (shop_name + ".json")
    if not snap.exists():
        return [], [], False
    try:
        data = json.loads(snap.read_text(encoding="utf-8"))
    except Exception:
        return [], [], False
    found = set()
    quotes = []
    for r in data.get("reviews", []):
        sigs = match_signals(r.get("text") or "")
        if sigs:
            found |= set(sigs)
            if len(quotes) < 2:
                quotes.append({
                    "text": (r.get("text") or "")[:180],
                    "date": r.get("date"),
                    "url": r.get("url"),
                })
    return sorted(found), quotes, True


def assess(shop, triggers, snap_dir=None):
    """Score one prospect. Returns ripeness 0-100 plus the drivers behind it.

    Weights come from the profile, so retargeting the skill to another business
    means editing state/profile.json, not this function.
    """
    drivers = []
    missing = []
    score = 0.0
    possible = 0.0
    evaluated = 0
    quotes = []

    # 1. Fulfilment deficit - the one signal that exists for every shop.
    t = triggers.get("fulfilment_deficit")
    if t:
        possible += t["weight"]
        q = shop.get("item_quality_rating")
        s = shop.get("shipping_rating")
        if q and s:
            evaluated += 1
            gap = q - s
            frac = min(1.0, gap / (t["fires_at"] * 3.0)) if gap > 0 else 0.0
            score += t["weight"] * frac
            if gap >= t["fires_at"]:
                drivers.append(
                    "shipping %.2f sits %.2f below quality %.2f - their own buyers rate "
                    "the delivery worse than the product" % (s, gap, q))
        else:
            missing.append("no published shipping/quality ratings")

    # 2. Serviceable volume. Below the floor is early, not unqualified.
    t = triggers.get("serviceable_volume")
    if t:
        possible += t["weight"]
        lo, hi = t["band"]
        v = shop.get("orders_per_year")
        fit = band_fit(v, lo, hi)
        if fit is None:
            missing.append("no volume figure")
        else:
            evaluated += 1
            score += t["weight"] * fit
            if v < lo:
                drivers.append("~%s orders/yr is below the %s floor - early, not unqualified"
                               % ("{:,}".format(v), "{:,}".format(lo)))
            elif v > hi:
                drivers.append("~%s orders/yr is above the %s ceiling - likely solved already"
                               % ("{:,}".format(v), "{:,}".format(hi)))
            else:
                drivers.append("~%s orders/yr sits inside the serviceable band"
                               % "{:,}".format(v))

    # 3. Throughput momentum - who is accelerating into the ceiling.
    t = triggers.get("throughput_momentum")
    if t:
        possible += t["weight"]
        now = shop.get("reviews_last_90d")
        prior = shop.get("reviews_prior_90d")
        if now is None or prior is None or (now + prior) < 6:
            missing.append("too little review history to read momentum")
        elif prior == 0:
            evaluated += 1
            score += t["weight"] * 0.8
            drivers.append(
                "%d reviews in the last 90d against none in the 90d before - either new or "
                "newly busy; capture more history to tell which" % now)
        else:
            evaluated += 1
            ratio = float(now) / prior
            span = (t["fires_at"] - 0.8) + 0.6
            score += t["weight"] * min(1.0, max(0.0, (ratio - 0.8) / span))
            if ratio >= t["fires_at"]:
                drivers.append(
                    "order rate up %.1fx (%d -> %d reviews/90d) - scaling into a "
                    "single-workshop ceiling" % (ratio, prior, now))
            elif ratio < 0.85:
                drivers.append("order rate down %.1fx (%d -> %d reviews/90d) - cooling"
                               % (ratio, prior, now))

    # 4. Cross-border origin.
    t = triggers.get("cross_border_origin")
    if t:
        possible += t["weight"]
        cc = shop.get("ships_from")
        if not cc:
            missing.append("origin country unknown")
        else:
            evaluated += 1
            if cc not in ("US", "GB"):
                score += t["weight"]
                drivers.append(
                    "prints in %s; most Etsy demand sits in the US/UK, so the majority of "
                    "orders cross a border" % cc)

    # 5. Complaint keywords. Confirms a prospect, never finds one: base rate ~0.2%.
    t = triggers.get("complaint_keywords")
    if t:
        possible += t["weight"]
        sigs, quotes, available = keyword_hits(shop["shop"], snap_dir)
        if not available:
            missing.append("no review corpus captured for this prospect")
        else:
            evaluated += 1
            if sigs:
                score += t["weight"] * min(1.0, len(sigs) / 2.0)
                drivers.append("buyers named it in writing: " + ", ".join(sigs))

    ripeness = int(round(score / possible * 100)) if possible else 0
    # Confidence is how much of the rubric we could actually evaluate, not how
    # sure we are of the answer. Say which, so nobody reads it as certainty.
    total_triggers = len(triggers) or 1
    confidence = int(round(evaluated * 100.0 / total_triggers))
    return {
        "shop": shop,
        "ripeness": ripeness,
        "drivers": drivers,
        "missing": missing,
        "confidence": confidence,
        "quotes": quotes,
    }


def band_name(r, bands):
    if r >= bands["ripe"]:
        return "RIPE"
    if r >= bands["ripening"]:
        return "RIPENING"
    if r >= bands["watch"]:
        return "WATCH"
    return "COLD"


def render(rows, profile, watchlist, out_path):
    bands = profile["ripeness_bands"]
    today = datetime.date.today().isoformat()
    src = watchlist.get("generated_from", "fallback/snapshot/*.json")
    L = []
    L.append("# Outreach radar")
    L.append("")
    L.append("**Run:** %s  ·  **Cadence:** every %d days  ·  **Prospects swept:** %d"
             % (today, profile["cadence_days"], len(rows)))
    L.append("")
    L.append("**Data mode:** cached snapshot, no credentials used. Per-shop source URL and "
             "retrieval date in `%s`." % src)
    L.append("")
    L.append("Ripeness is a likelihood, not a verdict. It answers *how close is this "
             "prospect to the moment their fulfilment stops working* - and every point of it "
             "traces to a driver listed below. Confidence is the share of triggers that could "
             "be evaluated at all, not how sure the answer is.")
    L.append("")
    L.append("| Prospect | Ripeness | Band | Conf. | Leading driver |")
    L.append("|---|---:|---|---:|---|")
    for r in rows:
        lead = r["drivers"][0] if r["drivers"] else "no trigger fired"
        L.append("| [%s](%s) | %d%% | %s | %d%% | %s |"
                 % (r["shop"]["shop"], r["shop"].get("shop_url", ""), r["ripeness"],
                    band_name(r["ripeness"], bands), r["confidence"], lead[:90]))
    L.append("")

    hot = [r for r in rows if r["ripeness"] >= bands["ripening"]]
    L.append("## Why these %d are interesting *now*" % len(hot))
    L.append("")
    if not hot:
        L.append("Nothing crossed the ripening threshold this run. That is a valid result: "
                 "the list is not ripe, and inventing a reason to call wastes the week.")
        L.append("")
    for r in hot:
        s = r["shop"]
        L.append("### %s — %d%% · %s" % (s["shop"], r["ripeness"], band_name(r["ripeness"], bands)))
        L.append("")
        for d in r["drivers"]:
            L.append("- " + d)
        L.append("")
        if r["quotes"]:
            L.append("Buyer evidence:")
            L.append("")
            for q in r["quotes"]:
                L.append("> \"%s\" — %s · [source](%s)" % (q["text"], q["date"], q["url"]))
            L.append("")
        else:
            L.append("*No buyer complaint quotes in the captured window.* This prospect "
                     "qualifies on published numbers alone - open with the numbers, never "
                     "with a review that does not exist.")
            L.append("")
        if r["missing"]:
            L.append("*Not assessed:* %s." % "; ".join(r["missing"]))
            L.append("")

    cold = [r for r in rows if r["ripeness"] < bands["ripening"]]
    L.append("## Not ripe this run (%d)" % len(cold))
    L.append("")
    for r in cold:
        reason = r["drivers"][0] if r["drivers"] else "no trigger fired"
        L.append("- **%s** — %d%%. %s" % (r["shop"]["shop"], r["ripeness"], reason))
    L.append("")

    L.append("## Limitations of this run")
    L.append("")
    L.append("- Ripeness reads *public* signals only. A shop can be in pain invisibly.")
    L.append("- Complaint text has a ~0.2% base rate, so it confirms a prospect rather than "
             "finding one. The ranking is carried by the ratings gap and by momentum.")
    L.append("- Momentum is measured inside a single capture. A per-shop review cap truncates "
             "busy shops, which reads here as *too little history*.")
    L.append("- Buyer geography is not public per shop, so cross-border scoring leans on the "
             "general fact that Etsy demand concentrates in the US and UK.")
    L.append("- Nothing here observes the prospect's costs, margin, or existing supplier. "
             "Ripeness is a reason to call, not a forecast that they will buy.")
    L.append("")

    L.append("## Close the loop")
    L.append("")
    L.append("Before the next run, tell the skill:")
    L.append("")
    L.append("1. Which of these did you contact, and which replied?")
    L.append("2. Where was a stated reason wrong - did anyone say their fulfilment is fine?")
    L.append("3. Who signed since the last run? Signed clients are the real ICP, and they "
             "retrain it.")
    L.append("")
    L.append("Answers are folded back into the profile: a trigger that keeps producing "
             "replies gains weight, one that keeps missing loses it.")
    out_path.write_text("\n".join(L) + "\n", encoding="utf-8")


def main():
    dprof, dwatch = default_pair()
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--profile", default=dprof,
                    help="Stage 1/2 profile. Default: state/profile.json if present, "
                         "else the shipped demo profile.")
    ap.add_argument("--watchlist", default=dwatch,
                    help="Prospects to sweep. Default: state/watchlist.json if present, "
                         "else the shipped demo watchlist.")
    ap.add_argument("--snapshots", default="fallback/snapshot",
                    help="Optional review corpus for the keyword trigger. Omit or point "
                         "at nothing for a metrics-only deployment.")
    ap.add_argument("--out", default="demo/output/radar.md")
    ap.add_argument("--limit", type=int, default=0, help="0 = all")
    a = ap.parse_args()

    profile = json.loads(resolve(a.profile).read_text(encoding="utf-8"))
    watchlist = json.loads(resolve(a.watchlist).read_text(encoding="utf-8"))
    shops = watchlist["shops"][:a.limit] if a.limit else watchlist["shops"]
    triggers = {t["id"]: t for t in profile.get("triggers", [])}

    snap_dir = resolve(a.snapshots) if a.snapshots else None
    if snap_dir is not None and not snap_dir.is_dir():
        snap_dir = None

    print("Stage 3 · periodic sweep · %d prospects · %d triggers · %s · "
          "no credentials used"
          % (len(shops), len(triggers),
             "review corpus present" if snap_dir else "metrics only, no review corpus"))

    rows = []
    for i, s in enumerate(shops, 1):
        rows.append(assess(s, triggers, snap_dir))
        progress(i, len(shops), "assessed")
    rows.sort(key=lambda r: -r["ripeness"])

    out = resolve(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    render(rows, profile, watchlist, out)

    b = profile["ripeness_bands"]
    print("\nWrote %s · %d ripe, %d ripening, %d not yet"
          % (a.out,
             sum(1 for r in rows if r["ripeness"] >= b["ripe"]),
             sum(1 for r in rows if b["ripening"] <= r["ripeness"] < b["ripe"]),
             sum(1 for r in rows if r["ripeness"] < b["ripening"])))


if __name__ == "__main__":
    main()
