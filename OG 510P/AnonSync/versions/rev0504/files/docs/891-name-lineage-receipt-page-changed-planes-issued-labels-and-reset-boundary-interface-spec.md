# Name lineage receipt page: changed planes, issued labels, and reset boundary interface spec

## Purpose

This receipt preserves naming truth after mutation.
It answers:

> what name planes changed, what did not, what outward labels were actually issued, and did this event clean up residue or mutate canonical subject identity?

## Core decision

Every non-trivial naming mutation, issuance-label change, or stale-alias reset emits one **Name lineage receipt**.

## Fixed receipt order

1. event summary
2. changed planes
3. untouched planes
4. issued-artifact consequences
5. residue/reset consequences
6. strongest-safe sentence

### 1) Event summary

Show:

- event kind (`canonical retitle`, `local alias edit`, `disk rename`, `recipient-label issuance`, `template change`, `stale-alias reset`, `mixed`)
- subject
- actor
- timestamp
- source review

### 2) Changed planes

List every changed plane with before/after values.

### 3) Untouched planes

List every important untouched plane explicitly.
For example:

- canonical title unchanged
- disk basename unchanged here
- older issued artifacts unchanged
- local alias on other seats unchanged

### 4) Issued-artifact consequences

If any outward artifact was created or reissued, show:

- recipient-facing label shipped
- artifact family
- carrier
- one-off versus template-derived
- whether older artifacts were superseded or left intact

### 5) Residue/reset consequences

If the event cleared or preserved residue, show:

- residue classes cleared
- residue classes preserved
- whether any stale labels remain visible

### 6) Strongest-safe sentence

The receipt must end with one sentence no stronger than the truth actually earned.

Example:

- `This event changed the local alias on seat A and issued one new QR artifact labeled 'Files for Server2'; it did not retitle the canonical subject, rename the disk path, or alter older issued artifacts.`

## Rules

### Rule 1 — unchanged planes must be explicit

The receipt is incomplete if it only lists what changed.

### Rule 2 — issued labels need artifact attribution

A recipient-facing label without its artifact family and carrier is incomplete provenance.

### Rule 3 — reset receipts stay narrow

A reset receipt must state that the action cleaned local residue unless more was truly changed.

### Rule 4 — receipts preserve historical divergence

The receipt must not erase the fact that older labels or artifacts once existed.

## Acceptance criteria

A later operator can reconstruct:

- what exact naming action happened
- what planes changed and stayed untouched
- what labels were shipped outward
- whether residue was cleaned or merely recorded
- which stronger naming claim would be false
