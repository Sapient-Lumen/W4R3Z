# Approval-seat roster, active-request split, and rerequest interface spec

## Purpose

The archive already keeps several approval truths separate:

- the current requested subject
- the acting seat that may speak
- the approval horizon and blast radius
- standing approval memory and later matched-arrival reuse
- freshness and material-change reapproval for remembered trust

What still remained under-specified was a smaller but important coordination seam:

> once a subject has one or more **approval-capable seats**, what proves whether any seat is **currently being asked to act on the current basis now**, which seats merely remain eligible, which seats already reviewed an older basis, and when explicit **rerequest** is required instead of silent carry-forward?

Real systems routinely blur these facts.
A reviewer chip, approver list, or "can approve" badge often tries to stand in for at least three different states at once:

- seat remains eligible to act
- seat is currently requested on the present head / basis
- seat already reviewed an older head and now needs explicit rerequest

That flattening creates two opposite lies:

1. **request-only collapse** — once a seat finishes review, its visible presence disappears, so later operators lose the continuity of which seats are even relevant;
2. **automatic rerequest on drift** — once a newer approval basis appears, the product silently acts as though the same seat is already being asked again.

This document defines the interface contract for one explicit **approval-seat roster** and one explicit **active approval request** lane.

## Core rule

Approval-seat eligibility and current approval-request state are distinct public facts.

A seat may remain visible in the eligible roster even when no live request is active.
A completed review may clear the live request without erasing seat relevance.
Later basis drift must surface `rerequest-needed` rather than silently preserving or silently reopening the request.

This applies anywhere AnonSync exposes:

- pending approvals for a current subject
- candidate acting seats for one approval-worthy action
- multi-seat operator workflows where any one of several seats could legitimately speak
- later basis drift that changes which reviewed request still binds the current subject

## Why this needs its own spec

`96-approval-seat-and-constellation-scope-review-interface-spec.md` already keeps acting seat and horizon explicit.
`97-standing-approval-memory-and-matched-arrival-guardrail-interface-spec.md` already keeps remembered trust separate from local claim.
`246-approval-memory-material-change-trigger-and-reapproval-clock-interface-spec.md` already says old trust reuse should reopen on material change.

But those truths are still not enough by themselves.
Without one explicit coordination split, the product can still lie in subtle ways:

- a row can show an eligible seat and imply that seat is already being asked to approve right now
- a seat can complete a prior review and then disappear as though it never mattered
- a newer basis can appear and the surface can look pending again without any explicit rerequest witness
- a stale reviewed basis can remain adjacent to current eligibility and trick operators into thinking the current request is already covered

Other comparison archives sharpened this seam in a directly portable way:

- roster membership is not the same thing as live request state
- completed review may clear the live request while keeping reviewer continuity visible
- later head or basis drift should produce `rerequest-needed`, not automatic reactivation

AnonSync should import that discipline directly.
A seat roster is continuity truth.
An active request is current coordination truth.
They are related, but they are not interchangeable.

## Public objects

### Approval seat roster row

A compact read object describing one seat that may matter to the current approval.

Suggested fields:

- `approval_seat_roster_row_id`
- `approval_request_ref`
- `seat_ref`
- `seat_label`
- `eligibility_state` (`eligible`, `eligible-narrow-only`, `blocked-current-basis`, `historical-only`, `unknown`)
- `eligibility_basis_summary`
- `max_horizon_now` (`none`, `this-subject`, `named-scope`, `reviewed-future-scope`)
- `last_reviewed_basis_ref` nullable
- `last_reviewed_at` nullable
- `current_request_state` (`not-requested`, `requested-current`, `review-in-progress`, `reviewed-current`, `rerequest-needed`, `withdrawn`, `ineligible`)
- `next_honest_action`

### Active approval request row

A compact read object describing the current live request state for one seat against one explicit basis.

Suggested fields:

- `active_approval_request_row_id`
- `approval_request_ref`
- `seat_ref`
- `requested_basis_ref`
- `requested_at`
- `request_state` (`requested-current`, `review-in-progress`, `reviewed-current`, `rerequest-needed`, `withdrawn`, `superseded`)
- `request_origin` (`operator-explicit`, `policy-generated`, `handoff-return`, `unknown`)
- `latest_review_witness_ref` nullable
- `latest_rerequest_witness_ref` nullable
- `basis_drift_class_since_request` (`none`, `additive-nonmaterial`, `material-compatible`, `contradictory`, `expired`, `unknown`)

### Approval rerequest object

A prepared review object for explicitly re-asking one seat to act on a newer basis.

Suggested fields:

- `approval_rerequest_object_id`
- `approval_request_ref`
- `seat_ref`
- `prior_requested_basis_ref` nullable
- `current_basis_ref`
- `rerequest_reason` (`basis-drift`, `scope-change`, `seat-switch`, `request-cleared-but-needed-again`, `policy-change`, `other`)
- `safe_to_rerequest_summary`
- `counterfactual_if_not_rerequested`
- `receipt_promise`

### Approval coordination receipt

A durable object proving what happened to current request state without erasing seat continuity.

Suggested fields:

- `approval_coordination_receipt_id`
- `approval_request_ref`
- `seat_ref`
- `prior_request_state`
- `resulting_request_state`
- `prior_basis_ref` nullable
- `resulting_basis_ref` nullable
- `coordination_outcome` (`request-opened`, `request-cleared-after-review`, `rerequest-opened`, `request-withdrawn`, `seat-marked-historical`, `seat-blocked-on-current-basis`)
- `issued_at`

## Stable coordination line

