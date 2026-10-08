# Indirection posture page: entry kind, platform lane, and object fate interface spec

## Purpose

This page exists to answer one ordinary operator question:

> what kind of path row is this really, and what exactly survives on this seat — the object, the target, both, or neither?

## Core decision

Every serious sync product must own one first-class **Indirection posture** page whenever a row that looks like a file or folder is actually an indirection object.

## Fixed page order

1. identity strip
2. entry-class card
3. object-fate card
4. target-scope card
5. graph-widening card
6. receipts and next action

### 1) Identity strip

Show:

- subject and seat
- entry path
- current display name
- detected entry kind (`ordinary-file`, `ordinary-folder`, `symbolic-link`, `hard-link`, `junction`, `alias-like`, `unknown-indirection`)
- current summary verdict (`ordinary`, `preserved-as-object`, `target-excluded`, `separate-admission-needed`, `blocked`, `conflict-prone`)

### 2) Entry-class card

Show:

- detection basis used for classification
- seat family / filesystem lane used for interpretation
- whether this platform lane supports the entry object natively
- whether the object is being treated as entry, payload, or unsupported control residue

### 3) Object-fate card

Show:

- `entry_object_fate` (`preserve`, `flatten`, `block`, `unsupported-conflict-prone`, `unknown`)
- strongest safe sentence
- stronger forbidden sentence
- whether a mismatch already produced warnings or conflicts

### 4) Target-scope card

Show:

- whether the entry has a resolvable target
- target scope (`inside-subject`, `outside-subject`, `unresolved`, `none`, `unknown`)
- whether target bytes are in scope now
- whether target inclusion would require a separate admission act
- whether target inspection is safe from this page

### 5) Graph-widening card

Show:

- `graph_widening_risk` (`none`, `inside-coupling-only`, `outside-subject-widening`, `unknown`)
- whether follow-target would widen the current subject contract
- whether later drift remains coupled if the operator keeps the object only
- safest next action (`leave-local`, `preserve-object`, `follow-target`, `branch-bytes`, `block`, `inspect-only`)

### 6) Receipts and next action

Show:

- latest indirection receipt
- latest target transitivity proof
- any conflict evidence linked to this object
- next honest action

## Public objects

### Indirection posture page

Fields:

- `indirection_posture_page_id`
- `subject_ref`
- `seat_ref`
- `entry_path`
- `entry_kind`
- `platform_lane`
- `entry_object_fate`
- `target_scope`
- `target_transitivity_verdict`
- `graph_widening_risk`
- `conflict_hazard`
- `receipt_refs[]`
- `next_honest_action`

## Guardrails

The page must never:

- imply that preserving a symbolic link automatically preserves target bytes
- imply that an unsupported entry is harmless when conflict fallout is possible
- silently widen the graph by following a target
- flatten object fate and target scope into one badge

## Success criteria

The page is successful only when an operator can answer:

1. what entry kind was actually found
2. what happens to the object on this seat family
3. whether target bytes are in scope now
4. whether following the target widens the graph
5. what the safest next action is
