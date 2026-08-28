# etsy-fulfillment-leads

**GTM Skillathon 2026 · Bucharest**

Turns public Etsy buyer complaints into a ranked, evidence-backed lead list for
[3DAPI](https://dapi.digital), a global manufacturing network for 3D-printed
products.

## The idea

Etsy's negative reviews are dominated by fulfilment complaints — slow delivery,
customs charges, transit damage, "you don't ship to my country", inconsistent
print quality. All of them share one root cause: **the product was printed far
from the person who bought it, by a single workshop.**

That is exactly what a distributed print network removes. So each complaint is
not sentiment — it is a qualified, timed sales trigger written by the
prospect's own customer.

## Run it

```bash
python3 scripts/qualify.py --limit 3     # no credentials needed
```

Writes `leads.md`: a ranked table, a card per top lead with quoted evidence
(source URL + retrieval date) and a drafted opener, and every rejected shop
with its reason.

To refresh evidence, copy `.env.example` to `.env`, add your Apify token, then:

```bash
python3 scripts/capture.py --shops DeltaLoom,Olee3DArt --ships-from DE --market US
```

## Layout

| Path | |
|---|---|
| `.agents/skills/etsy-fulfillment-leads/SKILL.md` | The skill: taxonomy, rubric, privacy rules |
| `SEED_PROMPT.md` | The task, as stated |
| `inputs/shops.csv` | 411 candidate shops · provenance in `inputs/SOURCES.md` |
| `fallback/snapshot/` | 376 enriched shops · 22 with full review capture |
| `scripts/taxonomy.py` | Pain signal → what it means → what fixes it |
| `scripts/qualify.py` | Scoring and rendering |
| `scripts/capture.py` | Apify capture, strips reviewer identity at ingest |
| `fallback/snapshot/` | Committed evidence for credential-free runs |
| `evals/` | Three evaluation cases + runner |
| `DEMO.md` | 2.5-minute runsheet |
| `HANDOFF.md` | Picking this up cold: state, gotchas, open work |

## Privacy

The lead is the **shop**. Reviewer identity is discarded at ingest before
anything is written to disk — only rating, date, text and listing URL survive.
Asserted by `tests/test_scoring.py`, not just promised. The internal prospect
sheet (team names, outreach status, contact emails) is gitignored; only the
reduced list is published.

## Reuse

Swap `inputs/shops.csv` for any shop list. Retarget to another business by
editing one table in `scripts/taxonomy.py`.

MIT.
