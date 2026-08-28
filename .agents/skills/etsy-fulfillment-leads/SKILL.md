---
name: etsy-fulfillment-leads
description: Qualify Etsy 3D-printing shops as leads for a distributed manufacturing network by finding public buyer reviews that describe fulfilment pain — slow cross-border delivery, customs charges, transit damage, capacity limits, blocked countries, inconsistent print quality — and mapping each to the thing that fixes it.
---

# Etsy fulfilment-pain lead qualifier

## What this does

Takes a list of Etsy shops selling 3D-printed products and returns a **ranked,
evidence-backed lead list**: which shops are visibly hitting the limits of
printing everything in one place, what specifically is breaking, and the quoted
buyer review that proves it.

## Why these signals qualify a lead

Every complaint in the taxonomy below is a symptom of **one** root cause: the
product was printed far away from the person who bought it, by a single
workshop. That is exactly what a distributed print network removes — the order
is routed to a farm near the customer, produced locally, and shipped
domestically.

So the skill is not doing sentiment analysis. It is looking for the specific
failure modes that a routing layer makes impossible, which is what turns a
public complaint into a qualified, timed sales conversation.

## When to use it

- Building an outbound list from a set of candidate shops
- Deciding which of a long prospect list to contact **this week** rather than eventually
- Writing an opener that leads with the prospect's own problem instead of a pitch

Do not use it to evaluate individual buyers, or any person. The unit of
analysis is the shop.

## Inputs

| Path | What it is |
|---|---|
| `inputs/shops.csv` | Candidate shops: `shop`, `shop_url`, `website`, `category` |
| `fallback/snapshot/<shop>.json` | Captured public review evidence, shop facts and linked storefronts per shop |

Volume is not taken from the input list. `scripts/capture_shop.py` retrieves
Etsy's own `sold_count` per shop, divided by shop age, so the serviceability
band is checked against a real figure rather than an estimate.

## Pain taxonomy

| Signal | What it means | What fixes it |
|---|---|---|
| **Cannot buy from that country** | Shipping footprint excludes demand that already exists | Production inside the buyer's market — the shop sells globally without posting globally |
| **Customs / import fees** | The order crossed a border | Local production, no customs event |
| **Slow delivery** | Long transit from a single origin | Route to the nearest print farm |
| **Damaged in transit** | Long shipping leg, more handling | Short domestic leg, fewer handoffs |
| **Long make time** | Made-to-order backlog on one printer | On-demand network capacity absorbs spikes |
| **Capacity ceiling** | Demand exceeds what the seller can physically print | Network capacity instead of one workshop |
| **Shipping cost** | Distance priced into every order | Local fulfilment collapses the shipping leg |
| **Inconsistent print quality** | Output varies between runs on one workshop's machines | Every order passes the QC pipeline and ships as the seller specified |

"Cannot buy from that country" carries 1.5× weight: it is demand the seller has
already generated and cannot capture, so the cost of the problem is visible and
the fix is immediate.

## Rubric (0–100)

| Component | Max | Question |
|---|---|---|
| **Fulfilment deficit** | 25 | Does Etsy rate the shop's *shipping* below its *item quality*, and how low is shipping in absolute terms |
| Pain match | 20 | Which failure modes appear in buyer review text, weighted by severity |
| Volume fit | 20 | Are real orders/year (from `sold_count` ÷ shop age) inside the serviceable band |
| Throughput | 15 | How fast the shop is shipping — review velocity as an order-rate proxy |
| Cross-border exposure | 10 | Does the shop produce outside the US/UK, where most Etsy demand sits |
| Corroboration | 10 | Independent confirmations: multiple reviews, rating deficit, make time, foreign origin |
| Recency | 5 | Is the complaint evidence live rather than historical |

**hot** ≥ 60 · **watch** ≥ 35 · **nurture** · **pass** < 35

### Why the fulfilment deficit leads

Etsy publishes `shipping_rating` and `item_quality_rating` as separate numbers.
When shipping sits below item quality, buyers are saying the product is fine
and the *delivery* is not — which is precisely the axis a routing layer moves,
and it is the seller's own customers saying it.

Crucially this signal exists for **every** shop, where complaint text exists for
almost none (0.2% of the captured corpus). It is what lets the skill rank
honestly instead of returning an empty list.

A shop qualifying on ratings alone is rendered as such: the evidence block says
"no buyer complaint quotes in the captured window" and shows the numbers
instead, and the drafted opener leads with the rating gap rather than claiming
reviews say something they do not.

### The `nurture` tier

A shop below the serviceable floor (`ratio_per_year` < 1000) is not a
rejection — it is a lead we are **early for**. Dropping those is how a
prospect that was "too small" quietly becomes someone else's customer.

So a small shop whose review rate is *rising* is tiered `nurture` rather than
`pass`, and the report gives its gap to the floor, its quarter-on-quarter
growth, an estimated crossing time, and a recheck cadence (30 days if growing,
90 otherwise). A small shop whose rate is *declining* stays `pass` — that is a
lead we are late for, not early.

