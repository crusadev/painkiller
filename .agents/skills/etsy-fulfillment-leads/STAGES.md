# The three stages

This skill runs in three stages. Setup and Processing happen once (and are
revisited when the market changes). The periodic stage is where the user
actually spends their time.

| Stage | Runs | Writes | Demoable |
|---|---|---|---|
| 1 · Setup | once, conversational | `state/profile.json` | no — it is an interview |
| 2 · Processing | once, long | `state/*.md`, `scripts/taxonomy.py` | no — minutes, needs credentials |
| 3 · Periodic | weekly/daily/monthly | `demo/output/radar.md` | **yes — this is the demo** |

`state/` is gitignored. Stages 1 and 2 handle real company and client
information; none of it is ever committed. Only the reduced, publishable
artifacts leave that directory.

---

## Stage 1 — Setup

**Goal:** a clear picture of who the user is, what the company sells, the ICP
they *believe* they have, the ICP their signed clients *actually* describe, the
weight of cold email versus cold call in their motion, and a list of live
outreach candidates.

### Mine first, then ask

Do not open with a blank questionnaire. Ask permission, read what already
exists, then bring drafted answers back for correction. People correct a wrong
answer far more precisely than they compose a right one from nothing.

Ask for access explicitly, and name what you can reach:

> Before I ask you anything, may I read your existing chats and notes? Most of
> this is usually already written down somewhere. I can read the sessions on
> this machine directly. For anything else — ChatGPT, Claude on the web, a CRM
> export, a pitch deck, past proposals — export it and drop it in `state/inbox/`
> and I will read that too. What may I look at?

What to reach for:
- Local agent sessions on this machine (list them, search transcripts).
- Anything the user drops in `state/inbox/` — chat exports, decks, proposals,
  call notes, a CRM CSV, old outreach threads.
- The repo itself: an existing prospect list, previous outputs.

Then present each answer below as a **draft with a confidence**, and ask only
for what mining could not settle or contradicted itself on.

### The question set

Ask one at a time, batching only tightly related pairs. Twelve questions is the
target; skip any the mining already answered well.

**Who is asking**

1. What is your name, and what do you actually own here — do you send the
   emails yourself, or hand a list to someone who does?
