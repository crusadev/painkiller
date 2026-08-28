# Input provenance

## `shops.csv`

- **What:** 411 Etsy shops selling 3D-printed products (lamps, board-game
  accessories and inserts, console/handheld holders and organisers, displays).
- **Source:** internal prospect list, manually compiled by the 3DAPI team from
  public Etsy category browsing.
- **Retrieved:** 2026-08-28.
- **Fields:** `shop`, `shop_url`, `website`, `category` — public identity only.

## What was removed before publishing

The internal sheet also carried outreach state and contact details. None of it
is in this repository, and the source sheet is gitignored (`input/`). Removed:

- Team member names and outreach ownership
- Contacted / channel / date-contacted columns
- Free-text internal comments
- Seller contact email addresses
- **Revenue and tenure estimates.** The internal sheet carries the team's own
  estimates of these third-party businesses' annual sales. That is internal
  commercial judgement about other companies and is deliberately not
  published. Volume scoring instead uses Etsy's own `sold_count` over shop
  age, retrieved per shop — a real figure rather than an estimate.

`scripts/sanitize_list.py` performs the reduction and asserts no email address
survives into the published file.

## Review evidence

Captured from public Etsy shop review pages via Apify. Each snapshot in
`fallback/snapshot/` records its `source` URL and `retrieved_at` date.
Reviewer identity is discarded at ingest — see `scripts/capture.py`.
