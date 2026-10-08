# Convergence campaign contract sheet page: debt cohort, target end state, and safety fences interface spec

## Purpose

After the archive learned how to represent each changed return as explicit parity debt, it still needed one ordinary page for the next operator question:

> which debts belong in this settlement effort, what end state do we want for each, and what safety fences stop us from turning cleanup into fresh damage?

## Core decision

AnonSync must expose one first-class **Convergence campaign contract sheet** whenever more than one active return-delta object is being settled under one operator goal.

## Fixed page order

1. **Campaign header**
2. **Target-claim card**
3. **Cohort membership card**
4. **Per-subject routing card**
5. **Safety fences card**
6. **Decision sentence**

### 1) Campaign header

Show:

- convergence campaign id
- linked baseline / profile / policy family
- linked case / control / return-delta ids in scope
- campaign owner
- created time
- next decision gate
- current campaign status
- highest safe claim for covered scope

Supported `current_campaign_status` values:

- `drafting`
- `awaiting-approval`
- `wave-active`
- `partially-settled`
- `blocked-by-stragglers`
- `settled-for-bounded-scope`
- `reopened`
- `retired`

Hard rule:

A settlement effort may not be represented only as a pile of independent tasks once it is being judged as one success story.

### 2) Target-claim card

This card states what stronger sentence the campaign is trying to earn back.
Required rows:

- intended post-campaign sentence
- current weaker still-safe sentence
- target scope
- target settlement class
- proof needed before claim upgrade
- blocking subject classes

Supported `target_settlement_class` values:

- `exact-baseline-restored`
- `approved-successor-baseline`
- `mixed-but-bounded`
- `narrowed-stable-subset`
- `debt-reduction-only`

Hard rule:

The page must say whether the goal is exact restoration or accepted successor settlement.
Those may not share one generic success label.

### 3) Cohort membership card

This card defines what is in scope.
Required rows:

- total candidate subjects
- selected subjects in campaign
- excluded subjects
- inclusion rule
- shared risk signature
- shared proof assumption if any

Supported `inclusion_rule` values:

- `same-baseline-family`
- `same-return-delta-class`
- `same-failed-rearm-shape`
- `same-path-drift-family`
- `same-mode-drift-family`
- `mixed-manual-selection`

Hard rule:

Every excluded subject must remain visible.
No silent scope trimming.

### 4) Per-subject routing card

This card states where each subject is headed.
Required columns:

- subject id
- current debt class
- chosen route
- owner
- blocking condition
- next proof or action

Supported `chosen_route` values:

- `exact-restore`
- `promote-successor`
- `keep-temporary-with-expiry`
- `split-out-and-narrow-claim`
- `reopen-linked-case`
- `drop-from-this-wave`

Hard rule:

Every subject gets one explicit route.
`will figure it out during cleanup` is not a valid route.

### 5) Safety fences card

This card publishes the dangerous edges of the wave.
Required rows:

- destructive action classes allowed
- destructive action classes forbidden
- folder-not-empty / merge risk present?
- path fork risk present?
- rights drift risk present?
- abort threshold

Supported `abort_threshold` values:

- `first-unexpected-overwrite-risk`
- `first-unapproved-path-fork`
- `first-unplanned-claim-downgrade`
- `more-than-n-stragglers`
- `operator-manual-stop-only`

Hard rule:

A settlement wave may not begin with ambiguous destructive boundaries.

### 6) Decision sentence

Format:

> `This campaign is settling [selected subjects] toward [target settlement class]. It is safe to say [current weaker still-safe sentence] for [target scope]. It is not yet safe to say [intended post-campaign sentence] until [blocking subject classes / missing proof] are cleared.`

## Required interactions

### A) `Shape cohort`

Builds or changes the selected subject set.

### B) `Assign route`

Applies one explicit route to each subject.

### C) `Arm safety fences`

Records campaign-level abort logic before execution.

### D) `Freeze claim`

Locks the current claim ceiling until enough settlement proof arrives.

## Explicit anti-goals

Do not:

- present a many-subject cleanup as generic maintenance
- allow hidden exclusions
- allow success language before routes are explicit
- allow average progress to erase uncovered subjects

## Why this page exists

Because once many tolerated deltas exist at the same time, the product needs one honest place that says what exactly this wave is trying to settle, who is in, who is out, and what must not be risked while doing it.
