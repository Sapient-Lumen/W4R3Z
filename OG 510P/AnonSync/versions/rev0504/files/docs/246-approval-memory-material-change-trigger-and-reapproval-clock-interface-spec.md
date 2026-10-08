# Approval-memory material-change trigger and reapproval-clock interface spec

## Purpose

The archive already separates first approval from later remembered matches, gives remembered approval a freshness class, and traces the lineage node that authorized a later match.
What still remained too easy to blur was a harder question:

> when the trust basis itself changes materially, why should remembered approval continue to lower friction at all unless that change is explicitly re-reviewed?

This document turns that question into one explicit interface contract.
It is the event-based companion to `106-approval-memory-freshness-cooling-and-touch-renewal-interface-spec.md`, the lineage-trigger companion to `107-approval-memory-lineage-and-authorization-trace-interface-spec.md`, and the guarded-match companion to `97-standing-approval-memory-and-matched-arrival-guardrail-interface-spec.md`.

## Core rule

Remembered approval may age gradually, but it may also be invalidated abruptly by a **material trust-basis change**.

The product is not fully inspectable until it can answer six questions in one place:

1. what trust basis the remembered approval originally depended on
2. what material trigger changed since that approval or its last renewal
3. whether reuse is now still allowed, guarded, frozen, or blocked pending reapproval
4. when a periodic reapproval clock would have required review even without the trigger
5. which reviewed outcomes are available now (`reapprove-same-scope`, `reapprove-narrowed`, `freeze-until-fresh`, `revoke`, or `mark-non-material-with-receipt`)
6. which receipt later proves whether the product truly reapproved the memory or merely kept history visible while stopping reuse

If a remembered approval can survive a changed identity epoch, linked-device set, ownership domain, role horizon, or governing policy without one first-class explanation of why, the product is still depending on folklore.

## Why this needs its own spec

Freshness alone is not enough.
A memory can be recent and still no longer deserve reuse because something foundational changed.
Examples include:

- peer identity epoch rotated
- certificate or control-channel identity changed
- linked-device set widened materially
- governing role or share class widened
- local policy narrowed or route posture changed in a way the original approval never reviewed
- original proof bundle is now contradicted or incomplete
- reapproval clock elapsed even though nobody reported a trigger

Cross-reading the companion datacubes sharpened this missing contract:
old approval should not keep floating forward just because no one manually revoked it.
The burden of proof should move to the operator to show that the live trust basis still matches the remembered authorization.

## Public objects

### Approval-memory material-change row

A compact read object describing one remembered approval and one candidate trigger that may reopen review.

Suggested fields:

- `approval_memory_material_change_row_id`
- `approval_memory_ref`
- `current_lineage_head_ref`
- `trigger_kind` (`identity-epoch-changed`, `linked-device-set-changed`, `scope-widened`, `governed-horizon-changed`, `policy-basis-narrowed`, `supporting-proof-contradicted`, `periodic-clock-due`, `other`)
- `trigger_strength` (`advisory`, `guarded`, `blocking`, `unknown`)
- `trigger_summary`
- `reuse_posture_now` (`still-allowed`, `guarded`, `frozen-pending-reapproval`, `revoked`, `unknown`)
- `observed_at`
- `supporting_receipt_refs[]`

### Approval-memory reapproval clock

A read object describing the standing periodic review expectation for one approval-memory family.

Suggested fields:

- `approval_memory_reapproval_clock_id`
- `approval_memory_ref`
- `review_interval_class` (`none`, `low`, `normal`, `high`, `strict`)
- `last_reapproved_at` nullable
- `next_due_at` nullable
- `clock_state` (`not-due`, `due-soon`, `due`, `overdue`, `suspended`, `unknown`)
- `clock_basis`

### Approval-memory reapproval review

A prepared review object for deciding how one material trigger should change remembered reuse.

Suggested fields:

- `approval_memory_reapproval_review_id`
- `approval_memory_ref`
- `trigger_refs[]`
- `clock_ref` nullable
- `current_scope_summary`
- `requested_outcome` (`reapprove-same-scope`, `reapprove-narrowed`, `freeze-until-fresh`, `revoke-memory`, `mark-non-material-with-receipt`)
- `changed_basis_summary`
- `effect_summary`
- `non_effect_summary`
- `blockers[]`
- `receipt_promise`

