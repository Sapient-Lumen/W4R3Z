# Linked-seat rights narrowing and owner-domain separation interface spec

## Purpose

The archive already has observer-rights decomposition, topology-aware rights editing, and future-arrival posture language.
What it still lacked was one explicit contract for a subtler but important seam:

> when several seats belong to the same person or owner-domain, how does the product let one of those seats become intentionally narrower without pretending it is a different subject, a different owner, or a reconnect-by-key ritual?

Current official Resilio docs make this seam vivid.
They still say all devices linked to one identity act as Owners, and a separate current help page for making one linked device read-only still tells the operator to use a Standard folder with a Read Only key, disconnect the already-connected folder, open `+ -> Enter a key or link`, paste the key, and choose a path manually.

That is not just a workaround.
It means self-owned seat posture and subject identity are still tangled together.

AnonSync should therefore treat per-seat narrowing inside one owner-domain as a first-class rights change, not as share replacement folklore.

## Core decision

A subject should keep one stable subject identity even when seats inside the same owner-domain hold different postures.
The product must let the operator narrow one seat to a less powerful posture without forcing any of these hidden substitutions:

- new artifact family
- new subject class
- disconnect/reconnect ritual
- silent path re-adoption
- new owner-domain meaning

In other words:

> seat posture may narrow without pretending the seat left and rejoined a different subject.

## Fixed review order

Every same-owner seat-narrowing review should render the same sections in the same order:

1. **Owner-domain and seat in scope**
2. **Current versus requested seat posture**
3. **Subject-identity continuity**
4. **Dependent consequences and reversal**
5. **Seat-narrowing receipt**

### 1) Owner-domain and seat in scope

This section should show:

- owner-domain / constellation in scope
- subject in scope
- seat selected for narrowing
- other seats that retain broader posture

The operator must be able to answer: **which one of my seats am I narrowing, and who else stays broad?**

### 2) Current versus requested seat posture

This section should show:

- current effective posture on the seat
- requested posture (`observe`, `receive-only`, `write-blocked`, `names-only`, `other`)
- whether the narrowing changes materialization, writeback, delegation, or future-arrival defaults
- whether the seat already carries local bytes that need separate treatment

The operator must be able to answer: **what exactly becomes narrower on this seat?**

### 3) Subject-identity continuity

This section should show:

- that the subject identity stays the same
- whether any delivery artifact or local bind would change
- whether the seat remains a remembered member of the same owner-domain
- whether reversal later is a posture change, not a rejoin

The operator must be able to answer: **am I narrowing one seat inside the same subject, or creating a second subject in disguise?**

### 4) Dependent consequences and reversal

This section should show:

- effects on local materialization
- effects on local write attempts
- effects on future arrivals on this seat
- whether reversal is immediate, reviewed, or blocked by policy
- whether any older stronger rights artifacts remain and need retirement

The operator must be able to answer: **what stays local, what becomes inert, and how would I widen this seat later?**

### 5) Seat-narrowing receipt

This section should show:

- subject identity before/after
- seat posture before/after
- owner-domain continuity proof
- artifact rotation or retirement if any
- reversal conditions

The operator must be able to answer: **what later proves that I narrowed a seat, not that I disconnected and joined something else?**

## Public objects

### `linked_seat_narrowing_review`

Fields:

- `linked_seat_narrowing_review_id`
- `owner_domain_ref`
- `subject_ref`
- `seat_ref`
- `current_posture`
- `requested_posture`
- `subject_identity_continuity_class`
- `artifact_delta_summary`
- `dependent_effects[]`
- `generated_at`

### `linked_seat_posture_receipt`

Fields:

- `linked_seat_posture_receipt_id`
- `review_ref`
- `subject_ref`
- `seat_ref`
- `before_summary`
- `after_summary`
- `owner_domain_continuity_summary`
- `artifact_retirement_refs[]`
- `created_at`

## Main surface

A compact row should read like one of these:

- `seat narrowed inside same subject`
- `seat observe-only · subject identity preserved`
- `seat narrowing blocked · old broad artifact still active`
- `seat posture widened back by review`

## CLI shape

```text
anonsync seat posture review --seat tablet-citrine --subject photos --to observe
anonsync seat posture apply <review>
anonsync seat posture receipt <receipt>
```

## Design tests

The model is not explicit enough if any of these remain true:

- narrowing one self-owned seat still requires disconnect-and-rejoin ritual
- subject identity changes just to express a weaker seat posture
- seat reversal later behaves like a fresh join instead of a posture widening
- the operator must infer from keys, path prompts, or new rows that this was really a self-seat rights edit

## Non-clone reason

Resilio's current docs still treat linked devices as one owner-like domain and then fall back to disconnect-plus-read-only-key ritual when one of those seats should become narrower.
AnonSync should instead make same-owner seat narrowing a first-class, in-place rights change with explicit continuity receipts.
