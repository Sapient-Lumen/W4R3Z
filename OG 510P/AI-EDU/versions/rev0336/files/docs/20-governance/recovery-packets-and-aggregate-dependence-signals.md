# Recovery packets and aggregate dependence signals without learner-risk files

## Current overlay

Recovery signals now intersect with companion safeguarding. Repeated answer dependence, reassurance
seeking, after-hours attachment, or private emotional disclosure should not be treated only as a
study-skill issue; it may require `CD` review, memory reduction, human coverage, and a recovery path
that avoids stigma or ambient monitoring.

This document closes the archive's next implementation gap about **what teacher-owned recovery paths
for official study companions may actually retain, what may be aggregated for service improvement,
and where that logging must stop so dependence handling does not turn into durable learner-risk
files or broad trace capture**.

The archive's current bet is:

> **keep dependence handling short-lived, purpose-bound, and teacher-owned: use a tiny temporary
recovery packet for named reset work, allow only coarse aggregate service signals for improvement,
and require any hotter case file to be justified by a separate trigger rather than by “learning
support” alone.**

That matters because four failures now travel together:

- **packet inflation** — a temporary reset note silently becomes a durable learner dossier;
- **dependence scoring** — repeated answer use becomes a hidden risk label or ranking feature;
- **cross-function drift** — study-support traces migrate into discipline, advising, admissions,
  welfare, or progression files;
- **telemetry substitution** — institutions try to solve pedagogical design problems by capturing
  more learner history instead of improving task design, human availability, or branch rules.

Current public signals point in the same direction. OECD's 2026 outlook says GenAI supports learning
when it is used with clear teaching principles rather than as generic outsourcing, and that
educational systems should protect learners while aligning GenAI to educational objectives. UNESCO's
2025 rights framing says AI in education should strengthen rather than endanger the right to
education, while UNESCO's 2026 teacher and student competency frameworks centre human agency,
ethics, and AI pedagogy rather than passive dependence. OpenAI's 2026 learning-outcomes work adds a
narrower measurement signal: educational value should be assessed longitudinally and can rely on
de-identified interaction data rather than raw durable learner dossiers. ICO guidance then sharpens
the data side: organisations should keep only personal data that are adequate, relevant, and limited
to what is necessary for the purpose, and by default should limit the amount collected, extent of
processing, period of storage, and degree of accessibility. The same ICO children's code keeps
profiling children off by default unless there is a compelling reason. See `B138`, `B151`, `B152`,
`B153`, `B154`, `B155`, `B156`.

## Relationship to the rest of the archive

This document is a narrow companion to:

- [`learning-first-interaction-defaults-and-answer-release-triggers.md`](learning-first-interaction-defaults-and-answer-release-triggers.md),
  which says **when** ordinary AI-owned interaction must cool, hand off, or stop;
- [`minimum-observability-and-retention-without-surveillance.md`](minimum-observability-and-retention-without-surveillance.md),
  which says **how hot** visibility and retention may become;
- [`persistent-memory-personalization-and-learner-model-boundaries.md`](persistent-memory-personalization-and-learner-model-boundaries.md),
  which says **what kinds of remembered state** may exist at all.

It adds one thing only:

- a **small packet-and-signal rule** for recovery after repeated answer dependence, non-transfer,
  looping confusion, relational stickiness, or hidden path pressure.

## The archive now distinguishes only two legitimate recovery artifacts

The archive now permits only two ordinary artifacts below a separately triggered case file.

| Artifact | Owner | Ordinary use | Default visibility / retention posture |
|---|---|---|---|
| **temporary recovery packet** | named teacher, tutor, or service owner | reset one learner's support mode after `IR3` handoff | coolest workable `V2-V3 / R1`, with expiry set at creation |
| **aggregate dependence signal** | service owner, course team, or governance owner | inspect whether one branch, construct, or service design is creating repeated dependence or failed re-entry | `V0-V1 / R0-R1`, using de-identified or minimum-cell reporting |

Anything hotter than those two artifacts belongs on a **separate rail** — integrity review,
safeguarding, formal progression, complaint, or other case-bound handling — and must be opened by
that separate trigger, not by the mere fact that a learner needed recovery.

## The temporary recovery packet (`RP0-RP2`)

The archive now keeps the learner-bound side deliberately short.

| Packet state | When it exists | What it contains | What it cannot become |
|---|---|---|---|
| **`RP0` — none** | `IR0-IR2`; AI-owned reset or cool-down remains inside ordinary interaction | no new durable learner-bound packet | a hidden background profile built from ordinary hinting or cool-down events |
| **`RP1` — temporary recovery packet** | `IR3`; a named adult must reset posture, re-entry condition, or support mode | only the minimum fields below, owned by one named adult/service owner | a durable learner-risk file, cross-function tag, or broad transcript store |
| **`RP2` — case-bound file by separate trigger** | a distinct integrity, rights, safeguarding, formal progression, or complaint trigger has fired | whatever the separate governed rail requires | the default shape for ordinary dependence handling |

### `RP1` fields the archive now permits by default

A temporary recovery packet may usually contain only seven fields:

1. **construct / task family** — what the learner was trying to do;
2. **active grammar context** — task mode, interaction branch, and answer-release trigger family in
   force when recovery became necessary;
3. **dependence signal family** — `DS1-DS5`, using the named family rather than a narrative
   transcript;
4. **scope band** — whether the pattern appeared in the current session, the current task window, or
   repeated across multiple task windows;
5. **already-surfaced access or language condition** — only if the learner or the published support
   route already made it relevant to the reset; no fresh inference is added here;
