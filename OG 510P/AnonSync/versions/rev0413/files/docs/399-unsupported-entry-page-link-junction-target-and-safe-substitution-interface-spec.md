# Unsupported entry page: link, junction, target, and safe substitution interface spec

## Purpose

The archive already has alias-edge and filesystem-shape doctrine.
This document makes the ordinary unsupported-entry page concrete.

The page exists to answer:

> what exactly is this entry class, what lies behind it, what part will sync faithfully, and what safe substitution path exists if the current class is unsupported or only partially preserved?

## Core decision

Every serious sync product must own one first-class **Unsupported entry** page whenever a link, junction, alias, or related entry class materially changes fidelity or inclusion.

## Fixed page order

1. entry identity strip
2. observed entry-class card
3. target-material card
4. fidelity / inclusion verdict
5. safe substitution ladder
6. receipts and follow-up

### 1) Entry identity strip

Show:

- subject and seat
- observed entry path
- detected entry class (`symlink`, `junction`, `hard link`, `alias-like`, `unknown indirection`)
- current verdict (`faithful`, `entry-only`, `target-excluded`, `unsupported`, `blocked-needs-migration`)

### 2) Observed entry-class card

Show:

- how the product classified the entry
- platform family used for classification
- whether the class is natively supported here
- whether support applies to the link object itself, its target material, or neither

### 3) Target-material card

Show:

- whether the entry points to another path
- whether the target path is inside the current subject, elsewhere on the same seat, or unresolved
- whether target bytes are included, excluded, or require separate admission
- whether the operator can inspect the target safely from this page

### 4) Fidelity / inclusion verdict

Show one explicit verdict:

- `entry preserved and target included`
- `entry preserved but target excluded`
- `entry rewritten / downgraded`
- `unsupported on this seat family`
- `blocked pending separate-subject decision`

Also show the strongest sentence explaining why.

### 5) Safe substitution ladder

Allowed next steps:

- `leave as-is and accept reduced fidelity`
- `admit target as separate subject`
- `replace with ordinary copied bytes`
- `keep local-only`
- `block subject on this seat`
- `open filesystem shape audit`

Each action must preview:

- whether target bytes enter the sync graph
- whether alias semantics are lost
- whether later target drift remains coupled
- whether cross-seat parity improves or worsens

### 6) Receipts and follow-up

Show:

- last unsupported-entry receipt
- target-inspection receipts
- any substitution receipts
- whether revalidation is required after platform or policy change

## Public objects

### Unsupported entry page

Fields:

- `unsupported_entry_page_id`
- `subject_ref`
- `seat_ref`
- `entry_path`
- `detected_entry_class`
- `target_rows[]`
- `fidelity_verdict`
- `substitution_actions[]`
- `receipt_refs[]`
- `next_honest_action`

### Target row

Fields:

- `target_row_id`
- `target_path` nullable
- `target_scope` (`inside-subject`, `outside-subject`, `unresolved`, `unknown`)
- `included_now`
- `would_require_separate_admission`
- `proof_confidence`

## Guardrails

The page must never:

- imply that syncing a symlink automatically syncs the target material when it does not
- imply unsupported entry classes are harmless if they can spawn repeated conflict fallout
- silently rewrite or drop alias semantics without publishing the fidelity verdict
- bury separate-subject admission as a support workaround instead of a first-class action

## Success criteria

The page is successful only when an operator can answer:

1. what entry class was actually found
2. whether the entry object itself is preserved
3. whether the target bytes are included, excluded, or require separate admission
4. what the least-destructive safe substitution is
5. what receipt will prove the chosen fidelity tradeoff
