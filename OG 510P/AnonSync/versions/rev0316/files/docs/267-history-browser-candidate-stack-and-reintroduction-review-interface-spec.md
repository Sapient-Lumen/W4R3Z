# History browser, candidate stack, and reintroduction review interface spec

## Purpose

The archive already has rollback provenance, restore candidates, and reintroduction doctrine.
What it still lacked was a fixed page contract for the **History / Restore** workbench surface.

This document answers one everyday operator question:

> when I need an earlier file state, what browser lets me see candidate versions, current live state, provenance strength, and the difference between local inspection versus live reintroduction without filesystem scavenger hunts or receipt archaeology?

Current Resilio docs sharpen this need because they still split restore meaning between hidden archive storage, a separate History view, and manual restore timing caveats.
AnonSync should keep those truths together.

## Core decision

The History browser is not a raw event feed.
It is a **candidate stack browser** for recoverable earlier states.

Each row must keep these truths adjacent:

1. what path or object family this candidate belongs to
2. what is true about the current live path now
3. what recoverable candidate exists
4. how strong the provenance is
5. what reintroduction shape is safest
6. where deeper review or receipts live

## Browser layout

The page should have three persistent regions:

1. **Path list / candidate list**
2. **Current path answer pane**
3. **Candidate stack / restore review pane**

On narrow surfaces these may stack, but the semantic regions should remain the same.

## Row anatomy

Each browser row should render:

1. **Path slot**
2. **Current-live slot**
3. **Best candidate slot**
4. **Provenance slot**
5. **Primary-action slot**
6. **Review / receipts slot**

### Path slot

Show the path or subject label plus any tombstone / renamed-from marker.

### Current-live slot

Show one honest phrase such as:

- `Missing now`
- `Present but newer`
- `Conflicted now`
- `Deleted share-wide`
- `Locally absent, share still live`

### Best candidate slot

Show the strongest recoverable candidate summary such as:

- `1 prior local version`
- `3 archived remote versions`
- `Rollback bundle available`
- `History only, no bytes`

### Provenance slot

Show:

- `Peer-attributed`
- `Local history`
- `Archive-only`
- `Incident bundle`
- `Unknown authorship`

### Primary-action slot

Show only the safest next honest verb:

- `Inspect`
- `Restore locally`
- `Compare`
- `Review reintroduce`
- `Export`

### Review / receipts slot

Jump to:

- restore review
- rollback receipts
- related conflict case
- deeper provenance timeline

## Candidate stack rules

Selecting a row should open a candidate stack ordered by recovery relevance, not just timestamp.
The default order should prefer:

1. same-path, strong-provenance, low-collision candidate
2. same-path, weaker-provenance candidate
3. side-branch or orphaned recovered bytes
4. evidence-only rows with no recoverable bytes

This order answers `what can I honestly do next?`, not merely `what happened last?`

## Fixed review order

The review pane should render sections in this order:

1. **Current path answer**
2. **Candidate ladder**
3. **Provenance and continuity**
4. **Restore shape choices**
5. **Collision and propagation guardrails**
6. **Receipt promise**

### 1) Current path answer

Show the current live posture first.
The operator must not have to infer whether the restore is inspection-only or a live overwrite candidate.

### 2) Candidate ladder

For each candidate, show:

- capture time
- capture reason
- storage class
- retention horizon
- whether bytes are directly available now

### 3) Provenance and continuity

Show:

- actor / seat when known
- whether the candidate belongs to the same live line
- whether it is orphaned, side-branch, or incident-preserved
- provenance confidence

### 4) Restore shape choices

Render explicit actions:

- `Restore locally only`
- `Open comparison fork`
- `Review live reintroduction`
- `Export bytes`

### 5) Collision and propagation guardrails

Show:

- current path occupancy
- newer-live-state collision risk
- whether live reintroduction would propagate
- whether settlement or preservation review is required

### 6) Receipt promise

Show which durable object will result:

- local restore receipt
- rollback receipt
- share reintroduction review receipt
- export receipt

## Search and grouping

The browser should support grouping by:

- path family
- recent deletion / overwrite incident
- share
- provenance class
- recovery action class

And search by:

- path
- candidate ID
- actor / seat
- receipt ID
- incident / conflict reference

## Batch rules

Batch operations should be rare and tightly limited.
Allowed examples:

- `Export 4 local-only candidates`
- `Open compare for 3 same-incident paths`

Disallowed examples:

- `Restore selected`
- `Reintroduce all`

History recovery is too scope-sensitive for generic bulk verbs.

## Relationship to nearby specs

This spec is the browser/page companion to:

- `48-history-conflict-and-rollback-provenance-spec.md`
- `174-restore-history-archive-and-share-safe-reintroduction-interface-spec.md`
- `72-conflict-adjudication-and-path-collision-review-spec.md`

Those documents define the semantics of restore and rollback.
This one fixes the page that should let operators navigate those semantics without hidden storage or mental reconstruction.
