# Authority contract page: grant class, delegability, and retained-material truth interface spec

## Purpose

This page answers one ordinary question:

> what authority does this seat actually hold right now, what stronger authority does it not hold, and what happens to already-held material if we change or revoke it later?

The page exists because operators should not need to inspect folder family, peer lineage, or local-derivative caveats just to understand one seat's contract.

## Core decision

Every live seat that can read, write, delegate, or be revoked must render one first-class **Authority contract** page.
That page owns:

- grant class
- delegation ceiling
- mutation path
- retained-material truth
- derivative dependence
- strongest safe sentence

## Fixed page order

1. seat strip
2. grant class card
3. delegation card
4. mutation path card
5. retained-material card
6. derivative dependence card
7. receipt / lineage rail

### 1) Seat strip

Show:

- seat label
- principal or seat family
- current grant class
- origin family
- strongest next-safe action

Grant classes must include at minimum:

- `observe-only`
- `write-without-delegate`
- `delegate-within-ceiling`
- `owner-like-admin`
- `derived-local-narrowing`
- `linked-own-seat`
- `revoked-future-updates`

### 2) Grant class card

Publish:

- what this seat may presently do
- what it may not do
- whether the grant is live policy or the residue of an artifact that has already been consumed
- whether the seat is native, imported, linked, derived, downgraded, or superseded

### 3) Delegation card

Show clearly:

- may this seat invite or issue onward authority?
- if yes, what ceiling may it delegate?
- if no, what nearby stronger seat would be required?
- whether downstream delegation is direct, approval-gated, or forbidden

### 4) Mutation path card

The page must say which verb family applies for change:

- `edit existing live policy`
- `issue successor artifact`
- `remove and reconnect`
- `lower only`
- `blocked`

This card exists to stop operators from assuming every permission change is a live edit.

### 5) Retained-material card

This card publishes the revocation truth in one sentence family:

- what future motion stops if revoked or downgraded
- what already-held material remains local to the seat
- whether prior copies remain usable, merely inspectable, or administratively orphaned
- whether cleanup or reclamation is a separate later workflow

### 6) Derivative dependence card

Publish:

- whether this seat depends on a source seat or parent line
- whether it can exceed, match, or only narrow source authority
- what source changes auto-lower or invalidate it
- whether source removal disconnects or destroys this seat

### 7) Receipt / lineage rail

Show linked change receipt, downgrade receipt, revocation receipt, or successor receipt when available.

## Rules

### Rule 1 — grant class must not be inferred from iconography alone

A pencil, shield, chain, or linked-device badge is not enough.
The contract page must state the actual authority.

### Rule 2 — delegability must be explicit

`can write` and `can delegate` are different powers and must never collapse into one label.

### Rule 3 — retained material must stay adjacent to revocation meaning

Never let `revoke access` sound like remote deletion unless that stronger effect is actually true.

### Rule 4 — derivative seats publish their narrowing

A local or downstream derivative must always state what stronger source authority it depends on and what stronger action it cannot do.

## Acceptance criteria

A later operator can:

- tell what this seat can do now
- tell whether it may delegate onward
- tell whether a requested change is live mutation or reissue
- tell what bytes remain after revocation or downgrade
- reopen the right workflow from this page without reading support prose
