# Outreach radar

**Run:** 2026-08-28  ·  **Cadence:** every 7 days  ·  **Prospects swept:** 22

**Data mode:** cached snapshot, no credentials used. Per-shop source URL and retrieval date in `fallback/snapshot/*.json`.

> **Provenance:** this pre-committed fallback was generated from the same watchlist and profile as the live run, evaluating the four metric triggers. The `complaint_keywords` trigger is scored as unresolved here, so live-run figures for shops with complaint text may be higher. Regenerate with `python3 scripts/periodic.py` to replace this file.

Ripeness is a likelihood, not a verdict. It answers *how close is this prospect to the moment their fulfilment stops working* - and every point of it traces to a driver below. Confidence is the share of triggers that could be evaluated at all, not how sure the answer is.

| Prospect | Ripeness | Band | Conf. | Leading driver |
|---|---:|---|---:|---|
| [Creat3DLab](https://www.etsy.com/shop/Creat3DLab) | 82% | RIPE | 100% | shipping 4.64 sits 0.13 below quality 4.77 - their own buyers rate the delivery worse than |
| [BGExpansions](https://www.etsy.com/shop/BGExpansions) | 68% | RIPE | 100% | shipping 4.86 sits 0.08 below quality 4.93 - their own buyers rate the delivery worse than |
| [MouseDenGames](https://www.etsy.com/shop/MouseDenGames) | 54% | RIPENING | 100% | ~4,588 orders/yr sits inside the serviceable band |
| [BKPrint3D](https://www.etsy.com/shop/BKPrint3D) | 48% | RIPENING | 100% | ~4,297 orders/yr sits inside the serviceable band |
| [ClemmyCreations](https://www.etsy.com/shop/ClemmyCreations) | 47% | RIPENING | 100% | ~4,233 orders/yr sits inside the serviceable band |
| [TinkerStudio3D](https://www.etsy.com/shop/TinkerStudio3D) | 42% | WATCH | 100% | ~5,275 orders/yr sits inside the serviceable band |
| [WeLove3D](https://www.etsy.com/shop/WeLove3D) | 41% | WATCH | 100% | ~5,874 orders/yr sits inside the serviceable band |
| [LignumAndLight](https://www.etsy.com/shop/LignumAndLight) | 41% | WATCH | 100% | ~5,870 orders/yr sits inside the serviceable band |
| [RogueHomeDesign](https://www.etsy.com/shop/RogueHomeDesign) | 41% | WATCH | 100% | ~5,106 orders/yr sits inside the serviceable band |
| [myJeepDuck](https://www.etsy.com/shop/myJeepDuck) | 41% | WATCH | 100% | ~3,926 orders/yr sits inside the serviceable band |
| [FusedLine](https://www.etsy.com/shop/FusedLine) | 41% | WATCH | 100% | ~6,347 orders/yr sits inside the serviceable band |
| [LEDBFG](https://www.etsy.com/shop/LEDBFG) | 41% | WATCH | 100% | ~5,228 orders/yr sits inside the serviceable band |
| [Creative3DByBen](https://www.etsy.com/shop/Creative3DByBen) | 41% | WATCH | 100% | ~4,361 orders/yr sits inside the serviceable band |
| [NewSwedishDesign](https://www.etsy.com/shop/NewSwedishDesign) | 41% | WATCH | 80% | ~6,690 orders/yr sits inside the serviceable band |
| [McMaster3D](https://www.etsy.com/shop/McMaster3D) | 41% | WATCH | 100% | ~5,041 orders/yr sits inside the serviceable band |
| [Sander3DPrint](https://www.etsy.com/shop/Sander3DPrint) | 30% | WATCH | 100% | shipping 4.90 sits 0.08 below quality 4.98 - their own buyers rate the delivery worse than |
| [Worldthreedi](https://www.etsy.com/shop/Worldthreedi) | 30% | WATCH | 100% | ~57 orders/yr is below the 1,000 floor - early, not unqualified |
| [MontanaAngleWorx](https://www.etsy.com/shop/MontanaAngleWorx) | 19% | COLD | 100% | shipping 4.82 sits 0.09 below quality 4.90 - their own buyers rate the delivery worse than |
| [ShellypartsShop](https://www.etsy.com/shop/ShellypartsShop) | 14% | COLD | 100% | ~154 orders/yr is below the 1,000 floor - early, not unqualified |
| [3DSchmelzwerk](https://www.etsy.com/shop/3DSchmelzwerk) | 13% | COLD | 100% | ~79 orders/yr is below the 1,000 floor - early, not unqualified |
| [GirdledGoodsShop](https://www.etsy.com/shop/GirdledGoodsShop) | 5% | COLD | 100% | ~95 orders/yr is below the 1,000 floor - early, not unqualified |
| [OffDaBench](https://www.etsy.com/shop/OffDaBench) | 2% | COLD | 100% | ~116 orders/yr is below the 1,000 floor - early, not unqualified |

## Why these 5 are interesting *now*

### Creat3DLab — 82% · RIPE

- shipping 4.64 sits 0.13 below quality 4.77 - their own buyers rate the delivery worse than the product
- ~5,258 orders/yr sits inside the serviceable band
- order rate up 14.0x (4 -> 56 reviews/90d) - scaling into a single-workshop ceiling
- prints in HR; most Etsy demand sits in the US/UK, so the majority of orders cross a border

*No buyer complaint quotes in the captured window.* This prospect qualifies on published numbers alone - open with the numbers, never with a review that does not exist.

### BGExpansions — 68% · RIPE

- shipping 4.86 sits 0.08 below quality 4.93 - their own buyers rate the delivery worse than the product
- ~4,619 orders/yr sits inside the serviceable band
- 60 reviews in the last 90d against none in the 90d before - either new or newly busy; capture more history to tell which
- prints in ES; most Etsy demand sits in the US/UK, so the majority of orders cross a border

*No buyer complaint quotes in the captured window.* This prospect qualifies on published numbers alone - open with the numbers, never with a review that does not exist.

### MouseDenGames — 54% · RIPENING

- ~4,588 orders/yr sits inside the serviceable band
- 60 reviews in the last 90d against none in the 90d before - either new or newly busy; capture more history to tell which
- prints in CZ; most Etsy demand sits in the US/UK, so the majority of orders cross a border

*No buyer complaint quotes in the captured window.* This prospect qualifies on published numbers alone - open with the numbers, never with a review that does not exist.

### BKPrint3D — 48% · RIPENING

- ~4,297 orders/yr sits inside the serviceable band
- 60 reviews in the last 90d against none in the 90d before - either new or newly busy; capture more history to tell which

*No buyer complaint quotes in the captured window.* This prospect qualifies on published numbers alone - open with the numbers, never with a review that does not exist.

### ClemmyCreations — 47% · RIPENING

- ~4,233 orders/yr sits inside the serviceable band
- 60 reviews in the last 90d against none in the 90d before - either new or newly busy; capture more history to tell which

*No buyer complaint quotes in the captured window.* This prospect qualifies on published numbers alone - open with the numbers, never with a review that does not exist.

## Not ripe this run (17)

- **TinkerStudio3D** — 42%. ~5,275 orders/yr sits inside the serviceable band
- **WeLove3D** — 41%. ~5,874 orders/yr sits inside the serviceable band
- **LignumAndLight** — 41%. ~5,870 orders/yr sits inside the serviceable band
- **RogueHomeDesign** — 41%. ~5,106 orders/yr sits inside the serviceable band
- **myJeepDuck** — 41%. ~3,926 orders/yr sits inside the serviceable band
- **FusedLine** — 41%. ~6,347 orders/yr sits inside the serviceable band
- **LEDBFG** — 41%. ~5,228 orders/yr sits inside the serviceable band
- **Creative3DByBen** — 41%. ~4,361 orders/yr sits inside the serviceable band
- **NewSwedishDesign** — 41%. ~6,690 orders/yr sits inside the serviceable band
- **McMaster3D** — 41%. ~5,041 orders/yr sits inside the serviceable band
- **Sander3DPrint** — 30%. shipping 4.90 sits 0.08 below quality 4.98 - their own buyers rate the delivery worse than the product
- **Worldthreedi** — 30%. ~57 orders/yr is below the 1,000 floor - early, not unqualified
- **MontanaAngleWorx** — 19%. shipping 4.82 sits 0.09 below quality 4.90 - their own buyers rate the delivery worse than the product
- **ShellypartsShop** — 14%. ~154 orders/yr is below the 1,000 floor - early, not unqualified
- **3DSchmelzwerk** — 13%. ~79 orders/yr is below the 1,000 floor - early, not unqualified
- **GirdledGoodsShop** — 5%. ~95 orders/yr is below the 1,000 floor - early, not unqualified
- **OffDaBench** — 2%. ~116 orders/yr is below the 1,000 floor - early, not unqualified

## Limitations of this run

- Ripeness reads *public* signals only. A shop can be in pain invisibly.
- Complaint text has a ~0.2% base rate, so it confirms a prospect rather than finding one. The ranking is carried by the ratings gap and by momentum.
- Momentum is measured inside a single capture. A per-shop review cap truncates busy shops, which reads here as *too little history*.
- Buyer geography is not public per shop, so cross-border scoring leans on the general fact that Etsy demand concentrates in the US and UK.
- Nothing here observes the prospect cost, margin, or existing supplier. Ripeness is a reason to call, not a forecast that they will buy.

## Close the loop

Before the next run, tell the skill:

1. Which of these did you contact, and which replied?
2. Where was a stated reason wrong - did anyone say their fulfilment is fine?
3. Who signed since the last run? Signed clients are the real ICP, and they retrain it.

Answers are folded back into the profile: a trigger that keeps producing replies gains weight, one that keeps missing loses it.
