# Cohort drift timeline page: live-count history, expiry, hide, and reentry triggers interface spec

## Problem this page solves

A cohort rarely changes only by explicit adds and removals.
It also drifts through:

- peers going offline
- auto-disconnect after dormancy thresholds
- rows hidden for decluttering
- local-share fanout increasing apparent count
- disconnected linked-folder visibility rows appearing
- later reentry of previously hidden or offline participants

The operator needs one place to see how the cohort sentence drifted over time.

## Timeline events this page must preserve

Supported event classes must include:

- `peer-became-live`
- `peer-went-offline`
- `peer-auto-expired-or-disconnected`
- `row-hidden-for-declutter`
- `row-reappeared-on-return`
- `self-derived-branch-added`
- `visibility-only-row-created`
- `severance-confirmed`
- `counting-basis-changed`

## Fixed timeline columns

- event time
- affected row or cohort slice
- previous bucket
- next bucket
- changed counters
- did independent source count change?
- did only visible row count change?
- reopen trigger if the operator made a prior conclusion

## Required summary cards

### A. Live-count drift

Shows how `live_reachable_count` changed over time.

### B. Historical-roster drift

Shows how `historical_roster_count` changed over time.

### C. Independent-source drift

Shows whether real resilience changed or only the apparent count changed.

### D. Reopen triggers

Lists prior receipts or claims that should be reconsidered because of:

- hidden row reappearance
- auto-expiry of a source-capable peer
- new self-derived branch making the count look safer than it is
- return of a formerly offline source peer

## Example safe sentences

- `Visible row count increased from 4 to 5, but independent source count stayed at 1 because the new row is self-derived local fanout.`
- `Historical roster count stayed at 7 while live set fell from 3 to 1 after two peers crossed the dormancy threshold.`
- `A previously hidden offline device reappeared; this changed row visibility and potential future reachability, but live source coverage is still unproved.`

## Hard rules

- no timeline may plot a single `peer count` line without also plotting independent source count
- hide/show actions must be marked as visibility drift, not resilience drift
- local-branch adds must be marked as fanout drift, not independent cohort growth
