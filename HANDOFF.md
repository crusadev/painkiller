# Handoff

State of the `etsy-fulfillment-leads` skill as of 2026-08-28, for whoever picks
this up next. Written to be read cold.

## What this is

A skill that ranks Etsy shops selling 3D-printed products as leads for 3DAPI,
using public evidence that the shop is hitting the limits of printing
everything in one place.

The insight it runs on: **Etsy publishes `shipping_rating` separately from
`item_quality_rating`.** When shipping sits below quality, the seller's own
customers are saying the product is fine and the *delivery* is not — which is
the exact axis a distributed print network moves. That signal exists for every
shop, which is what makes the ranking possible at all (see "What we learned the
hard way").

## Run it

```bash
python3 scripts/qualify.py --limit 0     # no credentials needed
```

Reads `fallback/snapshot/*.json`, writes `leads.md`. Takes ~0.1s. `--limit 3`
is the default for the judging gate; `--limit 0` means all.

To capture fresh data you need your own Apify token:

```bash
cp .env.example .env      # then add APIFY_TOKEN
python3 scripts/capture.py --shops-file shops.txt --item-limit 60   # reviews
python3 scripts/capture_shop.py                                     # shop facts
python3 scripts/qualify.py --limit 0                                # score
```

`.env` is gitignored. Never commit a token.

## Verify before you push

```bash
python3 evals/run_evals.py                       # 12 checks, expects exit 0
python3 -c "import sys;sys.path.insert(0,'tests');import test_scoring as t;\
[getattr(t,n)() for n in dir(t) if n.startswith('test_')];print('ok')"
```

## Current state

| | |
|---|---|
| Shops in list | 411 (`inputs/shops.csv`) |
| Shops with captured evidence | 22 |
| Reviews captured | 1,283 |
| Ranking | 2 hot · 9 watch · 10 pass · 1 nurture |
| Top lead | Creat3DLab — shipping 4.64 vs quality 4.77, 27k sold, prints in HR |
| Submission | filed from commit `2c443cb`, repo `crusadev/painkiller` |

## Layout

| Path | |
|---|---|
| `.agents/skills/etsy-fulfillment-leads/SKILL.md` | The skill: taxonomy, rubric, privacy rules, known limits |
| `scripts/taxonomy.py` | 8 pain signals: `patterns` → `means` → `fix`. Edit this to retarget |
| `scripts/qualify.py` | Scoring + rendering. `score_shop()` is the rubric |
| `scripts/capture.py` | Review capture. Drops buyer identity at ingest |
| `scripts/capture_shop.py` | Shop facts: origin, ratings, sold count, linked storefronts. Drops seller identity |
| `scripts/sanitize_list.py` | Internal sheet → publishable list |
| `fallback/snapshot/` | Committed evidence, one file per shop |
| `evals/`, `tests/` | 12 eval checks, 6 unit tests |

## Rubric (100 points)

Fulfilment deficit 25 · Pain match 20 · Volume fit 20 · Throughput 15 ·
Cross-border 10 · Corroboration 10 · Recency 5.

**hot** ≥60 · **watch** ≥35 · **pass** <35. The volume floor (1000 orders/yr)
**overrides** the tier: below it a shop becomes `nurture` if steady or rising,
`pass` if declining. A shop below the floor cannot be served today, but
discarding it is how a "too small" prospect turns up later as someone else's
customer.

## What we learned the hard way

Read this before changing the matcher. These cost hours.

1. **`\bcustoms?\b` also matches "custom".** "Custom-made", "custom size",
   "custom set" are everywhere on Etsy. Every customs hit was a false positive
   until the pattern required a fee/border context. Bare `\bslow\b` matched
   *"I'm just slow with picking up the brush"*. **Any pattern you add, run it
   over the whole corpus and eyeball every hit** — see the snippet at the
   bottom.

2. **The complaint base rate is 0.2%.** 96.5% of reviews are five-star. Etsy
   buyers who wait three weeks still leave five stars. Ranking on complaint
   text alone returns an empty list. This is why the rubric leans on shop-level
   facts.

3. **Star ratings are deliberately unused.** All three fulfilment signals in
   the corpus sit in *five-star* reviews. Filtering by rating finds zero.

4. **Matching is per clause, not per sentence.** Buyers bury complaints in
   praise: "took three weeks but the seller was great". Splitting on
   but/however/although keeps the praise from cancelling the complaint.

5. **The review actor fails a whole batch if one shop name is bad.**
   `capture.py` retries failed batches shop-by-shop. Don't remove that.

6. **A lead qualifying on ratings alone must render as such.** Creat3DLab has
   no complaint quotes; its card says so explicitly and the opener leads with
   the numbers. Never draft an opener claiming reviews said something they did
   not — that is a judging gate, and it is also just wrong.

## Privacy rules — do not relax these

The lead is the **shop**. Everyone else is irrelevant to the score.

- Buyer identity (real name, login, user id, avatar) is dropped in
  `capture.py:normalise_review`. Reviews keep four fields: rating, date, text, url.
- Seller identity (name, bio, avatar) is dropped in `capture_shop.py` via `KEEP`.
- The internal prospect sheet — team names, outreach status, contact emails,
  and our revenue estimates of third-party businesses — is gitignored at
  `input/`. Only `scripts/sanitize_list.py` output gets published.
- `tests/test_scoring.py` asserts the review rules. Keep it passing.

## Open work, highest value first

1. **Enrich all 411 shops with shop facts.** ~$4, a few minutes.
   `python3 scripts/capture_shop.py --shops <comma-list>` — but note it
   currently only enriches shops that already have a review snapshot. To rank
   the full list you need to let it write a facts-only snapshot. The rubric
   scores 55/100 from shop facts alone, so no review capture is needed for a
   first-pass ranking. **This turns the deliverable from a 22-shop sample into
   the real 411-shop list.** Two-stage funnel: cheap wide pass, then capture
   reviews only for the top slice.

2. **Multi-platform.** The sheet had 9 usable storefront domains across 411
   rows; `related_links` from the shop actor found 8 across just 22 shops, so
   enriching all 411 should surface ~150. `myjeepduck.com/blogs/news` is a
   Shopify URL pattern — detect Shopify, then pull reviews from Judge.me / Loox
   endpoints. Trustpilot is keyed by domain and is the easy first one.
   Snapshots should grow a `platform` field per review before this lands.

3. **`primary_buyer_market` is unset** and not public per-shop. Cross-border
   scoring currently leans on "Etsy demand is concentrated in US/UK", stated
   wherever used. If you find a source, corroboration gets sharper.

4. **`geo_blocked` is near-undetectable in reviews** — a buyer who cannot order
   never becomes a reviewer. The signal is retained because it fires on shop
   Q&A and message data, which we do not capture. Highest-value signal we
   cannot yet see (1.5× weight).

5. **Re-sample the small end for *rising* shops.** The nurture tier has one
   occupant because the small shops were picked by lowest volume, which selects
   for dead shops rather than early ones.

## Actors used

| Actor | For | Cost |
|---|---|---|
| `hello.datawizards~etsy-reviews` | Buyer reviews. Input `shop_name[]`, `itemLimit`. Batches of ~5 | $0.005/review |
| `getdataforme~etsy-shop-details-scraper` | Shop facts + `related_links`. Input `ShopNames[]` | ~$0.01/shop |

Avoid `axlymxp~etsy-email-contact-extractor` and `memo23~etsy-scraper` — they
return seller emails we have no business collecting.

## Checking a new pattern against the corpus

```python
import json, pathlib, sys
sys.path.insert(0, "scripts")
from taxonomy import match_signals
for p in sorted(pathlib.Path("fallback/snapshot").glob("*.json")):
    d = json.loads(p.read_text())
    for r in d["reviews"]:
        if (s := match_signals(r["text"])):
            print(f"[{r.get('rating')}* {d['shop']} {sorted(s)}] {r['text'][:110]}")
```

Eyeball every line. If any of them is not a real fulfilment complaint, the
pattern is wrong.
