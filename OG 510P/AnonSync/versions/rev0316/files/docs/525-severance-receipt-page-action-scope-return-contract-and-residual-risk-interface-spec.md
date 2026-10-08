# Severance receipt page — action scope, return contract, and residual risk interface spec

## Purpose

The archive already had receipts for posture changes, bind outcomes, and containment decisions.
What it still lacked was one durable receipt proving what kind of severance actually happened and what did **not** happen.

This page exists to answer:

> after I made something disappear, what scope was actually touched, what can still return, and what stronger action is still pending?

## Core decision

AnonSync should emit a **severance receipt** for every action that changes disappearance, local relation, or retention scope.

That receipt must preserve:

- requested verb
- reviewed severance class
- effective scope touched
- objects not touched
- return contract
- residual risk
- stronger unresolved action, if any

## Receipt sections

1. **Requested versus actual**
2. **Scope touched**
3. **Residual truth**
4. **Return contract**
5. **Follow-up work**
6. **Evidence bundle**

### 1) Requested versus actual

Show:

- operator-requested wording
- reviewed class
- final executed class
- whether the class changed during review

### 2) Scope touched

Show explicit outcomes for:

- local row
- local bytes
- local future relation
- linked cohort
- external retainers
- archive/history

### 3) Residual truth

Show what still exists and why:

- hidden-only rows
- bytes outside recall
- external retainers
- pending rotation requirement
- unknowns / blind spots

### 4) Return contract

Show:

- whether automatic return remains possible
- exact events that can cause return
- how the operator would recognize it
- whether a new review will be required before full reattachment

### 5) Follow-up work

Show next actions such as:

- no follow-up required
- optional stronger severance
- rotate identity
- reissue successor subject
- inspect external retainer list
- archive review

### 6) Evidence bundle

Include:

- pre-action state hash / digest
- review identifier
- graph snapshot reference
- policy basis reference
- actor / timestamp / seat

## Main surface

The receipt should have a top verdict line in plain language, for example:

- `Hidden only; no severance occurred`
- `Disconnected here; bytes remain locally`
- `Removed from linked cohort; external retainers may remain`
- `Deleted across authorized retainers; archive residue remains`
- `Local unlink complete; broader rotation still recommended`

## Searchability

Receipts must be searchable by:

- object
- action class
- actor
- time
- residual-risk tag
- return-contract tag

## CLI parity

Minimum commands:

- `anonsync severance receipt list`
- `anonsync severance receipt show <receipt-id>`
- `anonsync severance receipt export <receipt-id>`

## Non-goals

This spec does **not** define:

- archive restore receipts
- long-term log retention policy
- external notification wording
