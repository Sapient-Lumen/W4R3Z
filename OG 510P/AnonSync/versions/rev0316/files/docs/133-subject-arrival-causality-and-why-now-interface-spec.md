# Subject arrival causality and why-now interface spec

## Purpose

The archive now has:

- publication matrices
- publication delta preview
- mutation ledgers
- member-policy cards
- member-policy impact proof
- effective member-policy explanation

What still remained under-specified was the operator question that most often turns into folklore in sync products:

> why did this particular subject show up for this particular member now, with this role, this path suggestion, and this byte posture?

This document defines the **subject arrival causality** surface.
It is the per-cell counterpart to `132-effective-member-policy-explanation-and-provenance-trace-interface-spec.md`.
Where `132` explains a member's current standing defaults, this spec explains one concrete `(subject, member)` outcome.

## Core rule

For every visible `(subject, member)` cell, the product must be able to render one explicit **arrival causality explanation** object that answers all of the following in one place:

1. which publication act or standing template made the subject eligible for this member
2. which member-policy and subject-policy values won at the moment of arrival
3. whether approval reuse, explicit review, or fresh claim caused the subject to become live here
4. why the current role, path suggestion, and materialization posture won
5. which plausible alternative explanations did **not** win

The operator should not need to infer arrival semantics from the fact that something appeared in an inbox, landed at a path, or later behaved a certain way.

## Why this needs its own spec

Current Resilio docs still teach too much through later consequences:

- linking devices makes all folders available across the linked set
- synchronization mode governs how newly added folders arrive
- default folder location decides where automatically created arrivals go when a member is in `Selective Sync` or `Synced`
- duplicate-folder recovery teaches operators to disconnect and reconnect deliberately if a default path created the wrong target

That works as support knowledge.
It is not good enough for AnonSync.
AnonSync should let the operator click one cell and ask `why this member, why now, why this role, why this path, why this byte posture?`

## Public objects

### Arrival causality explanation

A current-state explanation object for one `(subject, member)` cell.

Suggested fields:

- `arrival_causality_explanation_id`
- `subject_ref`
- `member_ref`
- `generated_at`
- `current_cell_state`
- `eligibility_source_ref`
- `claim_or_adoption_ref` nullable
- `winning_role_cause_ref`
- `winning_path_cause_ref` nullable
- `winning_materialization_cause_ref` nullable
- `non_winning_cause_refs[]`
- `freshness_class`

### Arrival causality step

One leg in the explanation chain.

Suggested fields:

- `arrival_causality_step_id`
- `step_kind` (`publication-act`, `standing-template`, `member-override`, `subject-exception`, `approval-reuse`, `fresh-approval`, `claim-review`, `role-decision`, `path-bind`, `materialization-decision`, `temporary-freeze`, `temporary-lease`)
- `source_ref`
- `effective_summary`
- `selected` boolean
- `selection_reason`
- `non_selection_reason` nullable

### Arrival counterfactual row

A short explanation of a nearby path the system did not take.

Suggested fields:

- `arrival_counterfactual_row_id`
- `counterfactual_kind` (`not-published`, `published-but-unclaimed`, `role-would-have-been-lower`, `would-have-staged-only`, `would-have-bound-elsewhere`, `blocked-by-freeze`, `needs-fresh-approval`)
- `counterfactual_summary`
- `why_not`

### Arrival explanation receipt

A durable exportable proof of the explanation rendered at one time.

Suggested fields:

- `arrival_explanation_receipt_id`
- `arrival_causality_explanation_ref`
- `actor_ref`
- `created_at`
- `evidence_hash`

## Fixed inspection order

Every arrival-causality surface should preserve this order:

1. **Cell summary now**
2. **Eligibility source**
3. **Claim / approval / adoption path**
4. **Winning role, path, and byte posture causes**
5. **Counterfactuals that did not win**
6. **Recent mutations that would change this answer**
7. **Next honest actions**

### 1) Cell summary now

This section should answer in plain language:

- subject
- member
- current visibility state
- current role
- current path or staged-only state
- current materialization posture
- freshness of the explanation

### 2) Eligibility source

This section should say exactly how the subject became eligible for this member, for example:

- explicit per-subject publication
- subject-family publication template
- inherited constellation publication rule
- successor carry-forward publication

If multiple publication candidates existed, the winning one should be marked and the losing ones should remain inspectable.

### 3) Claim / approval / adoption path

This section should say whether the subject became live here by:

- fresh approval and claim
- prior approval reuse within policy
- standing low-risk auto-stage only
- explicit local adoption from inbox
- successor or continuity carry-forward

The point is to make `showed up here` and `was honestly accepted here` visibly different when they are different.

### 4) Winning role, path, and byte posture causes

This section should answer:

- why the member has observer versus writer versus approval-seat versus some other role now
- why the subject is staged, selective, or fully materialized
- why the current path was suggested or bound
- whether any temporary modifier or incident posture changed the ordinary answer

### 5) Counterfactuals that did not win

A strong explanation also shows nearby alternatives that did not happen.
Typical rows include:

- `Not published under current template`
- `Would have staged only, but explicit claim upgraded it`
- `Would have bound under root family B, but subject exception won`
- `Would have required fresh approval, but remembered approval matched and remained in scope`

### 6) Recent mutations that would change this answer

If today's explanation depends on a recent policy edit, publication mutation, lease, or freeze, the surface should keep that adjacent instead of making the operator hunt through history.

### 7) Next honest actions

Only actions supported by the current evidence should appear, for example:

- `Open publication source`
- `Open claim receipt`
- `Open member policy explanation`
- `Compare with prior causality`
- `Export explanation receipt`

## Public rules

### Rule 1 — one visible cell must always be explainable

If the product can render a cell in the matrix, it must be able to explain why that cell exists.

### Rule 2 — path and byte posture are semantic outcomes, not cosmetic details

The explanation is incomplete if it names only publication and role but not why the current bind/materialization outcome won.

### Rule 3 — counterfactuals stay adjacent

Operators should not have to run separate simulations just to understand why the system did not choose another obvious outcome.

### Rule 4 — explanation may mention freshness limits but not hide behind them

If the explanation is stale or degraded, the product may mark that clearly, but it should still render the last known winning chain and what would need recomputation.

### Rule 5 — arrival explanation does not replace mutation proof

This surface explains one cell.
It does not replace broader publication delta preview or member-policy impact proof for edits that would affect many cells.

## Dense row contract

A dense causality row should preserve these labels in this order:

- `Cell`
- `Published by`
- `Accepted by`
- `Role because`
- `Path because`
- `Bytes because`
- `Why not otherwise`

## Acceptance test

This surface is good enough when a cautious operator can click any one `(subject, member)` cell and answer all of the following without leaving the page:

- why this subject is eligible for this member at all
- whether it became live through fresh approval, reuse, or local claim
- why this exact role won
- why this exact path or staged-only posture won
- why this exact byte posture won
- which nearby explanations did not win and why
