"""Capture Etsy shop review snapshots via Apify, stripping reviewer identity.

Two modes:
  live      python3 scripts/capture.py --shops DeltaLoom,Olee3DArt
  normalise python3 scripts/capture.py --from-json raw.json --shop DeltaLoom

Identity is dropped here, at ingest, so it can never reach disk. Only these
fields survive: rating, date, text, listing url. Reviewer names, handles,
profile links and avatars are discarded and never written.
"""
import argparse, datetime as dt, json, os, pathlib, re, sys, urllib.request

load_env()

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "fallback" / "snapshot"
ACTOR = os.environ.get("APIFY_ETSY_ACTOR", "")
TOKEN = os.environ.get("APIFY_TOKEN", "")

KEEP = ("rating", "date", "text", "url")
IDENTITY = re.compile(
    r"author|buyer|reviewer|user|profile|avatar|display_?name|member|customer", re.I)
EMAIL = re.compile(r"[^@\s]+@[^@\s]+\.[A-Za-z]{2,}")


def pick(d, *names):
    for n in names:
        for k, v in d.items():
            if k.lower().replace("_", "") == n and v not in (None, ""):
                return v
    return None


def normalise_review(raw):
    """Whitelist four fields. Anything identity-shaped is dropped, not renamed."""
    text = pick(raw, "text", "review", "reviewtext", "body", "comment") or ""
    out = {
        "rating": pick(raw, "rating", "stars", "score"),
        "date": str(pick(raw, "date", "reviewdate", "createdat", "published") or "")[:10],
        "text": EMAIL.sub("[email removed]", str(text)).strip(),
        "url": pick(raw, "url", "listingurl", "producturl", "link"),
    }
    return {k: v for k, v in out.items() if k in KEEP}


def assert_clean(snap):
    for r in snap["reviews"]:
        bad = [k for k in r if IDENTITY.search(k)]
        assert not bad, f"identity field survived: {bad}"
        assert not EMAIL.search(r.get("text", "")), "email survived in review text"


def build(shop, items, source, ships_from=None, market=None, processing=None):
    snap = {
        "shop": shop,
        "shop_url": f"https://www.etsy.com/shop/{shop}",
        "source": source,
        "retrieved_at": dt.date.today().isoformat(),
        "collection_note": "Public buyer reviews. Reviewer identity not collected.",
        "ships_from": ships_from,
        "primary_buyer_market": market,
        "stated_processing_days": processing,
        "reviews": [r for r in (normalise_review(i) for i in items) if r["text"]],
    }
    assert_clean(snap)
    return snap


def run_actor(shop):
    if not (TOKEN and ACTOR):
        sys.exit("set APIFY_TOKEN and APIFY_ETSY_ACTOR to capture live")
    url = (f"https://api.apify.com/v2/acts/{ACTOR}/run-sync-get-dataset-items"
           f"?token={TOKEN}&timeout=60")
    body = json.dumps({"shopUrl": f"https://www.etsy.com/shop/{shop}/reviews",
                       "maxItems": 100}).encode()
    req = urllib.request.Request(url, data=body,
                                 headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=70) as resp:
        return json.load(resp)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shops", default="")
    ap.add_argument("--from-json")
    ap.add_argument("--shop")
    ap.add_argument("--ships-from")
    ap.add_argument("--market")
    ap.add_argument("--processing-days", type=int)
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)

    if a.from_json:
        items = json.loads(pathlib.Path(a.from_json).read_text(encoding="utf-8"))
        items = items if isinstance(items, list) else items.get("items", [])
        snap = build(a.shop, items, f"apify dataset {pathlib.Path(a.from_json).name}",
                     a.ships_from, a.market, a.processing_days)
        (OUT / f"{a.shop}.json").write_text(json.dumps(snap, indent=2), encoding="utf-8")
        print(f"{a.shop}: {len(snap['reviews'])} reviews -> {OUT / (a.shop + '.json')}")
        return

    for shop in [s.strip() for s in a.shops.split(",") if s.strip()]:
        snap = build(shop, run_actor(shop),
                     f"https://www.etsy.com/shop/{shop}/reviews",
                     a.ships_from, a.market, a.processing_days)
        (OUT / f"{shop}.json").write_text(json.dumps(snap, indent=2), encoding="utf-8")
        print(f"{shop}: {len(snap['reviews'])} reviews captured")


if __name__ == "__main__":
    main()
