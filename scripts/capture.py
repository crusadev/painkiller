"""Capture Etsy shop review snapshots via Apify, stripping reviewer identity.

Two modes:
  live      python3 scripts/capture.py --shops DeltaLoom,Olee3DArt
  normalise python3 scripts/capture.py --from-json raw.json --shop DeltaLoom

Identity is dropped here, at ingest, so it can never reach disk. Only these
fields survive: rating, date, text, listing url. Reviewer names, handles,
profile links and avatars are discarded and never written.
"""
import argparse, datetime as dt, html, json, os, pathlib, re, sys, urllib.request, urllib.error

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from env import load_env

load_env()

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "fallback" / "snapshot"
ACTOR = os.environ.get("APIFY_ETSY_ACTOR", "hello.datawizards~etsy-reviews")
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
    """Whitelist four fields. Anything identity-shaped is dropped, not renamed.

    The upstream actor returns buyer real name, login, numeric id and avatar
    URL. None of it is needed to score a shop, so none of it survives this
    function and none of it is ever written to disk.
    """
    details = raw.get("product_details") or {}
    text = pick(raw, "review", "text", "reviewtext", "body", "comment") or ""
    return {
        "rating": pick(raw, "productrating", "rating", "stars", "score"),
        "date": str(pick(raw, "date", "reviewdate", "createdat", "published") or "")[:10],
        "text": EMAIL.sub("[email removed]", html.unescape(str(text))).strip(),
        "url": details.get("product_url") or pick(raw, "url", "listingurl", "link"),
    }


def shop_of(raw):
    return ((raw.get("product_details") or {}).get("seller_name")
            or pick(raw, "shopname", "shop", "sellername"))


def assert_clean(snap):
    for r in snap["reviews"]:
        bad = [k for k in r if IDENTITY.search(k)]
        assert not bad, f"identity field survived: {bad}"
        assert not EMAIL.search(r.get("text", "")), "email survived in review text"


def build(shop, items, source, ships_from=None, market=None, processing=None):
    # Preserve anything capture_shop.py already wrote. Overwriting the file
    # wholesale silently destroys shop_facts and related_links.
    prior = {}
    f = OUT / f"{shop}.json"
    if f.exists():
        prior = json.loads(f.read_text(encoding="utf-8"))
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
    for k in ("shop_facts", "related_links"):
        if prior.get(k) is not None:
            snap[k] = prior[k]
    if not snap.get("ships_from") and prior.get("ships_from"):
        snap["ships_from"] = prior["ships_from"]
    assert_clean(snap)
    return snap


def run_actor(shops, item_limit, chunk=5):
    """One run per chunk of shops; the actor rejects very large batches."""
    if not (TOKEN and ACTOR):
        sys.exit("set APIFY_TOKEN (and optionally APIFY_ETSY_ACTOR) to capture live")
    url = (f"https://api.apify.com/v2/acts/{ACTOR}/run-sync-get-dataset-items"
           f"?token={TOKEN}&timeout=600")
    items = []
    for i in range(0, len(shops), chunk):
        batch = shops[i:i + chunk]
        body = json.dumps({"shop_name": batch, "itemLimit": item_limit}).encode()
        req = urllib.request.Request(url, data=body,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=900) as resp:
                got = json.load(resp)
        except urllib.error.HTTPError:
            # A single unknown shop fails the whole run - retry the batch
            # one shop at a time so its neighbours still get captured.
            print(f"  ! batch of {len(batch)} failed, retrying individually")
            got = []
            for one in batch:
                body1 = json.dumps({"shop_name": [one], "itemLimit": item_limit}).encode()
                r1 = urllib.request.Request(url, data=body1,
                                            headers={"Content-Type": "application/json"})
                try:
                    with urllib.request.urlopen(r1, timeout=900) as resp:
                        got += json.load(resp)
                except urllib.error.HTTPError:
                    print(f"     ! {one}: no data")
        items += got
        print(f"  .. {len(got)} items for {', '.join(batch)}")
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shops", default="", help="comma-separated shop names")
    ap.add_argument("--shops-file", help="file with one shop name per line")
    ap.add_argument("--item-limit", type=int, default=60, help="reviews per shop")
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
        snap = build(a.shop, items, f"https://www.etsy.com/shop/{a.shop}/reviews",
                     a.ships_from, a.market, a.processing_days)
        (OUT / f"{a.shop}.json").write_text(json.dumps(snap, indent=2), encoding="utf-8")
        print(f"{a.shop}: {len(snap['reviews'])} reviews")
        return

    shops = [s.strip() for s in a.shops.split(",") if s.strip()]
    if a.shops_file:
        shops += [l.strip() for l in pathlib.Path(a.shops_file).read_text().splitlines() if l.strip()]
    if not shops:
        sys.exit("nothing to capture: pass --shops or --shops-file")

    items = run_actor(shops, a.item_limit)
    grouped = {}
    for it in items:
        name = shop_of(it)
        if name:
            grouped.setdefault(name, []).append(it)

    total = 0
    for shop in shops:
        got = grouped.get(shop, [])
        if not got:
            print(f"  {shop}: no reviews returned - skipped")
            continue
        snap = build(shop, got, f"https://www.etsy.com/shop/{shop}/reviews",
                     a.ships_from, a.market, a.processing_days)
        (OUT / f"{shop}.json").write_text(json.dumps(snap, indent=2), encoding="utf-8")
        total += len(snap["reviews"])
        print(f"  {shop}: {len(snap['reviews'])} reviews")
    print(f"{total} reviews across {len(list(OUT.glob('*.json'))) - 1} shops -> {OUT}")


if __name__ == "__main__":
    main()
