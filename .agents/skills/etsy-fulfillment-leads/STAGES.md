# The three stages

This skill runs in three stages. Setup and Processing happen once, and are
revisited when the market changes. The periodic stage is where the user actually
spends their time.

| Stage | Runs | Writes | Demoable |
|---|---|---|---|
| 1 · Setup | once, ~10 min conversation | `state/profile.json` | no — it is an interview |
| 2 · Processing | once, long | `state/*.md`, `demo/input/shops.csv`, `scripts/taxonomy.py` | no — minutes, needs credentials |
| 3 · Periodic | weekly by default | `demo/output/leads.html` + `leads.md` | **yes — this is the demo** |

`state/` is gitignored. Stages 1 and 2 handle real company and client
information; none of it is ever committed. Only reduced, publishable artifacts
leave that directory.

**Privacy rule across all three stages.** The unit of analysis is the *company*.
Record business facts about clients and prospects. Never write an individual's
name, email, handle or profile into `state/` — not a buyer, not a seller, not a
contact — even when a mined chat contains it. If a fact only makes sense
attached to a person, it does not belong in the profile.

---

## Stage 1 — Setup

**Goal:** who the user is, what the company sells, the ICP they *believe* they
have, the ICP their signed clients *actually* describe, the real weight of cold
email versus cold call, and a list of live outreach candidates.

Target ten minutes. If it runs longer, mining was skipped or done badly.

### Mine first, then ask

Never open with a blank questionnaire. Ask permission, read what exists, then
bring drafted answers back for correction. People correct a wrong answer far
more precisely than they compose a right one from nothing.

Ask for access explicitly, naming what is reachable:

> Before I ask anything: may I read your existing chats and notes? Most of this
> is already written down somewhere. I can read the agent sessions on this
> machine directly. For anything else — ChatGPT, Claude on the web, a CRM
> export, a deck, past proposals, old outreach threads — export it into
> `state/inbox/` and I will read that too. What may I look at?

Reach for: local agent sessions (list them, search transcripts); anything in
`state/inbox/`; the repo itself for an existing prospect list or prior outputs.

Extract specifically — client names and how each arrived, language the user uses
about their own product, any number they quote twice, complaints about the
current outbound process, and openers that did or did not work.

Then present every answer below as a **draft with a confidence**, and ask only
what mining could not settle or contradicted itself on. A well-mined setup asks
four questions, not twelve.

### The twelve

Ask one at a time. Skip any the mining answered well; say that you are skipping
it and what you believe the answer is.

**Who is asking**

1. What do you own here — do you send the emails yourself, or hand a list to
   someone who does? And when this works, what changes in your week?

**What the company is**

2. In one sentence: what do you sell, and what does it *remove* for the buyer?
   The second half matters more — triggers get built from what you remove.
3. Finish this: *"Our customers used to have to ___, and now they don't."*
4. What do you lose deals to? Not competitors — the **status quo** they keep if
   they say no.

**The ICP they think they have**

5. If you could clone one customer 500 times, who is it? Describe them the way
   you would to a new hire.
6. Who do you deliberately **not** serve, and why? An ICP without a boundary is
   a wish list, and the boundary is what makes the periodic stage able to reject.

**The ICP they actually have** — this usually disagrees with 5 and 6

7. Name every client you have signed. For each: how did they arrive — inbound,
   outbound, intro, event, accident?
8. Which signed client surprised you — not supposed to fit, now happy? And which
   one fits perfectly on paper and has been a grind?
9. **For your best client: what was going wrong for them the *week* they replied
   to you?** Not their general problem — the specific thing that made that week
   the week.

   *This is the highest-value question in the interview.* Stage 3 is an attempt
   to detect that week, from outside, at scale. If the answer is vague, push
   once: what changed, who noticed, what did it cost them?

**The motion**

10. Rank what actually produces first meetings — cold email, cold call,
    LinkedIn, ads, community, intros — and say which of these you *wish* worked.
    Then paste a real opener, including one that got no reply.
11. How many prospects can you genuinely work in a week, and how often do you
    want to run this? *(Assume weekly unless told otherwise.)* This sets the
    size of the report: a radar returning 200 leads to someone with 20 slots is
    a broken radar.

**The list**

12. Where does your prospect list live, how was it built, and what is
    known-bad in it?

### Output

`state/profile.json` — answers normalised, each field carrying `source`
(`mined` or `stated`) and `confidence`. Anything unknown is `null` with a note,
never guessed.

Read it back in prose. Do not start Stage 2 on an unconfirmed profile.

---

## Stage 2 — Processing

**Goal:** turn the profile into what the periodic stage runs on — triggers,
thresholds, keywords and a watchlist, grounded in who actually signed.

