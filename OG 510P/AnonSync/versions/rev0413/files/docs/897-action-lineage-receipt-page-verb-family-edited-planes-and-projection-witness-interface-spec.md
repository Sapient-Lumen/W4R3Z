# Action lineage receipt page: verb family, edited planes, and projection witness interface spec

## Purpose

After a rename-like action, later operators need durable truth that does not depend on remembering which client or icon was used.
This page exists to preserve that truth.

## Core decision

Every serious rename-like action must emit one first-class **Action lineage receipt**.

The receipt owns:

- resolved verb family
- executing projection
- edited planes
- untouched planes
- audience reached
- stronger rejected reading
- lineage / supersession hooks

## Fixed page order

1. action receipt header
2. plane delta ledger
3. projection witness card
4. audience / artifact aftermath
5. supersession and reopen triggers

### 1) Action receipt header

Show:

- receipt id
- subject and optional seat scope
- resolved verb family
- executing projection
- executed time
- strongest safe sentence

### 2) Plane delta ledger

Render one row per serious plane with:

- plane
- before value summary
- after value summary
- change verdict (`changed`, `unchanged`, `cleared`, `issued`, `unknown`)

### 3) Projection witness card

This card is mandatory.
Show:

- exact projection used
- why that matters for semantic interpretation
- any broader or narrower neighboring projections
- stronger rejected reading

Example rejected reading:

- `This renamed the canonical subject everywhere.`

### 4) Audience / artifact aftermath

Show:

- who immediately saw the change
- which older artifacts retained older labels
- whether future artifacts will differ from past ones
- whether disk paths changed on this seat only or nowhere

### 5) Supersession and reopen triggers

Show at minimum:

- later action that would supersede this receipt
- whether reset/retitle/path rename would count as a new receipt family
- reopen trigger for ambiguous later evidence

## Rules

### Rule 1 — the receipt preserves projection witness forever

Later operators must not have to infer semantics from the changed value alone.

### Rule 2 — unchanged planes stay visible

A receipt that says only what changed invites overreading.

### Rule 3 — rejected stronger readings are explicit

The receipt must preserve the strongest honest sentence and at least one stronger forbidden interpretation.

## Acceptance criteria

A later operator can:

- tell exactly what verb family was executed
- tell which projection executed it
- tell which planes changed and which did not
- tell which audience actually saw the change
- tell what later act would supersede the receipt
