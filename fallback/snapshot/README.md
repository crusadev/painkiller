# Fallback snapshot

Committed public review evidence, used when the skill runs without an
`APIFY_TOKEN` — which is the case on the judging machine.

One file per shop, named `<shop>.json`:

```json
{
  "shop": "...", "shop_url": "...", "source": "...", "retrieved_at": "YYYY-MM-DD",
  "ships_from": "DE", "primary_buyer_market": "US", "stated_processing_days": 7,
  "reviews": [{"rating": 2, "date": "2026-08-20", "text": "...", "url": "..."}]
}
```

Reviews carry four fields only. No reviewer name, handle, profile URL or avatar
is ever collected — `scripts/capture.py` drops them at ingest and
`tests/test_scoring.py` asserts it.

Everything here is real captured data. Synthetic data lives in
`tests/fixtures/`, is prefixed `SYNTHETIC_`, is used only by unit tests, and is
never rendered into `leads.md`. A test asserts no synthetic record reaches this
directory.