Long-running. **Enumerate and state the work before starting** — number of
signed clients to research, number of prospects to sweep. That count is the
denominator; emit a progress line every ~10% of it.

### Steps

1. **Enumerate.** State both counts. No progress reporting without a
   denominator.

2. **Research each signed client.** Where do they sell, on which platforms, in
   which geographies? Public vibe — how they talk, what they charge, what they
   emphasise. What is distinctive.

3. **Theorise how each was won.** Cross the research with answers 7–9 and with
   the mined chats. Produce a **hypothesis, labelled as one**. Never state a
   motive as fact; the user will correct a labelled guess and silently absorb an
   unlabelled one.

4. **Real ICP versus theoretical.** Name the gap plainly. The theoretical ICP is
   almost always a *category*; the real one is a *condition*. Categories cannot
   be detected from outside — conditions can, and that is the whole deliverable.

5. **Company vibe versus client vibe.** Where they diverge, the outreach is
   written for the wrong reader.

6. **Derive triggers and keywords.** Each needs: metric or pattern, firing
   level, weight, and **why it predicts readiness**. A trigger without a causal
   story is a coincidence waiting to mislead. Keyword patterns go into
   `scripts/taxonomy.py` as `patterns` → `means` → `fix`.

   **Run every new pattern over the whole corpus and eyeball every hit** before
   it ships — snippet in `HANDOFF.md`. `\bcustoms?\b` matching "custom-made" cost
   hours once already.

7. **Build the watchlist.** Write `state/watchlist.json` in the shape
   `demo/input/watchlist.json` uses: one row per prospect, each carrying its
   source URL and retrieval date. This is what Stage 3 sweeps.

8. **Specify tracking.** For each metric, name the concrete mechanism it would
   use — which Apify actor, API, or connected service — at what cadence and
   cost. Ask rather than pick when the choice is not obvious.

   **Specify, do not connect.** Stage 2 writes the tracking plan into
   `state/triggers.md`; it does not authorise services or start pulling data.
   Connecting is a separate, explicit step the user asks for, because it spends
   money and grants access. A plan the user can read and approve beats a
   connection they discover after the fact.

   Known-good mechanisms: Apify `hello.datawizards~etsy-reviews` (~$0.005/review)
   and `getdataforme~etsy-shop-details-scraper` (~$0.01/shop). Where a prospect
   has a linked storefront domain, Google Search Console / GA4 / Google Ads can
   in principle carry demand-side triggers — note them as *available, not
   wired*, and note the coverage limit: only 8 of 22 captured shops have a usable
   domain, so any such trigger is unmeasurable for most of the list. Avoid any
   actor returning seller emails.

9. **Explain it back**, in this order: what is tracked and whether that matches
   Stage 1; how it will be tracked; and — at length — **what it cannot see**. A
   tracked metric presented without its blind spot is worse than no metric,
   because it gets trusted.

Pause and ask whenever a judgement call would change the triggers.

### Output

All gitignored, in `state/`:

| File | Contents |
|---|---|
| `clients.md` | Each signed client: where they sell, vibe, what is distinctive, labelled hypothesis for why they signed |
| `icp.md` | Real versus theoretical ICP, the gap, and what makes the real one detectable from outside |
| `vibe.md` | Company voice against client voice, and what it implies for the opener |
| `triggers.md` | Per trigger: metric, threshold, weight, causal story, tracking mechanism, limitation |
| `watchlist.json` | Prospects to sweep, with provenance |
| `profile.json` | Updated in place with the derived triggers |

---

## Stage 3 — Periodic

Implemented by `scripts/qualify.py`. This is the stage the user actually lives
in, and the one the demo shows.

```bash
python3 scripts/qualify.py       # no credentials; scores the committed snapshot
```

Writes `demo/output/leads.md` and `demo/output/leads.html`. Refresh the evidence
first with `scripts/capture.py` and `scripts/capture_shop.py` when an
`APIFY_TOKEN` is available; without one it scores what is committed and says so
in the report header.

### What the report must always do

- **Rank, and be willing to reject.** Every non-qualifying prospect is listed
  with the reason it did not qualify. A sweep that always finds something is not
  a sweep. On the committed data 83 shops are rejected outright.
- **Separate "too small" from "not interesting".** A prospect below the volume
  floor is tiered `nurture` with its gap to the floor, its growth rate and a
  recheck cadence — it is a lead we are early for, not one to discard. 212 shops
  sit there.
- **Never assert evidence it does not have.** A prospect qualifying on
  shop-level metrics alone says so in place of a quote, and its drafted opener
  leads with the metric rather than claiming reviews said something they did
  not.
- **Carry provenance.** Every quote keeps its date and source URL; the header
  states the data mode and capture date, and cached data is never described as
  live.

Re-run Stage 1 when the offer changes, and Stage 2 when the taxonomy stops
matching what prospects actually say.