### Approval-memory reapproval receipt

A durable object proving how one remembered approval responded to one material trigger or one due clock.

Suggested fields:

- `approval_memory_reapproval_receipt_id`
- `approval_memory_ref`
- `trigger_refs[]`
- `previous_head_ref`
- `result_head_ref` nullable
- `outcome`
- `reviewed_at`
- `next_due_at` nullable
- `proof_refs[]`

## Fixed inspection order

Every reapproval surface should preserve this order:

1. **Remembered approval and current head**
2. **What materially changed or became due**
3. **What reuse is still allowed now**
4. **Reapproval choices and scope outcomes**
5. **Counterfactual under no reapproval**
6. **Receipts and next review expectation**

### 1) Remembered approval and current head

This section should show:

- the approval-memory family
- current head node
- current scope summary
- current freshness class
- current linked seat / governed horizon posture

The operator must be able to answer: **what standing trust memory is being reopened?**

### 2) What materially changed or became due

This section should show:

- trigger kind and strength
- what fact changed
- when it changed or was observed
- whether a periodic clock is also due or overdue
- whether any proof is missing and forces `unknown`

The operator must be able to answer: **why is quiet reuse no longer trustworthy?**

### 3) What reuse is still allowed now

This section should show:

- whether later arrivals can still match as evidence only
- whether identity-only admit remains allowed
- whether claim-suggestion or any broader shortcut is frozen pending review
- whether current local claims or binds remain untouched despite reuse freeze

The operator must be able to answer: **what later convenience still survives right now, and what is already stopped?**

### 4) Reapproval choices and scope outcomes

This section should show:

- `Reapprove same scope`
- `Reapprove narrowed`
- `Freeze until fresh approval`
- `Revoke memory`
- `Mark non-material with receipt`

The operator must be able to answer: **what reviewed move resolves this trigger honestly?**

### 5) Counterfactual under no reapproval

This section should show:

- how the next matching arrival would be handled if the operator does nothing
- whether later matches would downgrade to evidence-only or fully fresh review
- whether the current head would remain visible but non-reusable
- which later user-visible warnings would recur until resolved

The operator must be able to answer: **what happens if I refuse to bless this change?**

### 6) Receipts and next review expectation

This section should show:

- the original approval receipt
- the head currently in force
- the trigger evidence
- the new reapproval receipt, if any
- the next periodic due time or why none exists

The operator must be able to answer: **what later proof shows whether trust was reapproved, narrowed, frozen, or revoked?**

## Trigger rules

### Rule 1 — material change reopens reuse before it silently reopens trust

A trigger may leave history visible, but it must not silently preserve broad convenience reuse.

### Rule 2 — periodic clocks catch unreported drift

Even with no declared trigger, remembered approval that remains consequential should be reviewable on a periodic clock.

### Rule 3 — `non-material` still needs a receipt

If the operator decides a trigger does not justify changed reuse, the product should record that reviewed judgment rather than silently continuing.

### Rule 4 — reuse freeze is narrower than revocation

The system should distinguish between `keep history but stop lower-friction reuse` and `revoke remembered approval entirely`.

### Rule 5 — current local state is not rewritten by trust review alone

Reapproval review must not by itself:

- claim a subject
- bind a path
- materialize bytes
- widen unrelated subject rights

## Dense row contract

A dense row should preserve these labels in this order:

- `Memory`
- `Trigger`
- `Reuse now`
- `Clock`
- `Next action`
- `State`

## CLI contract

Minimal commands:

```text
anonsync approval reapproval list --seat self --scope remembered
anonsync approval reapproval show --memory apm_01J...
anonsync approval reapproval prepare --memory apm_01J... --outcome reapprove-narrowed --plan
anonsync approval reapproval apply --review aprr_01J...
```

## Acceptance test

This surface is good enough when a cautious operator can answer all of the following without log archaeology:

- what changed in the basis for remembered trust
- whether quiet reuse is now still allowed, guarded, or frozen
- whether periodic reapproval was also due
- what reviewed outcome would preserve, narrow, or stop reuse
- what later receipt proves the answer