6. **next posture and re-entry condition** — what the named adult has set as the next allowed help
   mode and what the learner must show before ordinary AI support resumes;
7. **expiry / next review point and deletion owner** — when the packet should disappear or be
   reconsidered, and who is responsible.

The packet may also carry **one selected excerpt pointer** only when the adult owner cannot
understand the failure mode without it. The archive prefers a bounded excerpt or checkpoint
reference over copied full dialogue.

### What `RP1` may not contain by default

A temporary recovery packet may not, by default, contain:

- full transcripts or complete prompt/response histories;
- inferred ability labels, motivation labels, or mental-state labels;
- open-ended behavioural histories or exact time-on-tool dossiers;
- cross-course or cross-function summaries unless a separate rail already lawfully owns them;
- downstream tags for discipline, admissions, readiness ranking, welfare screening, or queue
  priority;
- a standing label like “AI-dependent learner,” “high offloading risk,” or any equivalent
  identity-like status.

The archive treats those as a different governance act, not as a more detailed version of recovery.

## The aggregate dependence signal rule (`AG1-AG5`)

The archive still permits institutions to learn from repeated recovery events — but only through
narrow aggregate views designed for branch repair, staffing, and service redesign.

### Allowed aggregate signal families

| Signal family | Ordinary question it answers | Lowest useful grouping |
|---|---|---|
| **`AG1` — repeated fuller-answer pull rate** | where is one branch or construct repeatedly collapsing toward answer demand? | by service, subject/construct family, branch, and task mode |
| **`AG2` — non-transfer after release rate** | where are released answers not turning back into explanation, adaptation, or analogue success? | by service, construct family, release-trigger family |
| **`AG3` — recovery ladder flow** | where are learners moving from `IR1` to `IR2` to `IR3` unusually often? | by service, cohort/age band, and construct family |
| **`AG4` — re-entry success after recovery** | after cool-down or teacher-owned reset, does ordinary guided support start working again? | by service, posture, and construct family |
| **`AG5` — path-pressure and mismatch signals** | is the service design or staffing pattern making AI the only practical route, or hiding an access mismatch? | by service, site, time window, and support/branch family |

The point of these aggregates is not to rank learners. It is to tell the institution where the
**service shape** is failing.

### Aggregate safeguards the archive now requires

1. **minimum-cell or de-identification rule** — do not publish or route aggregates at a level that
   effectively re-identifies one learner or one tiny class case;
2. **no learner leaderboard rule** — no lists of “most dependent learners,” “highest offloading
   risk,” or equivalent dashboards;
3. **branch-repair purpose rule** — aggregates exist to adjust branch defaults, staffing, training,
   release triggers, or re-entry design, not to alter unrelated learner treatment;
4. **windowed retention rule** — keep the aggregate long enough to improve the service, then roll or
   delete it; do not preserve it indefinitely by default;
5. **no hidden cross-function join rule** — tutoring/service aggregates may not quietly join
   advising, attendance, discipline, or benefits-linked systems without a fresh governance decision.

These are service-improvement signals, not the seed of a general learner-scoring system.

## The default crosswalk to observability and memory

The archive now makes the crosswalk explicit.

| Recovery situation | Default rail |
|---|---|
| ordinary interaction, bounded reset, or temporary cool-down (`IR0-IR2`) | stay at `V0-V1 / R0-R1`; do not create new learner-bound memory just because the learner is struggling |
| teacher-owned recovery (`IR3`) | allow `RP1` only: usually `V2 / R1`, occasionally the coolest truthful `V3 / R1-R2` when one named owner must act |
| separate integrity, safeguarding, rights, or formal progression trigger | the separate `V3-V4 / R2-R3` rail governs; do not pretend it is still ordinary study-support logging |

The archive's practical rule is: **ordinary dependence handling should not, by itself, push a study
companion above the coolest truthful packet-and-signal shape.**

## What institutions should publish

For any recurring official study companion, tutoring surface, or feedback assistant that uses
teacher-owned recovery, publish only six fields:

1. whether `RP1` packets exist at all;
2. the fields those packets may contain;
3. who owns them and when they expire;
4. which aggregate signal families (`AG1-AG5` or local equivalent) are used;
5. the minimum-cell / de-identification rule for aggregate reporting;
6. which downstream uses are explicitly prohibited.

That is enough to keep recovery legible without requiring institutions to publish a telemetry
manual.

## What counted as a real archive gain

The archive now does more than say “teacher-owned recovery should inspect a small packet.” It now
distinguishes three things that were previously too easy to blur:

- **ordinary AI-owned resets and cool-downs**, which should not automatically create durable
  learner-bound records;
- **temporary recovery packets**, which are permitted only to the extent needed for one accountable
  adult to reset the support path;
- **aggregate dependence signals**, which may improve the service only at a de-identified or
  minimum-cell level.

That is a real operating gain because it blocks a predictable drift: the institution notices
dependence, then solves the wrong problem by recording more and more about the learner.

## Current archive bet

The archive's current best guess is that **a short-lived recovery-packet rule plus coarse aggregate
dependence signals** will preserve both learning and legitimacy better than either of the two easier
extremes:

- keeping no structured recovery evidence at all, so repeated failure remains invisible until a
  worse case opens;
- or capturing broad learner histories and cross-function profiles in the name of support.

That claim is now canon, but still live. The later recovery line now reaches through child branches,
treatment mini-codes, authority-family defaults, a portable owner-facing packet floor, and a
departure-publication-and-ratchet rule; the next problem is when repaired packet defaults have
genuinely recovered and may harden again rather than living forever under stale departure evidence.
