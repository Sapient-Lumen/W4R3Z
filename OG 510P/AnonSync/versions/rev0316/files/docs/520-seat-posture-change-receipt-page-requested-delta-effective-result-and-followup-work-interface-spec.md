# Seat posture change receipt page — requested delta, mechanism class, effective result, and unfinished-work record interface spec

## Purpose

A posture change is not fully governed if the system can only show the live result and cannot prove how it got there.
This page exists to preserve one durable answer to:

> what posture change was requested here, what mechanism class actually executed, what changed, and what still remains to be done?

## Core decision

Every accepted posture-change draft must emit one durable **Seat posture change receipt**.
This receipt is distinct from:

- grant/artifact receipts
- bind receipts
- current seat posture receipts
- descendant reshare receipts

It bridges intention and resulting state.

## Fixed page order

1. **Receipt identity**
2. **Requested vs executed change**
3. **Effective result**
4. **Cascade and residue record**
5. **Unfinished work**
6. **Export and replay boundaries**

### 1) Receipt identity

Show:

- receipt id
- creation time
- actor
- root seat
- subject
- source draft / forecast refs

### 2) Requested vs executed change

Render both:

- requested posture delta
- executed mechanism class
- whether execution matched the request exactly, partially, or with substitution

Possible execution-match values:

- `exact`
- `exact_but_manual_followups_pending`
- `substituted_mechanism`
- `partially_applied`
- `blocked`
- `rolled_back`

This section must preserve why any substitution happened.

### 3) Effective result

Show:

- resulting effective posture on the root seat
- whether the same subject remained or a successor subject was bound
- resulting byte/path status
- resulting delegation and recovery ceilings

### 4) Cascade and residue record

Record:

- descendants auto-narrowed
- descendants removed
- descendants left pending manual rebind
- local residue or old-path leftovers
- archived or quarantined artifacts
- unaffected dependents

### 5) Unfinished work

List all remaining work items with status:

- `pending`
- `completed`
- `waived`
- `blocked`

Examples:

- recreate local child
- verify new read-only bind
- retire superseded artifact
- clear old residue
- inform dependent operator

### 6) Export and replay boundaries

The receipt must say what it can and cannot do.

It may:

- prove requested delta
- prove executed mechanism class
- prove resulting posture and known cascades

It must not:

- act as a live bearer artifact
- recreate secret keys
- silently replay a posture change without fresh review

## Public object

### `seat_posture_change_receipt`

Required fields:

- `seat_posture_change_receipt_id`
- `change_draft_ref`
- `forecast_ref`
- `actor_ref`
- `seat_ref`
- `subject_ref`
- `requested_delta[]`
- `executed_mechanism_class`
- `execution_match`
- `resulting_effective_posture`
- `resulting_bind_verdict`
- `cascade_effects[]`
- `residue_effects[]`
- `unfinished_work_items[]`
- `created_at`

## Main surface

A compact **Seat posture change receipt** card should show:

- result chip
- mechanism chip
- execution-match chip
- unfinished-work chip

Example:

```text
receive-only now effective   rebind_same_seat   exact but follow-ups pending   3 tasks remain
```

## Detailed surface

The detailed page should keep four panes.

### Pane A — Intent and execution

Columns:

- requested axis
- requested value
- executed result
- match class

### Pane B — Root result

Columns:

- result family
- final verdict
- strongest basis

### Pane C — Cascade/residue

Columns:

- affected node or residue
- effect
- status

### Pane D — Follow-up tasks

Columns:

- task
- status
- owner

## CLI parity

Minimum commands:

- `anonsync seat-posture receipt <receipt-id>`
- `anonsync seat-posture receipts --seat <seat> --subject <subject>`
- `anonsync seat-posture export-receipt <receipt-id>`

## Acceptance criteria

A user can:

- prove what was requested and what mechanism actually executed
- see whether the result matched exactly or required substitution
- see cascades, residue, and unfinished work in one durable place
- export a receipt without exporting live bearer authority
