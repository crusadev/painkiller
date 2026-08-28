# Evaluation cases

Run: `python3 evals/run_evals.py`

## Case 1 — a shop that should qualify

**Scenario:** a shop scaling fast, printing in one country and selling into
another, with recent reviews describing customs charges, multi-week delivery,
transit damage, and a buyer who could not order at all.

**Expect:** tier `hot`; ≥3 distinct pain signals including `geo_blocked`;
evidence quoted with dates; an opener that leads with the buyer's stated problem.

**Why it matters:** this is the demo case — it proves the taxonomy connects a
real complaint to a specific capability rather than producing generic sentiment.

## Case 2 — a shop that should *not* qualify

**Scenario:** a domestic shop with a 2-day make time and clean recent reviews.

**Expect:** tier `pass`, and a stated reason. Score gap vs. Case 1 ≥ 30 points.

**Why it matters:** a rubric that qualifies everything is not a rubric. This is
the case that proves the skill discriminates, and it is why `leads.md` always
renders rejections with reasons.

## Case 3 — no credentials, no network

**Scenario:** the skill runs with `APIFY_TOKEN` unset — the judging machine.

**Expect:** it scores the committed snapshot, labels the data mode and capture
date at the top of `leads.md`, completes in under 75 seconds, and fabricates
nothing. With no snapshot at all it exits with a message rather than inventing
evidence.

**Why it matters:** graceful degradation is a hard requirement of the event, and
"invent plausible reviews" is the failure mode worth ruling out explicitly.
