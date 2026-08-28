# Run sheet

## Say this — 20 seconds

**Team:** 3DAPI

**Track:** custom — signal-based lead qualification

**Who has the problem:** the founder doing outbound at a distributed
3D-printing manufacturing network. They have 411 candidate Etsy shops and no
basis for deciding who to contact first.

**The job this skill does:** ranks those shops by how visibly they are hitting
the limits of printing everything in one place, and attaches the buyer evidence
that proves it.

**Boundary — what it never does:** it never invents a complaint. A shop with no
buyer quotes says so and qualifies on shop-level facts, or not at all. It never
stores the identity of a buyer or a seller.

## Run this — 60 seconds

1. Codex is open at the repository root.
2. Paste [`demo/seed-prompt.md`](demo/seed-prompt.md).
3. Watch for: `376 scored ({'hot': 17, ...}) -> leads.md + leads.html` — it runs
   with no credentials and takes about a fifth of a second.
4. Open [`demo/output/leads.html`](demo/output/leads.html) in the browser. That
   is the report; `leads.md` beside it holds the full 376-shop listing.
5. If nothing visible after 60 seconds, open that same file — it is committed
   and identical to what the run produces.

## Show this — 25 seconds

**Result:** the page opens on the finding — *all 44 fulfilment complaints across
3,623 reviews sit in four- and five-star reviews.* Then **QuantumQuill3D** at
the top: prints in Canada, and the two bars show Etsy rating its shipping 4.52
against 4.72 for item quality, with the shortfall hatched between them. The
print is fine; the distance is not. Two buyers say so in their own words, both
in five-star reviews.

**Evidence:** every quote carries its star rating, date and a link to the
listing. The header states the data mode and retrieval date. Scroll once more:
83 shops rejected with a stated reason, 212 tracked below the volume floor — it
says no as readily as yes.

**Fallback output was produced:** 2026-08-28 during the event, by running
`python3 scripts/qualify.py` against the committed snapshot in
`fallback/snapshot/` — 3,623 public Etsy reviews and shop facts for 376 shops,
captured the same day via Apify. Not live.
