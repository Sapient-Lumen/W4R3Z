# Member policy impact classification and touched-subject review interface spec

## Purpose

The archive now has:

- a member policy card that explains future defaults
- a draft-first member-policy editor with precedence ladders
- a publication delta preview for explicit publication changes

What still remained under-specified was the truth boundary between those surfaces:

> when a member-policy edit claims to be `future only`, how does the product prove that honestly, and when it is not future-only, how does it show the exact currently affected subjects before commit?

This document defines the impact-classification and touched-subject review surface for member-policy edits.
It sits between `130-member-policy-editor-and-precedence-ladder-interface-spec.md` and `127-publication-delta-preview-and-counterfactual-review-interface-spec.md`.

## Core rule

Every semantic member-policy edit plan must resolve to one explicit **impact classification** before apply:

- `future-only-proven`
- `current-cells-affected`
- `mixed-current-and-future`
- `ambiguous-needs-recompute`
- `blocked-by-precedence-conflict`

The product may not let a member-policy edit commit on the basis of `this should only affect future arrivals` unless it can render the evidence for that claim.

If current `(subject, member)` cells would be touched, the product must render them as first-class review material.
It may summarize them compactly, but it may not hide them behind a generic `this may affect existing items` warning.

## Why this needs its own spec

Current Resilio docs still teach important consequences of default-location and arrival-mode choices through later outcomes:

- linked-device synchronization modes govern how new folders arrive on a member
- manual custom placement still often depends on putting a target into `Disconnected` mode first
- reconnect guidance still teaches operators to catch duplicate-path outcomes and choose an existing target deliberately

That is workable as support knowledge.
It is not strong enough as an interface contract.
AnonSync should instead prove whether a policy edit is truly future-only, and if not, which already-known subjects change and why.

## Public objects

### Member policy impact proof

A review object that classifies the real blast radius of one member-policy edit plan.

Suggested fields:

- `member_policy_impact_proof_id`
- `member_policy_edit_plan_ref`
- `impact_classification`
- `changed_current_cell_count`
- `future_only_subject_class_count`
- `ambiguous_subject_count`
- `touched_subject_bucket_refs[]`
- `generated_at`
- `stale_after`

### Touched subject bucket

A compact grouping of current subjects that would change for the edited member.

Suggested fields:

- `touched_subject_bucket_id`
- `bucket_reason` (`role-change`, `arrival-default-change`, `path-suggestion-change`, `exception-removal`, `temporary-lease-conflict`, `publication-template-expansion`, `publication-template-narrowing`)
- `subject_count`
- `example_subject_refs[]`
- `current_outcome_summary`
- `proposed_outcome_summary`
- `requires_full_delta_preview` boolean

### Untouched-proof summary

A machine-checkable summary of why the product believes untouched subjects truly remain untouched.

Suggested fields:

- `untouched_proof_summary_id`
- `member_policy_edit_plan_ref`
- `tested_subject_scope_summary`
- `proven_untouched_count`
- `excluded_subject_scope_summary`
- `exclusion_reasons[]`
- `confidence_class` (`full`, `sampled`, `degraded`)

### Impact proof receipt

A durable record that one impact proof was reviewed before apply.

Suggested fields:

- `impact_proof_receipt_id`
- `member_policy_impact_proof_ref`
- `actor_ref`
- `reviewed_at`
- `review_hash`
- `followed_by_delta_preview_ref` nullable

## Fixed inspection order

Every impact-proof surface should preserve this order:

1. **Edit being evaluated**
2. **Impact classification**
3. **Touched current subjects**
4. **Untouched proof and exclusions**
5. **Future-only consequences**
6. **Next honest review boundary**

### 1) Edit being evaluated

This section should restate:

- which member is being edited
- which policy fields changed
- whether the operator asked for compact or full review
- whether the proof was computed against a fresh or stale baseline

### 2) Impact classification

This section should state one clear verdict, for example:

- `Future only proven — zero current subject/member cells change`
- `Current cells affected — 14 existing subject/member cells would change`
- `Mixed — 14 current cells change and future arrivals would also differ`
- `Ambiguous — recompute required because the tested baseline drifted`

The verdict must not be phrased as product confidence theater.
It should directly answer whether current state would change.

### 3) Touched current subjects

If any current cells change, the surface must show them in grouped form first and expandable subject rows second.
Each group should preserve:

- reason for touch
- current outcome
- proposed outcome
- whether the touch changes publication, role, arrival posture, or only suggestion text
- whether a fuller publication delta preview must open next

Example row labels:

- `Reason`
- `Current`
- `Proposed`
- `Subjects`
- `Next`

### 4) Untouched proof and exclusions

A future-only claim is only honest when the product can also say what it checked and what it did not check.
This section must show:

- tested subject scope
- proven untouched count
- exclusions such as `offline-only evidence`, `degraded cache`, or `not yet recomputed after newer exception`
- whether the claim is `full`, `sampled`, or `degraded`

If confidence is degraded, compact apply must be blocked.

### 5) Future-only consequences

Even when zero current cells change, the product must still show representative future-arrival differences.
Examples:

- a new personal document would now stage under a different default root family
- a new high-risk offer would now stop at observer instead of writer
- an archival subject would now inherit a different arrival template

### 6) Next honest review boundary

The surface must end with the correct next action, not a generic apply button.
Examples:

- `Apply future-only edit`
- `Open full publication delta preview`
- `Recompute impact proof`
- `Resolve precedence conflict`
- `Export impact receipt`

## Compact versus full review

A compact impact sheet may be used only when all of the following are true:

- impact classification is `future-only-proven`
- untouched-proof confidence is `full`
- zero current cells change
- no conflict flags or drift flags exist

Otherwise the operator must be routed to the full impact review, and when current cells change, onward to the publication delta preview.

## Public rules

### Rule 1 — `future only` is a proved verdict, not a guess

The product may not use `future only` as shorthand for `we think probably only future arrivals are affected`.

### Rule 2 — touched current subjects are first-class review material

Affected current subjects may be grouped and sampled first, but they may not be hidden behind a collapsible footnote.

### Rule 3 — untouched claims must name exclusions

If any class of subject was not checked or only partially checked, the proof must say so explicitly.

### Rule 4 — path suggestion changes still count when they alter future binds materially

A change that leaves role unchanged but materially changes expected future path/bind posture is still a semantic effect and must be reviewed.

### Rule 5 — stale proofs do not silently apply

If later edits, leases, or exceptions drift the baseline, the impact proof must become stale and compact apply must stop.

## Acceptance test

This surface is good enough when a cautious operator can answer all of the following without reconstructing hidden semantics:

- is this really future-only, or is that merely the operator's intention
- if current state changes, how many current subjects are touched and why
- what was actually checked before making the untouched claim
- whether a fuller publication delta review must happen next
- what receipt will later prove that this impact review happened before apply
