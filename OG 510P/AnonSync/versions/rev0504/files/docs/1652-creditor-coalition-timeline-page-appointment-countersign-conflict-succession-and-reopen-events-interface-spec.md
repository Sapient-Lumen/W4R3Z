# Creditor coalition timeline page — appointment, countersign, conflict, succession, and reopen events

## Purpose

This page is the time-ordered witness for how closure sufficiency changed.
It must answer:

> at each point in time, which seats existed, who occupied them, what coalition rule applied, which actions were sufficiently signed, and which later conflicts or successions changed the truth of closure?

## Mandatory event classes

### A. Rule-definition events

- coalition rule established
- countersign requirement added or removed
- quorum threshold changed
- unanimity requirement added or removed
- adjudicator designated or withdrawn

### B. Seat-and-occupancy events

- seat created
- seat filled
- seat vacated
- occupant suspended
- successor appointed
- successor ratified or rejected

### C. Signature events

- payment acknowledged
- partial settlement signed
- countersign added
- countersign refused
- quorum reached
- unanimity reached
- final release attempted
- final release completed

### D. Conflict events

- valid signer objects
- seat dispute opened
- conflict-freeze begins
- adjudication requested
- adjudication resolves conflict
- earlier closure narrowed or withdrawn

### E. Reopen events

- successor authority questioned
- vacancy assumption fails
- stale consent invalidated
- quorum recalculated and lost
- prior finality reopened
- stronger sentence restored or permanently denied

## Required fields per event

- event time
- actor or seat involved
- coalition state immediately before the event
- coalition state immediately after the event
- strongest sentence gained or lost
- whether prior signatures remain countable
- whether partial acts remain valid if stronger acts fail

## Required comparisons

The timeline must keep these comparisons explicit:

- `seat occupied` vs `seat counted`
- `signature present` vs `signature sufficient`
- `quorum reached then` vs `quorum still valid now`
- `successor appointed` vs `successor ratified for prior acts`
- `administrative resolution` vs `final closure`

## Failure modes the page must prevent

- forgetting which threshold applied at the time a signature was recorded
- letting later seat edits silently rewrite earlier sufficiency truth
- losing earlier valid narrow acts when a later strong act fails
- treating successor appointment as retroactive ratification without proof
- collapsing conflict resolution and true finality into one timestamp

## Stronger-sentence guard

The timeline may show `partial settlement valid on day 4 under two-seat quorum; final waiver attempted on day 8 but reopened on day 11 after successor ratification failed`.
It may not flatten those events into `closed on day 4`.
