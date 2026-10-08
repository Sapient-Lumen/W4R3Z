# Intervention attempt receipt and post-action recompute interface spec

## Purpose

The archive now has:

- convergence windows
- wait-vs-intervene decision sheets
- structured evidence bundles with disambiguation ladders

What still remained under-specified was the action seam after a recommendation is made.
Even if the product knows the strongest next move, it still needs one honest contract for performing that move without collapsing back into ritual retrying, hidden collateral edits, or memory-based troubleshooting.

This document defines the interface contract for a first-class **intervention attempt** object, its receipt, and its mandatory **post-action recompute**.

## Core rule

Any non-trivial intervention against an unresolved convergence gap must be recordable as one explicit attempt object that:

1. states the chosen action and its exact scope
2. records the evidence snapshot that justified it
3. names the collateral changes that are forbidden during the attempt
4. captures the outcome artifacts
5. forces a fresh recompute of the convergence verdict afterward

The product must never treat intervention as a vague side quest.
It is part of the main state model.

## Why this needs its own spec

Current Resilio support guidance is often practical, but operators still learn many moves as folklore:

- retrying after reconnect
- changing a mode because a path choice was desired
- checking trackers, ports, relay, or source peers in scattered places
- collecting debug logs or even external network-test results when evidence remains ambiguous

That is survivable support material.
It is not the contract AnonSync wants.
AnonSync should make every intervention bounded, receipted, and recomputed so a later operator can see what was attempted and whether it actually changed the verdict.

## Public objects

### Intervention attempt

A durable object representing one bounded action taken against one unresolved gap.

Suggested fields:

- `intervention_attempt_id`
- `convergence_window_ref`
- `evidence_bundle_ref` nullable
- `action_kind` (`wait`, `re-announce`, `refresh-route`, `refresh-source`, `refresh-local-prerequisite`, `revise-policy`, `supersession-close`)
- `target_scope` (`cell`, `subject`, `member`, `policy-draft`, `announcement-channel`)
- `target_refs[]`
- `justifying_decision_receipt_ref`
- `started_at`
- `completed_at` nullable
- `outcome_class` (`changed-verdict`, `new-evidence-only`, `no-material-change`, `blocked-attempt`, `superseded-during-attempt`)

### Intervention precondition row

One condition that must hold before the attempt proceeds.

Suggested fields:

- `intervention_precondition_row_id`
- `kind` (`scope-confirmed`, `fresh-enough-evidence`, `required-seat-held`, `local-review-open`, `policy-draft-ready`, `forbidden-collateral-change-accepted`)
- `state` (`satisfied`, `missing`, `stale`, `blocked`)
- `summary`

### Intervention step receipt row

One material sub-step or artifact of the attempt.

Suggested fields:

- `intervention_step_receipt_row_id`
- `step_kind`
- `status` (`performed`, `skipped`, `blocked`, `not-needed`)
- `artifact_refs[]`
- `summary`

### Post-action recompute receipt

A required after-action receipt comparing before and after truth.

Suggested fields:

- `post_action_recompute_receipt_id`
- `intervention_attempt_ref`
- `old_convergence_verdict`
- `new_convergence_verdict`
- `changed_hypothesis_order[]`
- `new_primary_uncertainty` nullable
- `next_recommended_action`
- `computed_at`

## Fixed inspection order

Every intervention attempt surface should preserve this order:

1. **Target gap and chosen action**
2. **Why this action was justified**
3. **Scope and forbidden collateral changes**
4. **Preconditions and live execution state**
5. **Outcome artifacts**
6. **Post-action recompute verdict**
7. **Next review boundary**

### 1) Target gap and chosen action

This section should state plainly:

- which unresolved gap is in scope
- which action was chosen
- whether the action is evidence refresh, publication refresh, local review completion, or policy revision

### 2) Why this action was justified

This section should cite the decision receipt or evidence bundle that made the action the strongest next move.
Examples:

- `re-announce chosen because announcement freshness was missing while route and source evidence remained strong`
- `refresh-source chosen because the primary uncertainty was no eligible source online`
- `revise-policy chosen because the pending target no longer matched the winning policy state`

### 3) Scope and forbidden collateral changes

This section is mandatory.
It should say exactly what the attempt may and may not change.
Examples of forbidden collateral changes:

- changing member-wide future defaults to fix one current cell
- rebinding a different path without explicit role/path review
- widening publication scope when the evidence problem is route-side only
- withdrawing and reissuing when the evidence problem is source availability only

### 4) Preconditions and live execution state

Examples:

- decision receipt still fresh enough
- required seat has authority to perform the action
- related draft exists and is approved where needed
- local review gate is open if the action includes member-side work

### 5) Outcome artifacts

Examples:

- new announcement receipt
- new liveness proof
- refreshed route report
- refreshed source-availability witness
- policy-mutation receipt
- local-review completion receipt

### 6) Post-action recompute verdict

This section compares before and after.
It should answer:

- did the convergence verdict change
- did only the evidence set improve
- did the primary uncertainty move elsewhere
- is the next recommendation the same or different

The recompute is mandatory even when the attempt appears to have succeeded.

### 7) Next review boundary

Examples:

- `Close attempt and return to convergence window`
- `Open new evidence bundle`
- `Open next recommended intervention`
- `Mark superseded and archive receipt`

## Public rules

### Rule 1 — every non-trivial intervention becomes a durable object

No meaningful convergence action should disappear into transient UI history.

### Rule 2 — attempts are bounded by declared scope

The product must not silently broaden an intervention from one cell to one member or one policy domain.

### Rule 3 — post-action recompute is mandatory

An intervention is not complete until the system recomputes the convergence verdict from fresh evidence.

### Rule 4 — repeated identical retries must stay legible

If the operator performs the same action again, the surface should show the prior attempt and whether it changed anything last time.

### Rule 5 — success means changed truth, not relief

An attempt is successful only insofar as it changes the evidence set, the verdict, or the recommended next action in a meaningful way.

### Rule 6 — blocked attempts are informative

A blocked intervention should still produce a receipt showing why it was blocked and which precondition failed.

## Dense row contract

A dense intervention row should preserve these labels in this order:

- `Gap`
- `Chosen action`
- `Scope`
- `Why justified`
- `Artifacts`
- `Verdict before→after`
- `Next action`

## Acceptance test

This surface is good enough when a cautious operator can answer all of the following from one attempt receipt:

- what action was taken and why
- what the action was explicitly allowed to touch
- which preconditions were satisfied or missing
- what artifacts the attempt produced
- whether the convergence verdict changed afterward
- what the next honest action became after recompute


## Relationship to nearby specs

`251-outside-action-follow-through-coverage-and-fix-claim-boundary-interface-spec.md` now sharpens the middle seam where one requested or observed step still is not enough to justify a whole-fix claim before recompute closes the story.