Growth is measured inside a single capture: review rate in the last 90 days
against the 90 before it. It reads `unknown` when the snapshot does not span
both windows, which is what happens when a per-shop review cap truncates a busy
shop's history. Capture more history for those shops rather than assuming.

### Star ratings are not used

Nothing in the rubric reads the star rating. Buyers routinely bury a real
fulfilment complaint inside praise — "took three weeks but the seller was
great", "worth the wait" — and on the captured corpus **every fulfilment signal
found sits in a five-star review**. Filtering by rating would have discarded
all of them.

Matching therefore runs per *clause*, splitting on contrastive connectives
(but, however, although), so praise in one clause cannot cancel a complaint in
the next. A negation guard still suppresses the genuine non-events — "no
customs fees", "arrived quickly".

### Why throughput carries weight

Complaints are the sharpest evidence but they are *rare*: across the 1,283
reviews captured for this repo, 96.5% are five-star and only 0.2% describe a
fulfilment failure. Etsy buyers who wait three weeks often still leave five
stars. Ranking on complaints alone would therefore reject almost every shop,
including ones visibly at the constraint.

Review velocity is the counterweight. It is the only public proxy for order
volume, and on this corpus it spreads from 0.3 to 26 reviews/week — two orders
of magnitude. A shop clearing 20 orders a week out of one workshop is scaling
into the constraint whether or not anyone has complained yet; a shop clearing
one is not, whatever its reviews say.

So: **throughput finds who isapproaching the ceiling, complaints prove they have hit
it.** A shop with both is the strongest possible lead.

A single angry review never qualifies a shop. Corroboration across independent
evidence types is what separates a lead from noise. The skill must be willing
to return `pass`, and must say why — `leads.md` always renders the rejected
shops with their reasons.

## Privacy rules — non-negotiable

The lead is the **shop**. The people writing the reviews are its customers and
are irrelevant to the score.

- Reviewer identity is discarded at ingest in `scripts/capture.py`, before
  anything is written to disk. Only `rating`, `date`, `text`, `url` survive.
- Never collect or store reviewer names, handles, profile URLs or avatars.
- Emails found in review text are redacted.
- Only complaints about the **business** count. Anything naming an individual
  is out of scope.
- `tests/test_scoring.py` asserts these properties.

## How to run

```bash
# 1. Capture buyer reviews
python3 scripts/capture.py --shops DeltaLoom,Olee3DArt

# 2. Enrich with shop facts: origin country, Etsy shipping vs quality
#    ratings, real sold volume, and any linked storefront
python3 scripts/capture_shop.py

# 3. Score and render
python3 scripts/qualify.py --limit 3
```

Seller identity (name, bio, avatar) is dropped in step 2, exactly as reviewer
identity is dropped in step 1.

Output: `leads.md` — ranked table, a card per top lead with quoted evidence
(URL + retrieval date) and a drafted opener, then every rejection with its reason.

## Degraded operation

**The skill runs with no credentials.** With no `APIFY_TOKEN`, it scores the
committed snapshot in `fallback/snapshot/` instead of fetching, prints
`cached snapshot (no APIFY_TOKEN)`, and states the data mode and retrieval date
at the top of `leads.md`. Nothing is fabricated to fill the gap: if evidence is
missing, the shop scores low and says so.

`--limit` defaults to 3 so a run finishes inside the 75-second judging gate.

## Known limits

- **Volume is a lifetime average, not a current rate.** `orders/year` is Etsy's
  `sold_count` divided by shop age, so it reports what a shop has averaged since
  opening, not what it is doing now. Etsy's `rating_count_past_year` field would
  fix this but is a verbatim duplicate of the lifetime total on all 376 shops
  captured — it is not usable. Where review capture exists, current rate can be
  estimated as `review velocity x 52 x (sold_count / total_rating_count)`; on
  the 22 shops measured that way the median shop runs at **0.7x** its lifetime
  average, i.e. most are past peak. Treat the volume band as approximate, and
  prefer the current-rate estimate wherever reviews have been captured.

- **Complaint base rate is very low.** See above. The taxonomy fires correctly
  when pain is present; it is the corpus that is quiet, not the matcher.
- **`geo_blocked` is near-undetectable in review data.** A buyer who cannot
  order never becomes a reviewer. The signal is retained because it fires on
  shop Q&A and message data, which this capture does not yet reach.
- **`primary_buyer_market` is still unset.** `ships_from` now comes from the
  shop-details actor, but per-shop buyer geography is not public. Cross-border
  scoring therefore relies on the general fact that Etsy demand is
  concentrated in the US and UK, which is stated wherever it is used.
- Matching is lexical. It will miss complaints phrased unusually and in
  languages other than English.

## Reuse

Swap `inputs/shops.csv` for any shop list. To retarget a different business,
edit the taxonomy in `scripts/taxonomy.py`: each entry is `patterns` (what the
customer says) → `means` (what it implies) → `fix` (what you sell). The rubric
and renderer are unchanged.
