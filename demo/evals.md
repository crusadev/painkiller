# Evaluation cases — periodic stage

Three cases against the committed snapshot. **Observed results are filled in from an
actual run, not written ahead of it** — any case still marked _pending_ has not been executed yet. Command in each case is the one to run.

---

## Case 1 — Intended success: a prospect that is ripe now

```bash
python3 scripts/periodic.py --limit 3
```

**Expect:** `Creat3DLab` ranks first and lands in the RIPE band. Its drivers name
the ratings gap (shipping 4.64 against quality 4.77), the serviceable volume
(~5,300 orders/yr), the momentum (56 reviews in 90d against 4 in the 90d prior),
and the non-US/UK origin (HR). Its card carries the *no buyer complaint quotes*
disclosure, because it has none.

**Observed:** _pending — fill from the dry run before submission._

**What this proves:** the skill can qualify a prospect honestly on published
numbers, without a complaint to quote.

---

## Case 2 — Insufficient evidence: a prospect that cannot be assessed

```bash
python3 scripts/periodic.py
```

**Expect:** shops with fewer than six reviews across both 90-day windows report
`too little review history to read momentum` in *Not assessed*, and their
**confidence** figure drops accordingly while ripeness is computed from the
triggers that did resolve.

**Observed:** _pending — fill from the dry run before submission._

**What this proves:** missing evidence degrades the claim instead of being
silently scored as zero or silently filled in.

---

## Case 3 — Failure: nothing is ripe, and the run says so

```bash
python3 scripts/periodic.py --profile demo/input/profile-strict.json
```

A profile whose `ripeness_bands.ripening` is raised above anything the watchlist
can reach.

**Expect:** the *Why these are interesting now* section is empty and states:
*"Nothing crossed the ripening threshold this run. That is a valid result: the
list is not ripe, and inventing a reason to call wastes the week."* Every
prospect appears under **Not ripe this run** with its reason.

**Observed:** _pending — fill from the dry run before submission._

**What this proves:** an empty week is reported as an empty week. A radar that
always finds something to call is not a radar.

---

## Known gap in this eval set

These three exercise the **periodic** stage only, because that is the stage the
demo runs. The setup and processing stages are interview-driven and write to a
gitignored `state/`; they are exercised by dry run, not by this file.