2. When this works, what changes in your week? (Anchors the deliverable to a
   person's Monday, not to an abstraction.)

**What the company is**

3. In one sentence, what do you sell — and what does it *remove* for the buyer?
   The second half matters more than the first: the triggers get built from what
   you remove, not from what you make.
4. Finish this sentence: *"Our customers used to have to ___, and now they
   don't."*
5. What do you lose deals to? Not competitors — the *status quo* they'd keep if
   they said no.

**Theoretical ICP**

6. If you could clone one customer 500 times, who is it? Describe them the way
   you'd describe them to a new hire.
7. Who do you deliberately *not* serve, and why? (An ICP without an explicit
   boundary is a wish list.)

**Real ICP — the part that usually disagrees with the last two**

8. Name every client you've actually signed. For each: how did they arrive —
   inbound, outbound, intro, event, accident?
9. Which signed client surprised you? The one who was not supposed to be a fit
   and is now happy.
10. Which client fits your ICP on paper and has been a grind in practice?
11. For your best client: what was going wrong for them the *week* they replied
    to you? Not their general problem — the specific thing that made that week
    the week. (This is the single highest-value question in the interview. The
    periodic stage is an attempt to detect that week, from outside, at scale.)

**The motion**

12. Cold email, cold call, LinkedIn, ads, community, intros — rank what actually
    produces first meetings, and be honest about which of these you *wish* worked.
13. What does your current opener look like? Paste a real one, including one
    that got no reply.
14. How many prospects can you genuinely work in a week? (Sets the size of the
    periodic report. A radar returning 200 leads to a person with 20 slots is a
    broken radar.)
15. How often do you want to run this — daily, weekly, monthly?

**The list**

16. Where does your current prospect list live, and how was it built? Anything
    known-bad in it?

### Output of Stage 1

`state/profile.json` — the answers, normalised, with a `source` on each field
recording whether it came from mining or from the user, and a `confidence`.
Anything still unknown is written as `null` with a note, never guessed.

Read the profile back in prose and ask for corrections before moving on. Do not
start Stage 2 on an unconfirmed profile.

---

## Stage 2 — Processing

**Goal:** turn the profile into the thing the periodic stage runs on — a set of
triggers, thresholds and keywords grounded in who actually signed.

Long-running. Announce the plan and the count of work items before starting, so
progress means something. Emit a progress line every ~10%.

### Steps

1. **Enumerate the work.** Count the signed clients and the prospects to sweep.
   State both. That count is the denominator for all progress reporting.

2. **Research each signed client.** Where do they sell, on what platforms, in
   what geographies? What is their public vibe — how do they talk, what do they
   charge, what do they emphasise? What is distinctive about them?

3. **Theorise how each was won.** Cross the research with what the user said in
   questions 8–11 and with what the mined chats show. Produce a *hypothesis*,
   labelled as one. Never state a motive as fact.

4. **Compare real ICP against theoretical.** Name the gap plainly. The gap is
   usually the deliverable: the theoretical ICP is a category, the real one is a
   condition. Categories cannot be detected from outside; conditions can.

5. **Compare company vibe against client vibe.** Where the two diverge, outreach
   language is being written for the wrong reader.

6. **Derive triggers and keywords.** For each: the metric or pattern, the level
   at which it fires, its weight, and *why it predicts readiness*. A trigger
   without a stated causal story is a coincidence waiting to mislead.
   Keyword patterns go into `scripts/taxonomy.py` as `patterns` → `means` →
   `fix`. **Every new pattern must be run over the whole corpus and every hit
   eyeballed** before it ships — see the snippet in `HANDOFF.md`.

7. **Set up tracking.** Propose the concrete mechanism for each metric — which
   Apify actor, which API, which skill, at what cadence and cost. Where the
   choice is not obvious, ask rather than pick. Wire up what the user approves.

8. **Explain it back.** Three things, in order: what is being tracked and whether
   that matches what they said in Stage 1; how it will be tracked; and — at
   length — **what this cannot see**. A tracked metric presented without its
   blind spot is worse than no metric, because it gets trusted.

Pause and ask whenever a judgement call would change the triggers.

### Output of Stage 2

Written to `state/`, gitignored:

| File | Contents |
|---|---|
| `state/clients.md` | Each signed client: where they sell, vibe, what is distinctive, and the labelled hypothesis for why they signed |
| `state/icp.md` | Real versus theoretical ICP, the gap, and what makes the real one detectable from outside |
| `state/vibe.md` | Company voice against client voice, and what that implies for the opener |
| `state/triggers.md` | Every trigger: metric, threshold, weight, causal story, tracking mechanism, and limitation |
| `state/profile.json` | Updated in place with the derived triggers |

---

## Stage 3 — Periodic

**Goal:** the recurring run. Sweep every prospect, find who has become
interesting *since last time*, and say why now.

```bash
python3 scripts/periodic.py --profile state/profile.json
```

For each prospect: check listings and shop data for the keywords from Stage 2,
check each tracked metric against its trigger level, and combine them into a
**ripeness likelihood** — how close this prospect is to the moment their
fulfilment stops working.

### Ripeness is not a yes/no

Report a percentage and a band (RIPE / RIPENING / WATCH / COLD), because the
underlying question is continuous. A prospect at 58% is not a "no", it is a
"call in three weeks and here is what to watch for in between".

Report **confidence** separately, and define it: the share of triggers that
could be evaluated at all. A prospect can be highly ripe at low confidence, and
conflating the two is how a radar starts lying.

Every point of ripeness must trace to a named driver. No unexplained scores.

### Always render

- The prospects that fired, each with its drivers and its evidence.
- Where a prospect qualifies on numbers alone, an explicit statement that there
  are no complaint quotes — and an opener that leads with the numbers instead.
- The prospects that did **not** fire, with the reason. A radar that always
  finds something is not a radar.
- The limitations of that specific run.

### Close the loop

End every run by asking:

1. Which of these did you contact, and which replied?
2. Where was a stated reason wrong — did anyone say their fulfilment is fine?
3. Who signed since the last run?

Newly signed clients go back through Stage 2 research and join the real-ICP
evidence base. Triggers that keep producing replies gain weight; triggers that
keep missing lose it. Record each adjustment in `state/triggers.md` with the
date and the reason, so the weighting has a history rather than just a value.
