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

Reads `fallback/snapshot/*.json`, writes `demo/output/leads.md`. Takes ~0.1s. `--limit 3`
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
| Shops in list | 411 (`demo/input/shops.csv`) |
| Shops enriched with shop facts | 376 (35 returned no record — closed or renamed) |
| Shops with full review capture | 61 |
| Reviews captured | 3,623 |
| Linked storefronts discovered | 195 |
| Ranking | 17 hot · 64 watch · 83 pass · 212 nurture |
| Top lead | QuantumQuill3D — shipping 4.52 vs quality 4.72, prints in CA, four buyers describe slow shipping in 4-5 star reviews |
| Submission | filed from commit `2c443cb`, repo `crusadev/painkiller` |

## Layout

| Path | |
|---|---|
| `.agents/skills/etsy-fulfillment-leads/SKILL.md` | The skill: taxonomy, rubric, privacy rules, known limits |
| `submission.json` | Manifest, schema v2 |
| `demo/` | The judged artifacts: seed prompt, input, output, evals |
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

**hot** ≥60 · **watch** ≥35 · **pass** <35. The volume floor (1200 orders/yr)
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

2. **The complaint base rate is ~1.2%.** The overwhelming majority of reviews
   are five-star, and Etsy buyers who wait a month still leave five stars.
   Ranking on complaint text alone returns almost nothing, which is why the
   rubric leans on shop-level facts.

3. **Star ratings are deliberately unused.** All 44 fulfilment signals in the
   corpus sit in **four- and five-star** reviews (31 at five stars). Filtering
   by rating finds zero. Complaints are buried inside praise: "took about two
   months to arrive" sits in a 5-star review recommending the shop.

4. **Matching is per clause, not per sentence.** Buyers bury complaints in
   praise: "took three weeks but the seller was great". Splitting on
   but/however/although keeps the praise from cancelling the complaint.

5. **The review actor fails a whole batch if one shop name is bad.**
   `capture.py` retries failed batches shop-by-shop. Don't remove that.

5b. **`capture.py` merges into the existing snapshot.** It used to overwrite,
   which silently destroyed the `shop_facts` and `related_links` that
   `capture_shop.py` had written. Keep the merge.

5c. **The evals write to a scratch path.** `qualify.py`'s default output is the
   committed `demo/output/leads.md`; an earlier version of the eval runner clobbered it
   with a 3-shop report. There is now a regression check for this.

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

## Submission structure

The repo follows the official starter layout, which is **not** what this repo
originally used — the artifacts live under `demo/` with exact names the
validator checks. Before any resubmission:

```bash
node .agents/skills/skillathon-submit/scripts/validate.mjs .   # must print OK
```

That script is the organizer's own validator, vendored from the starter repo
along with the two organizer skills. The submission system runs this exact
script against the submitted commit.
It enforces things that are easy to break by accident: `SKILL.md` frontmatter
may contain **only** `name` and `description`; the folder name must equal the
frontmatter `name`; the seed prompt must invoke the entry skill as
`$etsy-fulfillment-leads` **and** name the input path; `demo/evals.md` must
contain the literal labels `Intended`, `Insufficient evidence` and `Failure`
plus at least three `| pass |` or `| fail |` cells; and no file may contain the
word TODO in a placeholder position.

## Open work, highest value first

1. **Volume is a lifetime average — fix this before trusting the tiers.**
   `orders/year` is `sold_count` ÷ shop age, so it is what a shop has averaged
   since opening, not its current rate. Etsy's `rating_count_past_year` would
   solve it but is a duplicate of the lifetime total on all 376 shops — dead
   end. Where reviews exist, current rate ≈
   `velocity × 52 × (sold_count / total_rating_count)`. Measured that way on 22
   shops, the median runs at **0.7×** its lifetime average — most of this list
   is past peak, not scaling into the pain. Getting this right needs review
   capture per shop (~$0.30/shop at 60 reviews), which is the main cost driver
   for going wide.

   The floor is **1200 orders/yr**, set by the team after seeing that a
   500-orders/month floor left only 19 of 376 shops serviceable and zero
   scoring hot — the shops above that bar mostly have healthy shipping ratings,
   while the fulfilment deficits sit below it. Distribution of lifetime
   averages: p25 = 501, p50 = 1,014, p75 = 1,913, p90 = 3,673, max 21,445.

2. **Third review-capture pass.** Reviews now cover 61 of 376 shops — the top
   of the ranking. Extend down the `watch` tier as needed
   (`scripts/capture.py --shops-file`, ~$0.30/shop at 60 reviews).

3. **Multi-platform.** `related_links` found **195 linked storefronts** across
   the enriched shops (the sheet itself had 9). `myjeepduck.com/blogs/news` is a
   Shopify URL pattern — detect Shopify, then pull reviews from Judge.me / Loox
   endpoints. Trustpilot is keyed by domain and is the easy first one.
   Snapshots should grow a `platform` field per review before this lands.

4. **`primary_buyer_market` is unset** and not public per-shop. Cross-border
   scoring currently leans on "Etsy demand is concentrated in US/UK", stated
   wherever used. If you find a source, corroboration gets sharper.

5. **`geo_blocked` is near-undetectable in reviews** — a buyer who cannot order
   never becomes a reviewer. The signal is retained because it fires on shop
   Q&A and message data, which we do not capture. Highest-value signal we
   cannot yet see (1.5× weight).

6. **Re-sample the small end for *rising* shops.** The nurture tier has one
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
