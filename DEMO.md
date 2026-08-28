# Demo runsheet — 2.5 minutes

**Skill:** `etsy-fulfillment-leads` · **Stage shown:** 3 of 3, the periodic run
**Run:** no credentials, no API keys, ~1 second · **Repo:** public

---

**0:00 — The problem (20s)**

3DAPI is a distributed manufacturing network for 3D-printed products. Sellers
list; we route each order to the print farm nearest the customer, produce it
locally under QC, ship domestically.

Outbound has 411 candidate Etsy shops. The question is never *who could use
this* — it is **who is ready this week, and what do I open with**. Those are
different questions, and only the second one is worth a Monday.

**0:20 — The three stages (20s)**

The skill runs in three stages. **Setup** interviews you — who you are, what you
sell, the ICP you think you have, and the ICP your signed clients actually
describe. **Processing** researches those signed clients and derives the
triggers that predict readiness. Both write locally and never leave your
machine.

**Stage three is what you live in**, and it is what runs now.

**0:40 — Run it (25s)**

```bash
python3 scripts/periodic.py
```

Point at the header: **no credentials, data mode and retrieval date stated up
front.** It sweeps 22 prospects against 5 triggers and prints progress as it
goes.

**1:05 — The output (50s)**

Open `demo/output/radar.md`.

1. **The radar table** — every prospect with a **ripeness percentage**, a band,
   and the driver that produced it. Not a yes/no: readiness is continuous, and a
   prospect at 54% is not a "no", it is a "call in three weeks".

2. **Confidence is a separate column**, and the report defines it — the share of
   triggers that could be evaluated at all. A prospect can be ripe at low
   confidence. Collapsing those two numbers into one is how a radar starts
   lying.

3. **Creat3DLab, 82%, RIPE.** Four independent triggers: shipping 4.64 against
   quality 4.77, ~5,300 orders/yr inside the serviceable band, 56 reviews in 90
   days against 4 in the 90 before — and it prints in Croatia while the demand
   sits in the US. Its card says **"no buyer complaint quotes in the captured
   window"**, because there are none, and the opener leads with the numbers
   instead of pretending otherwise.

4. **Scroll to "Not ripe this run" — 17 of 22.** This is the part to linger on.
   The skill rejects most of the list and says why. A radar that always finds
   something to call is not a radar.

**1:55 — The honest finding (20s)**

Across 1,283 real reviews: 96.5% five-star, **0.2% describe a fulfilment
failure**. Ranking on complaints returns nothing.

So the load-bearing signal is not complaints. Etsy publishes `shipping_rating`
**separately** from `item_quality_rating` — when shipping sits below quality,
the seller's own customers are saying the product is fine and the *delivery* is
not. That number exists for every shop, which is what makes an honest ranking
possible at all. Complaints then confirm; they never rank.

**2:15 — Limits and the loop (15s)**

Every run ends with what it **cannot** see — invisible pain, truncated history,
buyer geography that is not public — and then asks who replied, which reason was
wrong, and who signed. Triggers that produce replies gain weight; triggers that
miss lose it.

**2:30 — Close**

Public signals, mapped to one capability, scored as a likelihood, with the
evidence and the blind spots both attached.

---

## Reuse

Nothing here is Etsy-specific below the surface. Triggers, thresholds and
weights live in the profile JSON that Stage 2 writes — not in the code. Point
`--watchlist` at another list and `--profile` at another company's setup and the
same runner works. With no review corpus at all it runs metrics-only and reports
the keyword trigger as unassessed rather than scoring it zero.

## If something breaks

- **No network:** expected — it never needed one.
- **Live run stalls or errors:** `demo/output/radar.md` is pre-committed. Open it
  and keep going; it is the same file the run produces.
- **Empty output:** `ls demo/input/` then `python3 scripts/periodic.py --limit 3`.
- Skip the live run entirely if time is short. The committed report is the demo.
