# Absence versus authority page — hidden row, disconnected seat, and residual reachability interface spec

## Purpose

The archive already had hidden/offline truth, disconnect contracts, and compromise residuals.
What it still lacked was one page that proves the difference between a thing looking absent and a thing actually losing reach or authority.

This page exists to answer:

> if the row is gone or greyed out, what still exists, where, and who can still make it matter?

## Core decision

AnonSync should provide one explicit **absence versus authority** page whenever row visibility and actual reachability can diverge.

That page must separate four dimensions:

- **visibility** — is there still a row here
- **material presence** — do bytes still exist here
- **future relation** — can this seat still resume or receive future updates
- **external reachability** — can another seat still reintroduce or retain the subject

## Why this matters

Operators routinely misread absence.
The page must stop these false inferences:

- hidden means severed
- disconnected means deleted
- local placeholder means gone everywhere
- removed from linked seats means gone on every retainer
- unlinked here means the other seat is dead
- quiet means safe

## Fixed page order

1. **What looks absent**
2. **What still exists**
3. **Who can still cause return**
4. **What would fully sever it**
5. **Receipts and history**

### 1) What looks absent

Classify the visible state:

- hidden row
- disconnected row
- placeholder-only local presence
- removed from local list
- retired subject
- rotated-away identity
- no row but known external retainer

### 2) What still exists

Render an existence matrix:

- row here
- bytes here
- placeholder / stub here
- authority here
- linked-cohort presence
- external-retainer presence
- archive/history residue

### 3) Who can still cause return

Show exact return triggers:

- cleared hidden device comes online
- disconnected subject is reconnected
- placeholder is re-materialized
- peer reissues the subject
- current cohort relinks
- no supported return path

### 4) What would fully sever it

Show the smallest remaining action that would actually cut the residual path:

- hide-only is enough
- disconnect is enough
- remove from linked cohort is enough
- delete across authorized retainers is needed
- unlink local seat is needed
- identity rotation is needed
- no self-serve severance available

### 5) Receipts and history

Show prior receipts that affected current absence semantics:

- last hide
- last disconnect
- last remove
- last unlink
- last rotation
- last observed external reappearance

## Main surface

This page should present a compact verdict such as:

- `Absent here, still reachable by linked cohort`
- `No local bytes, external retainer still exists`
- `Hidden only; automatic return possible`
- `Locally severed; broader rotation still pending`

The verdict must be stronger than a generic `Offline` badge.

## Detailed widgets

### Widget A — Existence matrix

Rows for:

- local row
- local bytes
- local authority
- linked cohort
- external retainers
- archive/history

Columns for:

- present
- absent
- degraded
- unknown
- proof basis

### Widget B — Return triggers

A timeline card listing exactly what event would make the subject relevant again.

### Widget C — Full-severance ladder

A small ladder showing stronger actions still available.

### Widget D — Confidence and blind spots

Show whether the system knows external retainers exactly or only probabilistically.

## CLI parity

Minimum commands:

- `anonsync absence explain <object>`
- `anonsync absence matrix <object>`
- `anonsync absence return-triggers <object>`
- `anonsync absence full-severance <object>`

## Non-goals

This spec does **not** define:

- the actual rotate/reissue execution flow
- archive restore or resurrection UX
- discovery internals
