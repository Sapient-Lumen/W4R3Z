# Replay cost review page: edit shape, hash availability, and network-vs-CPU tradeoff interface spec

## Purpose

Review a pending policy change, workload choice, or subject mutation that may alter replay cost.
The page answers:

> if I commit this change, will future edits replay by changed pieces, by full resend, or by a stronger diff lane, and what exactly am I trading between network cost and local compute?

## Review triggers

Open this page when any of the following happen:

- enabling or disabling differential replay
- changing hash-retention or lazy-hash policy
- moving a subject to a slower or faster storage class
- changing workload profile for large mutable files
- importing a seat/job whose replay class is weaker than local defaults
- choosing a profile optimized for WAN savings vs local CPU savings

## Required sections

### 1) Proposed replay delta

Show current vs proposed:

- current replay class
- proposed replay class
- strongest likely fallback under adverse edit shape
- whether the change is stronger, weaker, or mixed

### 2) Why the class changes

State the winning reasons:

- policy flip
- edition/runtime difference
- changed hash-retention basis
- changed storage/disk profile
- missing rolling/diff lane
- subject moved to a seat with weaker replay support

### 3) Edit-shape examples

The review must show concrete examples, not just theory:

- `append 10 MB to end of 40 GB file`
- `modify bytes in place inside existing block range`
- `insert bytes near beginning and shift later offsets`
- `rename only`

For each example, show expected replay class and confidence.

### 4) Cost tradeoff

Always render a three-column forecast:

| Axis | Current | Proposed |
| --- | --- | --- |
| Network replay | low / mixed / high | low / mixed / high |
| Local CPU/disk recheck | low / mixed / high | low / mixed / high |
| Whole-resend risk after shift | low / mixed / high | low / mixed / high |

### 5) Unsafe shorthand rewrite

Ban vague summaries like:

- `better performance`
- `faster sync`
- `more efficient`

Replace them with sentences like:

- `This change saves local CPU by accepting more full-file resend.`
- `This change spends more local hash work to reduce network replay.`
- `This change does not remove whole-resend risk for piece-shifting edits.`

### 6) Commit actions

- `Commit proposed replay policy`
- `Keep current policy`
- `Open replay evidence`
- `Narrow to selected subject class`

## Receipt obligations

A commit from this page must later preserve:

- current and proposed replay class
- edit-shape examples shown
- dominant reason for class change
- network-vs-local-cost forecast
- strongest unavailable class

## Data model

- `replay_cost_review_id`
- `subject_or_policy_target_id`
- `current_replay_class`
- `proposed_replay_class`
- `fallback_class_if_shifted`
- `cause[]`
- `example_forecasts[]`
- `network_cost_delta`
- `local_cost_delta`
- `whole_resend_risk_delta`
- `stronger_unavailable_class`
- `commit_scope`
- `receipt_ref`

## Failure this page prevents

Without this review, a product quietly turns `optimize this profile` or `use incremental sync` into an uninspected bet about edit shape, hash availability, and who pays the cost — disk/CPU now or network later.

AnonSync should make that trade explicit before commit.
