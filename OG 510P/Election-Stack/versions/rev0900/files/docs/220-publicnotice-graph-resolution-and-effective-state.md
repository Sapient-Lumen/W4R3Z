# 220 — PublicNotice graph resolution (supersedes + corrections → “current state”)

**Track:** A (Deployable core)

PublicNotices (`186`) and PublicNotice feeds (`200`) make incident comms **content-addressed** and **rollback-detectable**.
But audiences still ask one question first:

> “What is the *current* official state?”

A feed is a **windowed list**, not an interpretation.
To keep status boards and monitors consistent (and hard to game), this doc defines a **small, deterministic** way to interpret:

- `supersedes_notice_id` (updates), and
- `correction_of_notice_id` (errors),

without introducing new schemas.

See also:
- Status boards / rumor-control surfaces: `195`
- Feed windowing + anti-rollback: `200`
- Update contract + auditable corrections: `219`
- Monitor contract (integrity + parity + convergence): `221`


## 220.1 The notice graph (two edge types)

Each PublicNotice payload can add **at most one** of these edges:

1) **Supersession edge** (update chain)
   - `supersedes_notice_id = <prior_notice_id>`
   - Meaning: “this notice replaces the prior notice in the *update storyline*.”

2) **Correction edge** (error correction)
   - `notice_type = correction` and `correction_of_notice_id = <prior_notice_id>`
   - Meaning: “this notice corrects a specific prior notice; do not treat the prior notice as silently edited.”

**Operator rule (tight):**
- Use **supersedes** for *newer state* (“what changed since last update”).
- Use **correction** for *factual error repair*.
- Avoid emitting a notice that is both a correction **and** a supersession in one step; publish the correction, then (if needed) a follow-on `status_update` that supersedes the latest state.


## 220.2 “Effective state” (what a status board should show)

Given a set of verified notices (typically from the latest feed window, plus any fetched older windows):

### Step A — Detect supersession forks (treat as a public incident)

Build `superseded_by[notice_id] = {notice_ids_that_claim_to_supersede_it}`.

- If any `notice_id` is superseded by **more than one** notice, you have a **fork**.
  - This can be operator error *or* split-view manipulation.
  - Response: publish a parity snapshot (`201`) and a bounded PublicNotice describing the mismatch (`186`, `216`).

### Step B — Compute “heads” (active update notices)

Define a notice as a **head** if **no other notice** in your set supersedes it.

- Heads represent the current *update storyline endpoints*.
- A deployment may intentionally have multiple heads (e.g., separate incidents), but each head SHOULD have a distinct scope or title prefix.

### Step C — Attach corrections (never hide them)

Build `corrections_of[notice_id] = [correction_notice_ids]`.

When rendering a head notice (and any in-scope notices it supersedes), also render:
- any corrections to that notice, and
- any corrections to notices in its supersession chain.

**Monitor rule:** if a correction notice exists but does not appear across declared channels/feeds, treat it as potential **selective disclosure** and capture evidence (`201`, `180`).


## 220.3 What “current state” is (and is not)

- “Current state” is the set of **head notices**, plus their **attached corrections**.
- It is **not** a free-form narrative stitched from social posts, screenshots, or an editable CMS database (`195`, `206`).
- It is **not** “whatever is easiest to read”; it is whatever is **digest-verifiable**.


## 220.4 Size discipline (how to keep chains readable)

To prevent “status sprawl” without deleting history:

- Prefer short, frequent notices that **supersede** the previous notice (linear chain) (`219`).
- If a chain grows too long for humans, publish a **rollup status update** that:
  - supersedes the prior head, and
  - summarizes the state *briefly*, with digest pointers (do not rehost packet bodies).

The feed chain (`200`) preserves discoverability without making a single page balloon.


## 220.5 Minimal checklist for implementers

A status board / rumor-control page implementation SHOULD:

- Render from the latest `PublicNoticeFeed` (`200`), not from an editable DB.
- Compute heads via supersession edges and display heads prominently.
- Display any corrections inline with the corrected notice.
- Display the feed digest (and the discovery digest) prominently (`195`, `204`).
- Treat forks or missing corrections as incidents and emit portable split-view evidence (`201`).


## 220.6 Election milestones (separate timeline; do not force into supersession)

`notice_type = election_milestone` notices (`237`) are usually **not** “updates to an incident thread”.
They should therefore be rendered as a **separate, time-ordered timeline** (often alongside results status), not forced into a single supersession chain.

Recommended rendering rule (deterministic and bounded):
- Show milestone notices in descending `issued_at` order.
- Do **not** treat a newer milestone notice as superseding an older milestone unless the operator explicitly uses `supersedes_notice_id`.
- Always display any corrections to milestone notices inline (`correction_of_notice_id`).
