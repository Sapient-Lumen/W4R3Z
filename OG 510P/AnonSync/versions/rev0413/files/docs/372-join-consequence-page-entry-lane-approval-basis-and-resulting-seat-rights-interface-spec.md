# Join consequence page: entry lane, approval basis, and resulting seat rights interface spec

## Purpose

The archive already has strong offer, claim, approval, and member-access doctrine.
This document makes the ordinary page concrete.

The page exists to answer one ordinary operator question:

> if this seat joins through this exact lane, what right will it actually gain, what future scope comes with it, and what has to be reviewed before that becomes real?

## Core decision

Every meaningful join or attach path must own one first-class **Join consequence** page.
That page is the semantic home of:

- entry lane identity
- approval basis
- resulting seat rights
- future-arrival scope
- onward-share ceiling
- continuity and receipt consequences

The product must not let `paste key`, `open link`, `scan QR`, or `link my device` stand alone without this page.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. entry-lane strip
2. artifact and proof card
3. approval-basis card
4. resulting-seat-rights card
5. future-scope card
6. onward-share card
7. recent join receipts
8. expert details drawer

### 1) Entry-lane strip

Show:

- lane family (`linked seat`, `manual claim`, `browser-open claim`, `QR claim`, `local import`, etc.)
- candidate subject
- candidate seat
- strongest next-safe action
- whether the page is previewing a potential join or reviewing one that is already pending

The strip should answer `what exact lane am I evaluating?`

### 2) Artifact and proof card

Show:

- what authority-bearing artifact actually exists
- what carrier or wrapper brought it here
- whether the lane is carrier-only different or artifact-different
- what strong identity proof is already present for the seat or claimant
- what proof is still absent

This card should answer `what is actually being claimed, and how much do we know about who is claiming it?`

### 3) Approval-basis card

Show one explicit approval verdict:

- `fresh review required`
- `auto-admissible by standing policy`
- `auto-admissible by linked-seat relationship`
- `blocked pending stronger proof`
- `artifact valid but current policy refuses auto-join`
- `artifact itself cannot create live access`

Also show:

- which policy layer supplied the verdict
- whether remembered approval is being widened, reused, or not touched
- whether the operator can force a one-time narrower approval instead

This card should answer `why would this join become live, and on what basis?`

### 4) Resulting-seat-rights card

Show:

- resulting seat role or capability set
- whether rights are same-subject rights, derivative-subject rights, or inspect-only rights
- whether local writes will propagate
- whether conflicting local writes will be rejected, quarantined, or overwritten under policy
- whether the seat becomes part of a broader owner-like family or a narrower leaf grant

This card should answer `what can this seat actually do after success?`

### 5) Future-scope card

Show:

- whether future subjects of a linked family will auto-arrive here
- whether the join concerns only one subject or a family relationship
- what default arrival mode the seat will use for later arrivals
- whether this lane changes future scope or only current-subject access

This card should answer `what ongoing relationship am I creating, not just what single bind am I making?`

### 6) Onward-share card

Show:

- whether this seat may share onward
- whether onward-share depends on subject class, resulting role, or separate policy
- whether the seat may only re-share a narrower grant
- whether later grant mutation remains possible from this seat

This card should answer `does success here also create downstream authority?`

### 7) Recent join receipts

Show recent receipts with:

- entry lane
- seat or claimant
- approval basis used
- resulting right shown at the time
- future-scope verdict
- onward-share verdict
- resulting continuation or refusal

### 8) Expert details drawer

Hide raw fingerprints, artifact parse details, browser/OS wrapper metadata, and low-level policy traces behind an expert drawer.
These details matter, but they are not the semantic center.

## Compact row contract

A trustworthy compact row should preserve the following order:

1. lane phrase
2. subject phrase
3. approval phrase
4. resulting-rights phrase
5. strongest next action

Example:

```text
Link claim   Project Atlas   fresh review required; remembered contact narrows proof work but does not auto-admit   resulting seat: RW leaf, no onward share, no future-family auto-arrival   Review consequence
```

## Acceptance criteria

This spec is satisfied when:

- linked-seat join and one-subject join are visibly different answers
- carrier-only differences and artifact-governance differences are visibly different answers
- resulting rights and future scope are shown before commitment
- onward-share ceiling is shown before commitment
- the product emits receipts for meaningful join decisions rather than outsourcing memory to later peer-list interpretation