Every relevant seat should be classifiable along one durable line:

1. **Eligible, not currently requested** — seat could speak, but no live request is open now
2. **Requested on current basis** — seat is explicitly being asked to review/approve the current basis
3. **Review in progress** — seat is actively working on the requested basis
4. **Reviewed on current basis** — live request cleared, but the seat remains visibly relevant
5. **Rerequest needed** — seat reviewed an older basis or the current request was superseded; a fresh explicit rerequest is required
6. **Blocked / historical / ineligible** — seat no longer honestly participates on the current basis

The product must not pretend states 1, 2, 4, and 5 are the same.
`Can approve`, `is being asked now`, `already reviewed this basis`, and `must be re-asked` are materially different operator facts.

## Queue row contract

A reviewed approval queue may compress the whole coordination story into one row, but it must preserve one stable answer to four separate questions:

1. **Current subject** — what needs approval now
2. **Seat roster** — which seats remain eligible and with what present horizon
3. **Active request state** — whether any seat is currently requested on the current basis
4. **Next honest action** — review here, request on seat, rerequest, switch seat, or keep eligible-only

### Example rows

```text
Maya → Photos-2026   Seats: Laptop-Admin, Studio-Server   Active: none   Request on seat   Details
Maya → Photos-2026   Seats: Laptop-Admin, Studio-Server   Active: Laptop-Admin current   Review here   Details
Maya → Photos-2026   Seats: Laptop-Admin reviewed, Studio-Server eligible   Active: rerequest needed   Re-request   Details
Printer-NAS → Scans  Seats: Studio-Server narrow-only      Active: reviewed current       Approve once   Details
```

The important part is that the row says **who could act**, **who is being asked now**, and **whether that current ask still binds the current basis**.
It must not let one badge answer all three questions.

## Fixed inspection order

Every approval-coordination surface should preserve this order:

1. **Current approval basis**
2. **Seat roster and present eligibility**
3. **Current active request state**
4. **Latest review witness versus current basis**
5. **Request, rerequest, clear, or switch-seat actions**

### 1) Current approval basis

The surface should show:

- requested subject
- current scope / rights at stake
- current basis ref or basis summary
- whether the basis is the same one last requested / reviewed

The operator should be able to answer:

> what exact approval world is current now?

### 2) Seat roster and present eligibility

This section should show, per seat:

- why the seat is eligible or blocked now
- how far that seat may currently speak
- whether that seat is narrower or wider than nearby alternatives
- whether that seat is only historical on the present basis

The operator should be able to answer:

> which seats still matter, even if no live request is open?

### 3) Current active request state

This section should say:

- whether any seat is currently requested on the current basis
- which basis that request targets
- whether review is in progress, completed, cleared, superseded, or rerequest-needed
- whether the current request exists at all

The operator should be able to answer:

> is anyone actually being asked right now, or are these seats merely eligible?

### 4) Latest review witness versus current basis

This section should compare:

- most recent review witness by seat
- current basis
- whether the last review still binds the current basis
- whether rerequest is required

The operator should be able to answer:

> did someone already review this exact basis, or only an older one?

### 5) Request, rerequest, clear, or switch-seat actions

Primary actions should reflect the coordination truth.
Examples:

- `Request review on Laptop-Admin`
- `Review here now`
- `Re-request on current basis`
- `Switch to narrower seat`
- `Clear live request`
- `Keep eligible only`

## Public rules

### Rule 1 — roster visibility survives completed review

A seat that completed review on the current basis may clear the live request.
It must not vanish from the coordination story if it still remains eligible or historically relevant.

### Rule 2 — later basis drift is not automatic rerequest

If the basis changes materially, the surface must say `rerequest-needed` until a fresh explicit rerequest is recorded.
The product must not silently reactivate the request.

### Rule 3 — eligibility is not proof of current ask

A seat chip, roster row, or capability badge must not imply that a live request exists.
`May approve` and `is currently requested` are separate facts.

### Rule 4 — reviewed-current is stronger than eligible, weaker than evergreen

A seat that reviewed the current basis is not merely eligible.
But that review is still basis-bound, not timeless.
Later drift may downgrade it to `rerequest-needed`.

### Rule 5 — rerequest requires a receipt

A fresh ask against a newer basis must produce its own coordination receipt.
A quiet pointer update is not enough.

### Rule 6 — no queue may claim "waiting on review" when nobody is requested

If all seats are merely eligible and no live request exists, the row should not say `waiting on review`.
The honest state is `eligible, no active request`.

## Dense row contract

A dense approval-coordination row should preserve these labels in this order:

- `Subject`
- `Seats`
- `Active`
- `Basis`
- `State`
- `Next action`

## Example prompts

- `Which seats could approve this now, even if nobody is currently asked?`
- `Is Laptop-Admin currently requested, or did it only review the older basis?`
- `Why does this say rerequest needed instead of already pending?`
- `Which seat remains eligible but narrower than the one we asked last time?`
- `What receipt proves the current ask targets the current basis rather than the older one?`

## Anti-goals

- no reviewer-chip folklore where seat presence implies live request
- no disappearing seat continuity after completed review
- no silent auto-rerequest when basis drift appears
- no generic `waiting for review` label when nobody is currently requested
- no timeless reading of a completed review witness

## Result

This seam matters because AnonSync is increasingly explicit about who may speak, what basis they are speaking against, and how later drift reopens previously careful work.
The archive should therefore preserve one small truth that many systems blur away:

> **seat relevance is a roster fact; live approval coordination is a request fact; later drift requires explicit rerequest instead of wishful continuity.**
