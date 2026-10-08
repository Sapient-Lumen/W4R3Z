# Policy-family timeline page — promotion, deprecation, split, merge, rollback, and sunset events

## Purpose

This page turns policy-family history into a legible event stream so later operators can answer:

> when did this family become current, when was the predecessor deprecated, when did the split happen, which waivers were re-evaluated, and when did retirement actually become true?

## Core decision

Every policy family needs one durable **Policy-family timeline**.
Promotion, deprecation, split, merge, rollback, and sunset are not footnotes.
They are public lifecycle events.

## Fixed page order

1. family history strip
2. lifecycle event stream
3. subject-posture drift graph
4. waiver migration stream
5. retirement and rollback checkpoints
6. timeline receipt

### 1) Family history strip

Show:

- policy family id
- current profile id and revision
- deprecated predecessors count
- retired predecessors count
- open successor proposals count
- active waiver debt count tied to family changes

### 2) Lifecycle event stream

Render chronologically typed events:

- `published`
- `made-current`
- `deprecated-predecessor`
- `retired-predecessor`
- `split-successor-created`
- `merged-successor-created`
- `world-branch-published`
- `rollback-made-current`
- `sunset-without-successor`
- `history-preserved`

For every event show:

- actor
- affected predecessor/successor ids
- worlds in scope
- subject counts affected
- strongest safe event sentence

### 3) Subject-posture drift graph

Track counts over time for:

- `on-current`
- `on-deprecated`
- `grandfathered`
- `blocked-from-successor`
- `orphaned`
- `rolled-back`

## Hard rule

The graph may not compress `on-deprecated` and `grandfathered` into one line.
Those are different governance truths.

### 4) Waiver migration stream

For every lifecycle event preserve waiver outcomes:

- waiver ids touched
- verdict (`carried`, `re-proved`, `resolved`, `split`, `expired`, `blocked`)
- rereview deadlines moved or created
- unresolved debt after event

## Hard rule

Waiver movement must be visible on the same family timeline as promotion and retirement.
It may not be hidden in a separate waiver-only view.

### 5) Retirement and rollback checkpoints

Publish milestone checkpoints:

- last moment predecessor was still current
- first moment predecessor was merely deprecated
- first moment predecessor became retired
- latest safe rollback point
- latest actual rollback event
- receipt retention horizon

### 6) Timeline receipt

Emit one compact receipt with:

- family id
- current profile id
- latest predecessor id touched
- latest lifecycle event
- subject posture counts now
- waiver migration counts now
- rollback posture now
- strongest safe family-history sentence
- blocked stronger sentence

## Copy rules

- Never say `history shows upgrade` when the truer event was split or merge.
- Never say `old policy disappeared` when it was only deprecated.
- Never say `fully retired since date X` if rollback later made the predecessor current again.
- Never say `no remaining debt` when waiver rereviews are still open from the promotion.
- Never say `stable family` if currentness depends on a world-specific branch.

