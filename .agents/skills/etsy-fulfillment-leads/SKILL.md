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
| `inputs/shops.csv` | Candidate shops: `shop`, `shop_url`, `category`, `est_annual_sales_k`, `years_active`, `ratio_per_year` |
| `fallback/snapshot/<shop>.json` | Captured public review evidence per shop |

`ratio_per_year` (annual sales ÷ years active) is the intent proxy: a shop
earning well in a short time is scaling *into* the pain right now.

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
| Pain match | 30 | How many distinct failure modes appear, weighted by severity |
| Recency | 15 | Is the pain live, or history — complaints in the last 90 days |
| Trend | 20 | Is the complaint *rate* rising as the shop scales |
| Volume fit | 20 | Is `ratio_per_year` in the serviceable band (1k–8k) |
| Corroboration | 15 | Independent confirmations: multiple reviews, stated make time ≥5d, international ships-from |

**hot** ≥ 60 · **watch** ≥ 35 · **pass** < 35

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
# 1. Capture evidence (needs APIFY_TOKEN + APIFY_ETSY_ACTOR)
python3 scripts/capture.py --shops DeltaLoom,Olee3DArt --ships-from DE --market US --processing-days 7

# 2. Score and render
python3 scripts/qualify.py --limit 3
```

Output: `leads.md` — ranked table, a card per top lead with quoted evidence
(URL + retrieval date) and a drafted opener, then every rejection with its reason.

## Degraded operation

**The skill runs with no credentials.** With no `APIFY_TOKEN`, it scores the
committed snapshot in `fallback/snapshot/` instead of fetching, prints
`cached snapshot (no APIFY_TOKEN)`, and states the data mode and retrieval date
at the top of `leads.md`. Nothing is fabricated to fill the gap: if evidence is
missing, the shop scores low and says so.

`--limit` defaults to 3 so a run finishes inside the 75-second judging gate.

## Reuse

Swap `inputs/shops.csv` for any shop list. To retarget a different business,
edit the taxonomy in `scripts/taxonomy.py`: each entry is `patterns` (what the
customer says) → `means` (what it implies) → `fix` (what you sell). The rubric
and renderer are unchanged.
