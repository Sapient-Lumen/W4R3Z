# Member policy future simulation and example-subject preview interface spec

## Purpose

The archive now has:

- a draft-first member-policy editor
- an impact proof that classifies current-cell blast radius
- an explanation object for current effective defaults

What still remained under-specified was the forward-looking operator question:

> if I apply this member-policy draft, what kinds of future arrivals will behave differently, and can I see those differences before I commit?

This document defines the **future-arrival simulation** surface for member-policy drafts.
It is the forward-looking companion to `131-member-policy-impact-classification-and-touched-subject-review-interface-spec.md`.
Where `131` proves what happens to current cells, this spec previews what would happen to future arrivals.

## Core rule

Every semantic member-policy draft must be able to render one explicit **future-arrival simulation sheet** before apply.
The sheet must show representative future subject classes and compare:

- current future outcome
- proposed future outcome
- which policy field causes the change
- whether the change is safe, widening, narrowing, or only presentational

The operator should not need to imagine future arrival behavior from raw defaults, path roots, or mode names.

## Why this needs its own spec

Current Resilio docs still explain future behavior through standing defaults:

- synchronization mode selected when linking applies to all newly added folders
- Sync Preferences choose the default folder location when the member is in `Selective Sync` or `Synced`
- duplicate-folder guidance teaches the operator to reason backward from what later arrived where

That is exactly what AnonSync should avoid.
Instead of asking the operator to mentally simulate future arrivals from defaults, AnonSync should simulate the future explicitly.

## Public objects

### Future-arrival simulation sheet

A preview object for one member-policy draft.

Suggested fields:

- `future_arrival_simulation_sheet_id`
- `member_policy_edit_plan_ref`
- `member_ref`
- `generated_at`
- `scenario_rows[]`
- `widening_change_count`
- `narrowing_change_count`
- `presentation_only_change_count`
- `freshness_class`

### Future scenario row

One representative future-arrival case.

Suggested fields:

- `future_scenario_row_id`
- `scenario_class` (`ordinary-personal`, `sensitive-personal`, `archival`, `media-large`, `incoming-offer-low-risk`, `incoming-offer-high-risk`, `approval-seat-case`, `path-sensitive-case`)
- `current_outcome_summary`
- `proposed_outcome_summary`
- `winning_field_deltas[]`
- `change_class` (`widening`, `narrowing`, `lateral`, `presentation-only`)
- `needs_extra_review` boolean

### Winning field delta

One field whose changed value would alter the simulated future outcome.

Suggested fields:

- `winning_field_delta_id`
- `field_path`
- `current_effective_value`
- `proposed_effective_value`
- `effect_summary`

### Future simulation receipt

A durable exportable record of the simulation rendered before apply.

Suggested fields:

- `future_simulation_receipt_id`
- `future_arrival_simulation_sheet_ref`
- `actor_ref`
- `created_at`
- `evidence_hash`

## Fixed inspection order

Every future-simulation surface should preserve this order:

1. **Draft summary**
2. **Current-cell impact classification**
3. **Representative future scenarios**
4. **Widening and narrowing callouts**
5. **Non-effects and unchanged scenarios**
6. **Next honest review boundary**

### 1) Draft summary

This section should restate:

- which member is being edited
- which fields changed
- whether the draft is durable or temporary
- freshness of the simulation baseline

### 2) Current-cell impact classification

This section should keep the result from `131` adjacent.
The operator should see immediately whether the draft is:

- future-only proven
- mixed current and future
- current-cells affected
- ambiguous and stale

Future simulation should not hide the fact that a draft also touches current cells.

### 3) Representative future scenarios

This section is the center of the sheet.
It should show a curated set of example subject classes and, for each one:

- what the member would receive today
- what the member would receive after apply
- which field values changed that result
- whether the result is safer, wider, narrower, or merely cosmetically different

Typical examples include:

- ordinary note or document
- large media directory where path choice matters
- archival item that should stay observer/staged
- high-risk incoming offer that should require fresh review
- trusted low-risk subject that may auto-stage only

### 4) Widening and narrowing callouts

Any scenario that would widen authority, publication visibility, or automatic materialization must appear in a dedicated callout section.
Narrowing changes should also be collected so the operator sees what convenience will be lost.

### 5) Non-effects and unchanged scenarios

The product should also prove what representative scenarios do **not** change.
This prevents the simulation from becoming a theater of only changed examples.

### 6) Next honest review boundary

Examples:

- `Apply future-only draft`
- `Open touched current subjects`
- `Resolve widening review`
- `Recompute simulation`
- `Export simulation receipt`

## Public rules

### Rule 1 — future simulation is mandatory for semantic drafts

If a member-policy draft can change the way future arrivals behave, the product must be able to simulate that behavior before apply.

### Rule 2 — current-cell proof and future simulation stay adjacent

Operators must not be forced to choose between learning what changes now and learning what changes later.
Both truths belong in the same review flow.

### Rule 3 — scenario classes are explicit, not hidden heuristics

If the product chooses representative scenarios automatically, it must name the scenario classes so the operator can see what was tested.

### Rule 4 — widening changes must be visually louder than convenience gains

A policy change that makes future arrivals more automatic, more writable, or more eagerly materialized is a higher-signal change than one that merely changes path labels or ordering.

### Rule 5 — simulations do not claim certainty beyond their baseline

The surface may simulate future outcomes from the current known policy graph.
It must not pretend to know future subjects that do not yet exist.
The honesty contract is: `given a future arrival of this class under the current graph, this is what would happen`.

## Dense row contract

A dense future-scenario row should preserve these labels in this order:

- `Scenario`
- `Current future outcome`
- `Proposed future outcome`
- `Changed because`
- `Risk class`
- `Review`

## Acceptance test

This surface is good enough when a cautious operator can review a member-policy draft and answer all of the following before apply:

- whether the draft changes only future behavior or also current cells
- what several representative future arrivals would do today versus after apply
- which field deltas cause those changes
- which changes widen, narrow, or merely restate behavior
- which representative scenarios remain unchanged
