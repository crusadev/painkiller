# Evaluations

Three cases, run against the submitted commit. Expectations were written before
running. Observed results are what the run actually produced.

| Case | Input | Expected behavior | Observed result | Pass / fail | Evidence |
| --- | --- | --- | --- | --- | --- |
| Intended | `demo/input/shops.csv` (411 shops, 376 with captured evidence) | Ranks every shop, tiers them, and gives each qualified lead quoted buyer evidence with a source URL and retrieval date | 376 scored in 0.2s: 17 hot, 64 watch, 83 pass, 212 nurture. Top lead QuantumQuill3D (CA, shipping 4.52 vs item quality 4.72) carries four dated buyer quotes, each linked to its listing | pass | `demo/output/leads.md` |
| Insufficient evidence | A shop with shop-level facts but no captured reviews, e.g. Creat3DLab | Must not manufacture a complaint. Says outright that no buyer quotes exist and qualifies on shop-level facts alone, with an opener that claims only what the data supports | Card renders *"No buyer complaint quotes in the captured window. This shop qualifies on shop-level evidence only"* and the drafted opener leads with the rating gap instead of asserting what reviews said | pass | `demo/output/leads.md`, `scripts/qualify.py` `opener()` |
| Failure / exclusion / safety | Run with `APIFY_TOKEN` unset; and any capture containing buyer or seller identity | With no credentials, score the committed snapshot, declare the data mode, and refuse rather than fabricate if no snapshot exists. Identity fields must never reach disk | Runs credential-free in 0.1s and stamps `committed snapshot, captured 2026-08-28 — no APIFY_TOKEN, cannot refresh` in the header; with the snapshot removed it exits non-zero with `no snapshots — run scripts/capture.py first`. Identity scan across 376 snapshots and 3,623 reviews: 0 violations | pass | `evals/run_evals.py`, `tests/test_scoring.py` |

Machine-checkable versions of all three run as 13 assertions:

```bash
python3 evals/run_evals.py     # exit 0
```

## Run context

- **Agent:** Claude Opus 5 via Claude Code, 2026-08-28
- **When:** 2026-08-28, Bucharest. Evidence captured the same day; every
  snapshot carries its own `retrieved_at`.
- **Baseline without the skill:** the same prospect list, unranked — 411 rows
  in a spreadsheet with no evidence attached and no basis for choosing who to
  contact first. The skill's own first cut was worse than useless: matching on
  complaint text alone found signals in 0.23% of reviews and produced zero
  qualified leads.

## What the cases were built to catch

The failure mode this skill is most exposed to is confident invention —
producing a plausible complaint for a shop that never had one. Case 2 exists
specifically to prove it abstains, because an earlier version did not: it drafted
an opener saying *"your reviews keep landing on the same thing"* for a shop with
no complaint quotes at all. That is now a rendering branch and a test.
