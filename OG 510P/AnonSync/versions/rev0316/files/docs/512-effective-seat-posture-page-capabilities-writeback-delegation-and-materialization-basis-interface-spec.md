# Effective seat posture page — capabilities, writeback, delegation, and materialization basis interface spec

## Purpose

The archive already has join consequence, linked-seat narrowing, ciphertext custody, and same-host lineage doctrine.
What it still lacked was one ordinary page for the question operators ask after setup is already real:

> what can this seat actually do now for this subject, and why?

This page exists so the operator does not have to infer effective posture from a permission chip, a hidden inheritance rule, an encrypted-folder caveat, or a failed local edit.

## Core decision

Every seat/subject pair must be able to render one first-class **Effective seat posture** page.

This page is about current truth, not only requested policy.
It must separate:

- requested right
- effective right
- current byte posture
- local-mutation behavior
- delegation ceiling
- derivation basis

## Fixed page order

1. **Seat and subject in scope**
2. **Effective capability vector**
3. **Byte and materialization posture**
4. **Local mutation contract**
5. **Delegation and descendant effects**
6. **Next actions and receipt promise**

### 1) Seat and subject in scope

Show:

- seat identity
- subject identity
- owner-domain / linked-family relation if relevant
- current artifact family or bind lane
- strongest requested-right label

The operator should be able to answer: **which seat/subject pair am I inspecting?**

### 2) Effective capability vector

Render the capability vector as separate lines, not one blended role label.

Required axes:

- `observe`
- `materialize bytes`
- `retain local full copy`
- `write local names`
- `write local content`
- `propagate local mutations`
- `delegate / re-share`
- `change member rights`
- `recover plaintext`

Each axis must show one of:

- `allowed`
- `allowed with review`
- `blocked`
- `blocked by posture`
- `blocked by derivation`
- `blocked by custody class`
- `unknown`

The page must also show the strongest basis for each blocked or narrowed capability, such as:

- `linked-owner default`
- `read-only grant`
- `encrypted-custody ceiling`
- `derived local child ceiling`
- `source-right lowered`
- `policy override`

### 3) Byte and materialization posture

Show:

- whether the seat is disconnected, names-only, partial, or full-copy
- whether local bytes are plaintext, ciphertext-only, or mixed/unknown
- whether on-demand materialization is available
- whether byte posture is chosen, inherited, or forced by custody class

The operator should be able to answer: **what byte form exists here right now?**

### 4) Local mutation contract

This section must say what happens if someone edits locally on this seat.

Possible contract rows include:

- local edit propagates normally
- local edit remains local only
- local edit suspends synchronization for touched items
- local edit is overwritten by authoritative source state
- local addition remains unsynced residue
- rename produces restored original alongside local rename
- delete is restored from broader peer

The page must not force the operator to learn this from a support article or after-the-fact conflict.

### 5) Delegation and descendant effects

Show:

- whether the seat may invite/share onward
- whether it may create descendants or local derivatives
- whether descendants inherit the same ceiling or a narrower one
- whether lowering the source right cascades automatically
- whether removal of the source also removes the descendant posture

The operator should be able to answer: **what spreads from this seat, and what cannot?**

### 6) Next actions and receipt promise

Allowed actions may include:

- `Review linked-seat narrowing`
- `Review local mutation on this seat`
- `Open derived rights graph`
- `Promote seat posture`
- `Retire stronger old artifact`
- `Export seat posture receipt`

The page must promise one durable receipt preserving the effective posture basis.

## Public object

### `effective_seat_posture_snapshot`

Required fields:

- `effective_seat_posture_snapshot_id`
- `seat_ref`
- `subject_ref`
- `requested_posture`
- `effective_posture`
- `capability_vector[]`
- `materialization_class`
- `local_mutation_contract[]`
- `delegation_verdict`
- `derivation_basis[]`
- `generated_at`

## Main surface

A compact **Effective seat posture** card should show:

- effective posture chip
- strongest narrowing basis chip
- local-mutation contract chip
- next action chip

Example:

```text
Tablet-Citrine · photos
receive-only effective posture   basis: encrypted custody   local edits overwritten or left local   Review
```

## Detailed surface

The detailed page should keep four panes.

### Pane A — Capability vector

Columns:

- capability axis
- verdict
- strongest basis

### Pane B — Byte posture

Columns:

- byte/materialization aspect
- current verdict
- why

### Pane C — Local mutation contract

Columns:

- local event kind
- result here
- result elsewhere

### Pane D — Delegation / descendants

Columns:

- downstream power
- verdict
- cascade note

## CLI parity

Minimum commands:

- `anonsync seat-posture show <seat> --subject <subject>`
- `anonsync seat-posture explain <seat> --subject <subject> --axis <axis>`
- `anonsync seat-posture receipt <receipt-id>`

## Acceptance criteria

A user can:

- tell what the seat can actually do now, not just what was once requested
- see whether local edits propagate, suspend, revert, or remain local residue
- see whether delegation and descendants are permitted or narrowed
- export one durable proof object for later troubleshooting or audit
