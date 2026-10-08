# Device-local eviction boundary page: placeholder reversion, disk residue, and reconnect risk interface spec

## Purpose

This review appears when the chosen removal family is local in scope.
It exists to answer one ordinary question before commit:

> after this local-only removal, what still exists here, what remains elsewhere, and what risks come back when I reconnect or re-materialize later?

## When this review must appear

Trigger it for actions such as:

- disconnect this subject on this seat
- clear synced files / revert to placeholders
- remove from this device
- uninstall locally while shared continuity remains elsewhere

## Fixed page order

1. local-boundary summary header
2. local disk / placeholder matrix
3. reconnect and branch-risk section
4. surviving remote continuity section
5. approval footer

### 1) Local-boundary summary header

Show:

- target subject
- requested verb family
- strongest safe sentence after apply
- stronger rejected sentence after apply

### 2) Local disk / placeholder matrix

Columns:

- artifact class
- after apply on this seat
- after apply on other seats
- later fetch / reconnect possible?
- proof freshness

Rows should include at least:

- full local bytes
- placeholders / stubs
- folder path binding
- hidden service material (`.sync`, archive, metadata)
- subject row in local control surface

### 3) Reconnect and branch-risk section

Show:

- whether reconnect is offered later
- whether a new default path may be proposed
- duplicate-branch / `(1)` risk if the default path differs
- whether the old path can be manually rebound
- whether reselection requires a non-empty-path warning

### 4) Surviving remote continuity section

Say plainly:

- which other seats keep ordinary continuity
- whether remote full copies remain required for later re-fetch
- whether placeholders-only risk exists if every seat evicts material

### 5) Approval footer

Require acknowledgement whenever the state created is such as:

- local bytes removed while remote continuity survives
- placeholders removed from the local file system
- reconnect may create a sibling branch by default
- comeback depends on remote full-copy witnesses still existing

## Rules

### Rule 1 — local-only language blocks global-finality wording

The product cannot imply shared deletion when the action is only a local eviction.

### Rule 2 — reconnect risk stays adjacent to remove

Operators must learn about default-path drift before, not after, the removal.

### Rule 3 — local cleanup and hidden service residue stay separate

Removing visible bytes does not imply archive or metadata cleanup.
