# Maintenance intent page — requested hold class and motion budget interface spec

## Purpose

The archive already has quiet-window, residual-activity, quiet-break, and backlog-release pages.
What it still lacked was one ordinary page for the question:

> before I touch any controls, what kind of maintenance hold do I actually need, what kinds of motion are allowed, and what stronger freeze sentence am I not yet entitled to use?

Current official Resilio docs make this seam concrete.
They still show `pause`, scheduled `Paused`, read-only sync, and Android backup as different semantic islands.
That is useful truth.
It should not remain a feature-memory test.

## Core decision

AnonSync must expose one first-class **Maintenance intent** page whenever an operator is preparing to quiet, freeze, redirect, preserve, or constrain a live subject, seat, or cohort for maintenance reasons.

The page exists to answer five things in one place:

1. what maintenance goal is being requested
2. which hold class best fits that goal
3. what motion budget is allowed during the hold
4. which counterpart seats must match or acknowledge it
5. what sentence is honest before the hold is actually entered

## Fixed page order

1. **Requested maintenance verdict**
2. **Hold-class chooser**
3. **Allowed motion budget**
4. **Counterpart and scope requirements**
5. **Actions and receipts**

### 1) Requested maintenance verdict

Show:

- `maintenance_intent_page_id`
- scope (`seat`, `subject`, `cohort`, or `route slice`)
- requested goal (`upgrade`, `evidence capture`, `destructive repair`, `bandwidth quiet`, `preservation`, `migration`, `other`)
- currently recommended `hold_class`
- strongest honest summary
- stronger unsupported summary

The operator must be able to answer:

> what kind of hold am I asking for, in the product's language?

### 2) Hold-class chooser

Offer typed classes such as:

- `transfer-quiet`
- `drain-then-hold`
- `writeback-quiet`
- `delete-freeze`
- `preserve-only`
- `full-maintenance-freeze`
- `custom`

Each class must visibly describe:

- whether downloads continue
- whether uploads continue
- whether local edits can write back
- whether remote deletions can land
- whether scans/indexing continue
- whether new backlog can accumulate behind the hold

The interface must make it ordinary to answer:

> which class actually matches my intent, and which near-miss class would mislead me later?

### 3) Allowed motion budget

This section is mandatory.
Show motion rows for at least:

- byte transfer
- delete propagation
- rename/move propagation
- local edit writeback
- remote arrival visibility
- indexing / share-size changes
- control-plane or zero-byte events
- backlog accumulation

Each row must show one state:

- `allowed`
- `allowed but not claim-bearing`
- `blocked`
- `unknown until counterpart review`

The page must answer:

> what exactly is still permitted to move during this maintenance hold?

### 4) Counterpart and scope requirements

Show:

- whether this hold is meaningful locally only or requires a counterpart cohort
- which seats must match the hold class for the claim to be operationally honest
- whether a weaker local-only claim is still available
- which uncovered seats remain risk-bearing
- what evidence or acknowledgement would upgrade the claim

The page must answer:

> is this a local posture only, or does the maintenance sentence I want require wider agreement?

### 5) Actions and receipts

Actions may include:

- `Enter hold`
- `Request counterpart hold`
- `Review semantics`
- `Plan transition`
- `Narrow scope`
- `Cancel`

Receipts must record requested goal, chosen hold class, motion budget, and strongest safe sentence.

## Public object

### Maintenance intent page

Fields:

- `maintenance_intent_page_id`
- `scope_ref`
- `requested_goal`
- `recommended_hold_class`
- `hold_class_candidates[]`
- `motion_budget_rows[]`
- `counterpart_requirement_rows[]`
- `strongest_safe_sentence`
- `stronger_rejected_sentence`
- `next_actions[]`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. scope
2. requested goal
3. chosen hold class
4. most important allowed residual
5. next action

Example:

```text
Project Alpha     upgrade window     drain-then-hold     remote deletes still unresolved until counterpart match     Request counterpart hold
```

## Non-goals

This page does **not** prove the hold is active yet.
It proves only the requested **maintenance intent, chosen hold class, and motion budget**.
