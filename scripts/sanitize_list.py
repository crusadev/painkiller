"""Derive a publishable shop list from the internal prospect sheet.

Drops every internal / personal column: owner names, contact status, outreach
channel, comments, and email addresses. Keeps only public shop identity plus
the two sizing estimates the rubric needs.
"""
import csv, re, sys, pathlib

SRC = pathlib.Path(sys.argv[1])
OUT = pathlib.Path(sys.argv[2])

SHOP_RE = re.compile(r"etsy\.com/shop/([A-Za-z0-9_-]+)")
EMAIL_RE = re.compile(r"[^@\s]+@[^@\s]+\.[A-Za-z]{2,}")

WANT = {
    "category": ("category",),
    "sales": ("sales if available",),
    "years": ("years if available",),
    "ratio": ("ratio per year", "sales on year"),
}


def norm(s):
    return s.strip().lower()


def build_map(header):
    m = {}
    for key, names in WANT.items():
        for i, cell in enumerate(header):
            if norm(cell) in names:
                m[key] = i
                break
    return m


def num(v):
    v = (v or "").strip().replace(",", ".")
    try:
        return float(v)
    except ValueError:
        return None


def main():
    rows, seen, colmap = [], set(), {}
    with SRC.open(newline="", encoding="utf-8") as fh:
        for raw in csv.reader(fh):
            joined = ",".join(raw)
            if "years if available" in joined:
                colmap = build_map(raw)
                continue
            m = SHOP_RE.search(joined)
            if not m:
                continue
            shop = m.group(1)
            if shop in seen:
                continue
            seen.add(shop)

            def cell(key):
                i = colmap.get(key)
                return raw[i] if i is not None and i < len(raw) else ""

            category = EMAIL_RE.sub("", cell("category")).strip().strip('"')
            sales, years = num(cell("sales")), num(cell("years"))
            ratio = num(cell("ratio"))
            if ratio is None and sales and years:
                ratio = round(sales * 1000 / years)
            rows.append({
                "shop": shop,
                "shop_url": f"https://www.etsy.com/shop/{shop}",
                "category": category,
                "est_annual_sales_k": sales if sales is not None else "",
                "years_active": years if years is not None else "",
                "ratio_per_year": int(ratio) if ratio else "",
            })

    with OUT.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)

    blob = OUT.read_text(encoding="utf-8")
    assert not EMAIL_RE.search(blob), "email leaked into sanitized output"
    print(f"wrote {len(rows)} shops -> {OUT}")


main()
