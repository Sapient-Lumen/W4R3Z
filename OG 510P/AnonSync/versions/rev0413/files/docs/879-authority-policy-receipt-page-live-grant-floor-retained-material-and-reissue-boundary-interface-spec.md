# Authority policy receipt page: live grant floor, retained material, and reissue boundary interface spec

## Purpose

This receipt preserves the policy truth that later operators usually misremember:

> what authority was actually in force, what floor remained after the last change, and whether the result came from live mutation, derivative narrowing, revocation, or successor reissue.

## Core decision

Every meaningful authority action must emit an **Authority policy receipt**.
That includes:

- initial grant
- upgrade
- downgrade
- revocation
- derivative creation
- successor reissue

## Fixed receipt fields

1. receipt header
2. effective grant section
3. mechanism section
4. retained-material section
5. derivative / downstream section
6. reopen boundary

### 1) Receipt header

Show:

- receipt type
- subject
- affected seat or seat family
- issuance time
- actor / authority basis

### 2) Effective grant section

Publish:

- resulting live grant floor
- stronger denied interpretations
- current delegability status
- whether the seat is linked, external, or derivative

### 3) Mechanism section

Publish one mechanism class:

- live policy edit
- derivative narrowing
- revocation of future updates
- successor reissue
- blocked / no-op

### 4) Retained-material section

Publish:

- what remains with the affected seat
- what no longer updates
- whether automatic cleanup was not performed
- strongest safe sentence after the change

### 5) Derivative / downstream section

Publish:

- derivatives affected
- delegates affected
- receipts superseded
- successor artifacts created or required

### 6) Reopen boundary

Publish the next conditions that would invalidate or supersede this receipt.
Examples:

- successor artifact accepted
- source seat removed
- derivative auto-lowered again
- retained-material cleanup attested separately

## Rules

### Rule 1 — receipt must preserve mechanism truth

Later operators should not need to guess whether a change was a live policy mutation or a reissue event.

### Rule 2 — receipt must preserve retained-material truth

A revocation receipt that omits surviving bytes is incomplete.

### Rule 3 — receipt must preserve authority floor, not aspirational ceiling

The stored result is the actual live floor after the action, not the original requested ambition.

## Acceptance criteria

A later operator can reopen the receipt and tell:

- the resulting authority floor
- whether delegation still survived
- what material remained after the action
- whether the change was live mutation or successor reissue
- what future event would supersede the receipt
