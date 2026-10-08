# Decision portfolio contract sheet page: candidate set, urgency lanes, and attention budget interface spec

## Purpose

Once several decision charters are live at the same time, the operator still needs one page that answers:

> what exact candidate set are we prioritizing, what attention budget do we really have, and which lane does each item belong in right now?

## Core decision

AnonSync must expose one first-class **Decision portfolio contract sheet** whenever two or more live decision charters compete for attention, execution, or monitoring.

## Fixed page order

1. **Portfolio header**
2. **Candidate-set card**
3. **Priority-factors card**
4. **Attention-budget card**
5. **Lane-assignment card**
6. **Starvation-guard card**
7. **Dispatch sentence**

### 1) Portfolio header

Show:

- portfolio id
- owning operator or team
- portfolio scope
- current portfolio posture
- total live candidates
- number in `now`
- number in `watch`
- number nearing starvation
- current dispatch winner if one exists

Supported `portfolio_posture` values:

- `portfolio-opened`
- `candidate-scoring-in-progress`
- `lane-mapping-in-progress`
- `dispatch-ready`
- `watch-heavy`
- `capacity-blocked`
- `frozen`
- `superseded`

Hard rule:

The header may not imply healthy control merely because one winner exists.
If three items are starving in `watch`, the header must still show that pressure.

### 2) Candidate-set card

Required rows:

- candidate decision id
- candidate title
- current claim ceiling
- allowed next verb
- current harm if delayed
- current harm if done too early
- affected scope
- dependency or blocker note

Supported `candidate_class` values:

- `bounded-repair`
- `monitoring-posture`
- `supplement-ask`
- `heavy-capture`
- `publication-decision`
- `freeze-or-halt`
- `external-handoff`

Hard rule:

Every candidate must remain visible even if it loses dispatch.
Hidden losers are not allowed.

### 3) Priority-factors card

Required rows:

- urgency
- blast radius
- reversibility
- evidence freshness risk
- watch-starvation risk
- dependency pressure
- operator-cost or burden
- benefit of dispatch now
- cost of not choosing now

Supported `priority_factor_grade` values:

- `low`
- `moderate`
- `high`
- `critical`
- `unknown`

Hard rule:

The card may not collapse all pressure into one synthetic score without still showing factor-by-factor grades.

### 4) Attention-budget card

Required rows:

- available operator budget
- number of safe concurrent actions
- maximum heavy investigations allowed
- watch capacity
- frozen capacity classes
- reevaluation cadence

Supported `attention_budget_class` values:

- `one-major-action-only`
- `many-light-checks-few-actions`
- `watch-only-for-now`
- `heavy-capture-limited`
- `frozen-by-external-dependency`

Hard rule:

Attention budget must be explicit.
The product may not pretend all action-ready items can proceed simultaneously unless the budget says so.

### 5) Lane-assignment card

Render one row per candidate.
Required fields:

- assigned lane
- reason for lane choice
- what would promote it
- what would demote it
- maximum tolerated age in lane

Supported `portfolio_lane` values:

- `now`
- `next`
- `later`
- `watch`
- `hold`
- `frozen`
- `done-or-exited`

Hard rule:

`watch` and `hold` are not synonyms.
`watch` means active observation is still valuable.
`hold` means the portfolio is deliberately not spending attention there yet.

### 6) Starvation-guard card

Required rows:

- candidates nearing starvation
- why they are not already promoted
- maximum allowed silent age
- automatic promotion trigger
- automatic forced-review trigger

Supported `starvation_guard_posture` values:

- `healthy`
- `aging`
- `near-breach`
- `breached`
- `unknown-because-review-missed`

Hard rule:

A portfolio with any `breached` candidate may not describe itself as fully controlled.

### 7) Dispatch sentence

Render exactly two lines:

- **Dispatch now**
- **Most important held-or-watching item and why it is not going now**

Hard rule:

The second line must name one losing item explicitly.
A portfolio without a visible losing item is not telling the truth about prioritization.
