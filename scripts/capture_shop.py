"""Capture Etsy shop-level facts and merge them into existing snapshots.

Adds what review text cannot give us: where the shop produces, Etsy's own
shipping rating, real sold volume, and any storefront the seller links to.

Seller identity (name, bio, avatar) is dropped. The lead is the shop.
"""
import argparse, json, os, pathlib, sys, urllib.request, urllib.error

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from env import load_env
load_env()

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "fallback" / "snapshot"
ACTOR = os.environ.get("APIFY_SHOP_ACTOR", "getdataforme~etsy-shop-details-scraper")
TOKEN = os.environ.get("APIFY_TOKEN", "")

# Business facts only. seller_name / seller_bio / seller_avatar_url are personal
# data about a named individual and are never stored.
KEEP = ("country_code", "city", "region", "shipping_rating", "item_quality_rating",
        "customer_service_rating", "average_rating", "total_rating_count",
        "rating_count_past_year", "sold_count", "active_listing_count",
        "create_date", "is_open", "shop_highlight", "accepts_custom_requests")
DROP = ("seller_name", "seller_bio", "seller_avatar_url", "icon_url", "banner_url")


def links(raw):
    out = []
    for l in (raw.get("related_links") or []):
        u = l if isinstance(l, str) else (l.get("url") or l.get("link") or "")
        if u and "etsy.com" not in u.lower():
            out.append(u)
    return out


def fetch(shops, chunk=10):
    if not TOKEN:
        sys.exit("APIFY_TOKEN not set")
    url = (f"https://api.apify.com/v2/acts/{ACTOR}/run-sync-get-dataset-items"
           f"?token={TOKEN}&timeout=300")
    items = []
    for i in range(0, len(shops), chunk):
        batch = shops[i:i + chunk]
        body = json.dumps({"ShopNames": batch, "item_limit": len(batch)}).encode()
        req = urllib.request.Request(url, data=body,
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=320) as r:
                got = json.load(r)
            items += got
            print(f"  .. {len(got)} shop records for {len(batch)} names")
        except urllib.error.HTTPError as e:
            print(f"  ! batch failed: HTTP {e.code} {e.read().decode()[:100]}")
    return items


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--shops", default="", help="comma-separated; default = every snapshot")
    ap.add_argument("--from-list", help="CSV with a 'shop' column - enrich the whole list")
    ap.add_argument("--chunk", type=int, default=10)
    a = ap.parse_args()
    if a.from_list:
        import csv
        with open(a.from_list, newline="", encoding="utf-8") as fh:
            shops = [r["shop"] for r in csv.DictReader(fh) if r.get("shop")]
    else:
        shops = ([s.strip() for s in a.shops.split(",") if s.strip()]
                 or sorted(p.stem for p in OUT.glob("*.json") if p.stem != "README"))
    if not shops:
        sys.exit("nothing to enrich")

    print(f"enriching {len(shops)} shops")
    by_name = {}
    for raw in fetch(shops, a.chunk):
        name = raw.get("shop_name")
        if name:
            by_name[name] = raw

    n, missing = 0, []
    for shop in shops:
        f = OUT / f"{shop}.json"
        raw = by_name.get(shop)
        if not raw:
            missing.append(shop)
            continue
        snap = (json.loads(f.read_text(encoding="utf-8")) if f.exists() else {
            "shop": shop,
            "shop_url": f"https://www.etsy.com/shop/{shop}",
            "source": f"https://www.etsy.com/shop/{shop}",
            "retrieved_at": __import__("datetime").date.today().isoformat(),
            "collection_note": "Shop-level facts only; no buyer reviews captured.",
            "reviews": [],
        })
        facts = {k: raw.get(k) for k in KEEP if raw.get(k) is not None}
        assert not any(d in facts for d in DROP), "seller identity leaked"
        snap["shop_facts"] = facts
        snap["related_links"] = links(raw)
        snap["ships_from"] = raw.get("country_code") or snap.get("ships_from")
        f.write_text(json.dumps(snap, indent=2), encoding="utf-8")
        n += 1
    print(f"{n} snapshots enriched, {len(missing)} shops returned no record")
    if missing:
        print("  no record: " + ", ".join(missing[:15]) + (" ..." if len(missing) > 15 else ""))


if __name__ == "__main__":
    main()
