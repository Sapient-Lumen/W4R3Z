# Grant change page: desired delta, live-mutation verdict, and epoch boundary interface spec

## Purpose

The archive already has strong member-access doctrine, subject-class doctrine, and revocation doctrine.
This document makes the ordinary page concrete.

The page exists to answer one ordinary operator question:

> for this member on this subject, am I truly changing the existing grant in place, or am I crossing a boundary that requires a successor grant epoch?

## Core decision

Every editable member grant must own one first-class **Grant change** page.
That page is the semantic home of:

- current grant
- requested delta
- live-mutation verdict
- class and lineage fences
- descendant impact preview
- epoch-boundary verdict

The product must not let a dropdown of roles stand in for this page.

## Primary page layout

The page always renders the same top-level regions in the same order:

1. member-and-subject strip
2. current-grant card
3. requested-delta card
4. live-mutation verdict card
5. descendant-impact card
6. epoch-boundary card
7. recent grant-change receipts
8. expert details drawer

### 1) Member-and-subject strip

Show:

- member or seat
- subject
- current operator authority
- strongest next-safe action
- whether the page is previewing a change or reviewing one already applied

The strip should answer `whose authority am I changing on what?`

### 2) Current-grant card

Show:

- right currently in force
- grant origin
- onward-share ceiling now
- artifact or approval event that created the current grant
- whether the current grant is direct, inherited, descendant-derived, or class-flattened

This card should answer `what exact grant exists right now?`

### 3) Requested-delta card

Show:

- requested new right
- whether the change is narrow, widen, revoke, freeze-future-updates, or promote to stewardship
- whether the operator is attempting to preserve current artifact family or is willing to issue a successor artifact
- whether the request includes downstream cleanup expectations that exceed simple revocation

This card should answer `what exact change is being requested?`

### 4) Live-mutation verdict card

Show one explicit verdict:

- `live in-place mutation available`
- `live mutation available but narrower than requested`
- `live mutation blocked by subject class`
- `live mutation blocked by derivative lineage`
- `live mutation blocked by current operator role`
- `successor artifact required`

Also show:

- which layer supplied the fence
- whether the same requested change would be live-editable on an adjacent class
- whether the verdict differs for direct member versus descendant local derivative

This card should answer `can this grant honestly be changed in place?`

### 5) Descendant-impact card

Show:

- whether downstream local derivatives, attached descendants, or inherited seats will narrow automatically
- whether they require separate review
- whether any already-issued downstream grants remain at prior ceiling
- whether the current requested delta will split the member into parallel epochs rather than one continued lineage

This card should answer `what else changes if I apply this delta?`

### 6) Epoch-boundary card

Show:

- whether the requested change preserves the same grant epoch or creates a successor
- which live artifacts must be retired, superseded, or left active
- whether peers on the old epoch continue syncing among themselves
- whether the operator must reissue, reconnect, or choose a new claim lane

This card should answer `am I editing this grant or replacing it with a new epoch?`

### 7) Recent grant-change receipts

Show recent receipts with:

- member
- subject
- prior right
- requested delta
- live-mutation verdict
- epoch-boundary verdict
- action taken

### 8) Expert details drawer

Hide raw lineage IDs, ACL serials, certificate traces, and transport-level continuity details behind an expert drawer.
They matter, but they are not the semantic center.

## Compact row contract

A trustworthy compact row should preserve the following order:

1. member phrase
2. current-right phrase
3. requested-delta phrase
4. mutation / epoch phrase
5. strongest next action

Example:

```text
Alex / Fedora seat   current: RW via direct approved grant   requested: narrow to RO   live mutation blocked by derivative lineage; successor artifact required   Review reissue plan
```

## Acceptance criteria

This spec is satisfied when:

- in-place change and successor-epoch change are visibly different answers
- class fence and operator-role fence are visibly different answers
- descendant impact is previewed before apply
- the page states whether old continuity islands remain after the change
- the product emits receipts for meaningful grant changes rather than outsourcing memory to peer-list drift
