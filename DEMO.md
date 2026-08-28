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
3. Watch for: `376 scored ({'hot': 17, 'watch': 64, 'pass': 83}) -> demo/output/leads.md`
   — it runs with no credentials and takes about a fifth of a second.
4. If nothing visible after 60 seconds, open the fallback:
   [`demo/output/leads.md`](demo/output/leads.md)

## Show this — 25 seconds

**Result:** a ranked list of 376 shops. Scroll to **QuantumQuill3D** at the top:
Canada, Etsy rates its shipping 4.52 against 4.72 for item quality, and three
buyers describe slow shipping — two of them in five-star reviews. Then scroll to **"Not qualified"** — the skill
rejects 83 shops and says why for each.

**Evidence:** every quote carries its star rating, date and a link to the
listing it came from. Each card states its data mode and retrieval date. The
one line worth reading aloud: *all 44 fulfilment complaints in 3,623 reviews sit
in **four- and five-star** reviews* — "took about two months to arrive" inside a
5-star review recommending the shop. Filter by star rating and you find nothing.

**Fallback output was produced:** 2026-08-28 during the event, by running
`python3 scripts/qualify.py` against the committed snapshot in
`fallback/snapshot/` — 3,623 public Etsy reviews and shop facts for 376 shops,
captured the same day via Apify. Not live.
