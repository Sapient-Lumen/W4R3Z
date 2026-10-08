# Post-bypass reconciliation timeline page: resume, path fork, merge, and trust-return events interface spec

## Purpose

After a return begins, the product still needs one durable page for the events that change what `back to normal` actually means over time:

> when did motion resume, when did path or mode fork, when did merge review complete, when did trust return, and when did we accept a new baseline instead of restoring the old one?

## Core decision

AnonSync must expose one first-class **Post-bypass reconciliation timeline** for every return that lasts long enough to matter, changes structure, or changes what sentence is safe.

## Fixed page order

1. **Timeline header**
2. **Return-history stream**
3. **Structural-shift card**
4. **Requalification ladder**
5. **Sentence-restoration card**
6. **Linked-object hooks**

### 1) Timeline header

Show:

- return id
- current restoration state
- current strongest safe sentence
- last restoration event
- next review or attestation
- current baseline state

Supported `current_restoration_state` values:

- `resume-possible-not-started`
- `motion-restored-structure-pending`
- `merge-or-path-review-pending`
- `partially-requalified`
- `fully-requalified`
- `new-baseline-accepted`
- `reopened-after-failed-return`

### 2) Return-history stream

Each row must include:

- event time
- event class
- impacted scope
- old state
- new state
- withdrawn or restored sentence
- linked proof or review id

Supported `event_class` values:

- `resume-requested`
- `resume-confirmed`
- `reconnect-started`
- `reconnect-completed`
- `new-path-created`
- `existing-directory-merge-started`
- `merge-review-completed`
- `permission-restored`
- `placeholder-posture-changed`
- `attestation-restored`
- `new-baseline-accepted`
- `same-cause-return-failed`

### 3) Structural-shift card

When the selected timeline row changes meaning materially, show:

- what structural fact changed
- old return truth
- new return truth
- whether path parity improved or worsened
- whether trust moved or stayed blocked
- whether rollback remains allowed

Supported `structural_shift_source` values:

- `simple-resume-confirmed`
- `reconnect-landed-new-path`
- `operator-corrected-to-original-path`
- `merge-chose-existing-directory`
- `placeholder-footprint-removed`
- `future-updates-restored`
- `baseline-replaced`
- `trust-restored-after-requalification`

### 4) Requalification ladder

The page must preserve this ladder:

1. `motion-only`
2. `motion-plus-structure-known`
3. `structure-reconciled`
4. `trust-restored`
5. `new-baseline-adopted-or-old-baseline-restored`
6. `reopened-on-return-failure`

Hard rule:

The timeline must preserve the gap between `motion resumed` and `protection restored` whenever that gap exists.

### 5) Sentence-restoration card

Required rows:

- earliest point motion resumed
- earliest point structure matched the target or accepted successor
- actual point trust sentence returned
- witness that allowed stronger sentence
- stronger sentence still blocked if any

Hard rule:

The timeline must show whether the old sentence returned or whether a new weaker or successor sentence replaced it.

### 6) Linked-object hooks

Each hook must show:

- linked object type (case / control / rollout / policy / baseline)
- why it is linked
- whether it reopened automatically
- first required next page
- sentence withdrawn or restored there
