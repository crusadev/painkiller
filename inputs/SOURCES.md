# Input provenance

## `shops.csv`

- **What:** 411 Etsy shops selling 3D-printed products (lamps, board-game
  accessories and inserts, console/handheld holders and organisers, displays).
- **Source:** internal prospect list, manually compiled by the 3DAPI team from
  public Etsy category browsing.
- **Retrieved:** 2026-08-28.
- **Fields:** `shop`, `shop_url`, `category`, `est_annual_sales_k`,
  `years_active`, `ratio_per_year`.
  `est_annual_sales_k` and `years_active` are the team's own estimates from
  public shop pages, not Etsy-published figures. `ratio_per_year` is derived.

## What was removed before publishing

The internal sheet also carried outreach state and contact details. None of it
is in this repository, and the source sheet is gitignored (`input/`). Removed:

- Team member names and outreach ownership
- Contacted / channel / date-contacted columns
- Free-text internal comments
- Seller contact email addresses

`scripts/sanitize_list.py` performs the reduction and asserts no email address
survives into the published file.

## Review evidence

Captured from public Etsy shop review pages via Apify. Each snapshot in
`fallback/snapshot/` records its `source` URL and `retrieved_at` date.
Reviewer identity is discarded at ingest — see `scripts/capture.py`.
