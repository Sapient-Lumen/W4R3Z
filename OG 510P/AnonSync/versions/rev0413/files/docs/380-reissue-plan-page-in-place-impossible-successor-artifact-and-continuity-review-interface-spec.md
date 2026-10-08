# Reissue plan page: in-place impossible, successor artifact, and continuity review interface spec

## Purpose

The archive already has strong continuity, reconnect, and reviewed-draft doctrine.
This document makes the ordinary page concrete.

The page exists to answer one ordinary operator question:

> when the desired change cannot honestly happen in place, what exact successor artifact, continuity plan, and retirement plan will replace the old grant epoch?

## Core decision

Whenever a requested access change is not truly live-editable, the product must open one first-class **Reissue plan** page.
That page is the semantic home of:

- reason in-place change failed
- successor artifact choice
- continuity and path-bind plan
- retirement plan for older artifacts / epochs
- expectation-management for peers
- reissue receipts

The product must not collapse this into `remove and share again`.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. source-epoch strip
2. in-place-impossible card
3. successor-artifact card
4. continuity-plan card
5. retirement-plan card
6. peer-expectation card
7. recent reissue receipts
8. expert details drawer

### 1) Source-epoch strip

Show:

- subject
- current member or target lane
- source grant epoch or artifact family
- requested end state
- strongest next-safe action

The strip should answer `what am I trying to replace with what?`

### 2) In-place-impossible card

Show one explicit reason:

- `subject class forbids live mutation`
- `derivative lineage forbids live mutation`
- `current operator role cannot perform in-place change`
- `artifact family lacks mutable identity-bearing grant`
- `requested change would merge or split continuity dishonestly`

Also show:

- whether a nearby class or lane would support live change
- whether the failure is permanent or only current-seat-specific

This card should answer `why can this not honestly be edited in place?`

### 3) Successor-artifact card

Show:

- exact successor artifact family
- claim lane options
- resulting rights ceiling
- approval / expiry / use-budget posture
- whether the successor preserves semantic intent exactly or only approximates it with a narrower / broader contract

This card should answer `what exact thing will replace the old access path?`

### 4) Continuity-plan card

Show:

- whether existing path / bytes can be reused safely
- whether the target must disconnect first
- whether reconnect or manual rebind is required
- whether the successor remains in the same subject or creates a new governance epoch / derivative
- whether peers on the old epoch continue syncing among themselves after cutover

This card should answer `how does continuity really work across the replacement?`

### 5) Retirement-plan card

Show:

- which old artifacts must be revoked, expired, or merely marked historical
- whether old approvals or remembered trust survive
- whether old descendants stay live until separate retirement work
- whether old epoch artifacts remain dangerous because they still create access elsewhere

This card should answer `what must be retired so the old epoch does not keep running?`

### 6) Peer-expectation card

Show:

- what the affected peer will experience (`new claim required`, `path choice required`, `same bytes new authority`, `temporary interruption`, `manual reconnect needed`)
- whether the new path changes names, path suggestions, or visible peer grouping
- what warnings must be acknowledged before the plan is applied

This card should answer `what will the other side think is happening, and how do I keep that honest?`

### 7) Recent reissue receipts

Show recent receipts with:

- source epoch
- reason reissue was required
- successor artifact chosen
- continuity verdict
- retirement actions opened
- apply / abort outcome

### 8) Expert details drawer

Hide raw key / certificate material, protocol traces, and bind-diff evidence behind an expert drawer.
They matter, but they are not the semantic center.

## Compact row contract

A trustworthy compact row should preserve the following order:

1. source-epoch phrase
2. impossibility phrase
3. successor phrase
4. continuity phrase
5. strongest next action

Example:

```text
Standard-key epoch k-119   live RO→RW edit impossible because subject class lacks mutable grant   successor: reviewed RW claim link with approval for all peers   manual reconnect required; old-key peers continue separately until retired   Review reissue
```

## Acceptance criteria

This spec is satisfied when:

- `remove and re-share` and `live edit` are visibly different answers
- successor artifact choice is reviewed before issuance
- continuity reuse and governance replacement are visibly different answers
- retirement of older artifacts is part of the same plan, not a forgotten afterthought
- the product emits receipts for reissue plans rather than outsourcing memory to ad hoc support rituals
