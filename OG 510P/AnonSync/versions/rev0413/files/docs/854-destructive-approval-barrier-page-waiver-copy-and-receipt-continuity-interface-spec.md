
# Destructive approval barrier page — waiver copy and receipt-continuity interface spec

## Purpose

A reviewed destructive action still needs one final barrier before state mutates.
This page exists so approval means:

> the operator has seen the exact destructive sentence, the surviving salvage ladder, and the current receipt lineage, and is authorizing *this* action rather than vaguely consenting to repair.

## Core decision

AnonSync must expose one first-class **Destructive approval barrier** before any serious destructive action executes.
A warning modal is insufficient.
The barrier is a page-level object with durable lineage.

## Fixed page order

1. **Barrier summary**
2. **What you are authorizing**
3. **Open salvage and unattempted rescue**
4. **Waiver rows and claim ceiling**
5. **Approval controls and resulting receipt path**

### 1) Barrier summary

Show:

- `destructive_approval_barrier_page_id`
- action under approval
- scope
- endpoint and acting seat summary
- current basis freshness (`current`, `stale`, `partially stale`, `unknown`)
- strongest honest summary

If basis freshness is not current enough for the action class, the barrier must block commit.

### 2) What you are authorizing

Show the exact destructive statement in plain language.
Examples:

- `Approve source-authoritative healing for 3 edited files and 1 local rename on seat Bristol-Laptop.`
- `Approve encrypted-seat reset knowing no same-line restore remains for 2 local additions.`

This section must also show:

- affected row counts by fate class
- whether same-line continuity will be broken for any class
- whether the action is reversible, partially reversible, or not reversible from current proof

### 3) Open salvage and unattempted rescue

Show:

- viable rescue rungs still open
- rescue rungs not yet attempted
- rescue rungs already spent
- fastest safe alternative action

The operator must be able to answer:

> what cheaper rescue am I explicitly declining by approving now?

### 4) Waiver rows and claim ceiling

Show structured waiver rows:

- waived work family
- why it is waived now
- what remnant, if any, survives elsewhere
- strongest safe sentence after execution
- stronger forbidden sentence

The barrier must preserve the future claim ceiling before the operator approves.

### 5) Approval controls and resulting receipt path

Controls may include:

- `Approve destructive action`
- `Approve after export`
- `Return to salvage`
- `Cancel`

A successful approval must emit or advance:

- destructive action receipt
- overwrite ledger / successor ledger linkage
- supersession path for later recovery

## Interaction rules

- no hidden checkbox confirmations
- no approval via row-menu shortcut
- no irreversible destructive commit from keyboard-only quick action unless the full barrier object is already in focus and rendered
- re-auth or stronger capability proof may be required for high-severity classes

## Public object

### Destructive approval barrier page

Fields:

- `destructive_approval_barrier_page_id`
- `destructive_action_ref`
- `endpoint_ref`
- `acting_seat_ref`
- `basis_freshness_verdict`
- `authorization_sentence`
- `affected_row_counts[]`
- `open_salvage_rows[]`
- `waiver_rows[]`
- `claim_ceiling`
- `allowed_controls[]`
- `resulting_receipt_path[]`
- `generated_at`
