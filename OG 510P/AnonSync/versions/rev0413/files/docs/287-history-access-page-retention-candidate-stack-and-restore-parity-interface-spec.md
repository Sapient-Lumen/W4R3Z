# History access page — retention, candidate stack, and restore parity interface spec

## Purpose

The archive already has history/conflict ideas and fetchability language.
What it still lacked was one ordinary page for the practical operator question:

> what versions or deleted copies are actually retained here, where are they accessible from this seat, which candidate is safest to reintroduce, and what restore consequences follow?

This page exists so history/Archive truth does not depend on hidden folders, platform asymmetry, or timestamp folklore.

## Core rule

History is not just storage.
It is an operator-facing continuity surface.
A serious restore page must tell the operator:

- retention window
- access parity on the current seat
- ordered candidate stack
- restore collision risk
- resulting object state after restore

## Fixed review order

Every serious history-access page should render the same sections in the same order:

1. **Retention and access verdict**
2. **Candidate stack**
3. **Restore destination and collision review**
4. **Resulting lineage after restore**
5. **Receipt and expiry truth**

### 1) Retention and access verdict

This section should answer:

- what retention policy applies here
- whether history is accessible from the current seat natively, indirectly, or not at all
- whether current access is `readable`, `restorable`, `browse-only`, or `no-local-access`

The operator must be able to answer: **what history exists here, and can this seat actually use it?**

### 2) Candidate stack

This section should show restore candidates in an explicit ordered stack with at least:

- candidate identifier
- captured time
- semantic class (`deleted-copy`, `prior-version`, `quarantine`, `manual-snapshot`)
- provenance
- freshness / confidence note

The operator must be able to answer: **which version is newest, which is oldest, and which semantic class each candidate belongs to?**

### 3) Restore destination and collision review

This section should show:

- current destination path
- whether restore will replace, fork, rename, or stage aside
- whether a newer live version already exists
- whether the restore should create a review branch rather than overwrite directly

The operator must be able to answer: **what exactly happens when I restore this candidate?**

### 4) Resulting lineage after restore

This section should show:

- whether restore creates a new live head, a side-by-side branch, or a staged artifact
- whether remote propagation follows immediately or waits for review
- whether the restored candidate becomes the new full-copy witness locally

The operator must be able to answer: **how does restore change current reality, not just storage contents?**

### 5) Receipt and expiry truth

This section should show:

- which candidate was selected
- how long other candidates remain retained
- whether restore consumed, duplicated, or preserved the retained candidate
- which receipt proves the action later

## States

Use a small stable vocabulary:

- `history readable`
- `history restorable`
- `history browse-only`
- `seat lacks history access`
- `restore collision review`
- `restore staged`

## Main surface

A compact **History access** card should show:

- retention verdict
- count of retained candidates
- access parity on this seat
- primary action: `Inspect history access`

## Detailed surface

The detailed page should provide five panes.

### Pane A — Retention strip

Shows:

- subject
- policy horizon
- current seat access class
- latest retained candidate age

### Pane B — Candidate stack

Columns:

- rank
- candidate id
- semantic class
- captured time
- size / subtree scope
- recommended action

### Pane C — Destination review

Columns:

- restore destination
- collision verdict
- after-state class
- propagation class

### Pane D — Alternatives

Rows may include:

- `Restore in place`
- `Restore as side branch`
- `Stage for compare`
- `Export only`
- `Hold and do nothing`

### Pane E — Receipts and expiry

Shows:

- restore receipts
- candidate-expiry schedule
- retained/not-retained consequences

## CLI parity

Minimum commands:

- `anonsync history show <subject> [<path>]`
- `anonsync history review <subject> <candidate-id>`
- `anonsync history restore <review-id>`
- `anonsync history export <candidate-id> --target <path>`

## Acceptance criteria

A user can:

- tell what history exists and whether the current seat can access it natively
- inspect retained candidates in a stable ordered stack
- preview restore collisions and after-state before apply
- choose restore-in-place versus branch/stage deliberately
- prove later which candidate was restored and what expiry truth remained
