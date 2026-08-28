# Demo runsheet — 2.5 minutes

**Skill:** `etsy-fulfillment-leads` · **Repo:** public · **Run:** no credentials required

---

**0:00 — The problem (20s)**

3DAPI is a global manufacturing network for 3D-printed products. Sellers list,
we route each order to the print farm nearest the customer, produce it locally
under QC, ship domestically.

We have 411 candidate Etsy shops. Which do we call *this week*, and what do we
say? Reading 411 shops' reviews by hand is the whole job, and it does not scale.

**0:20 — The insight (25s)**

Etsy's negative reviews are dominated by fulfilment complaints — "took four
weeks", "I paid €18 customs", "arrived cracked", "you don't ship to Australia".

Every one of those is the same root cause: *printed far from the buyer, by one
workshop*. That is precisely what routing removes. So a complaint is not
sentiment — it is a qualified, timed sales trigger, written by the prospect's
own customer.

**0:45 — Run it (35s)**

```bash
python3 scripts/qualify.py --limit 3
```

Point at the header: **data mode and capture date**, stated up front. No token
on this laptop — it scores the committed snapshot and says so.

**1:20 — The output (45s)**

Open `leads.md`.

1. **Ranked table** — tier, score, mapped pain signals.
2. **A top lead card** — the quoted buyer review, its date, its source URL, and
   the taxonomy line connecting it: *slow delivery → long transit from a single
   origin → route to the nearest print farm.*
3. **The opener** — leads with their problem, in their customer's words.
4. **Scroll to "Not qualified"** — this is the part to linger on. The skill
   rejects shops and says why. A rubric that qualifies everything is not a rubric.

**1:50 — The honest finding (25s)**

Across 1,283 real reviews: 96.5% five-star, and **0.2% describe a fulfilment
failure**. Complaint text alone ranks nothing.

So the top signal is not complaints — it is that Etsy publishes
`shipping_rating` **separately** from `item_quality_rating`. When shipping sits
below quality, the seller's own customers are saying the product is fine and
the delivery is not. Creat3DLab: 4.64 shipping against 4.77 quality, 27,000
sold, printing in Croatia. That is the pitch, in their buyers' numbers.

And when a shop qualifies on ratings alone, the card says *"no buyer complaint
quotes in the captured window"* and the opener leads with the numbers instead
of pretending reviews said something they did not.

**2:10 — Reuse (15s)**

Swap `inputs/shops.csv` for any shop list. Retarget the whole skill by editing
one table in `scripts/taxonomy.py`: what the customer says → what it implies →
what you sell.

And: the lead is the *shop*. Reviewer identity is discarded at ingest, before
anything touches disk — enforced by a test, not a promise.

**2:25 — Close**

Public complaints, mapped to a specific capability, ranked, with the evidence
attached.

---

## If something breaks

- No network: expected — it is already running from the snapshot.
- Empty output: `ls fallback/snapshot/` then `python3 scripts/qualify.py --only <shop>`.
- Skip the live run entirely; the snapshot path is the demo.
