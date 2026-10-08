# Action matrix timeline page — threshold change, cooling window, and executed-act events

## Purpose

This page is the time-ordered witness for how executable actions changed during the case.
It must answer:

> at each point in time, which typed acts were available, which stronger acts were blocked, what cooling or contest windows were running, and which executed act changed later rights?

## Mandatory event classes

### A. Matrix-definition events

- action row created
- threshold changed for an action row
- named-seat requirement added or removed
- reversibility class changed
- cooling window rule added, shortened, or removed
- reopen condition changed

### B. Readiness events

- coalition becomes sufficient for a narrow act
- coalition becomes sufficient for a stronger act
- objection blocks an irreversible act
- cooling window starts
- cooling window completes
- contest window opens or closes

### C. Execution events

- funds acknowledged
- provisional settlement accepted
- capped settlement executed
- final waiver executed
- probation lifted
- future-burst normalization executed
- successor appointed
- predecessor act ratified
- protective freeze executed
- reopen executed

### D. Narrowing and withdrawal events

- stronger act blocked again
- executed act reopened
- scope narrowed
- residue restored as open
- probation reinstated
- future-burst normalization withdrawn

## Required fields per event

- event time
- action family affected
- readiness state before the event
- readiness state after the event
- strongest sentence gained or lost
- cooling or contest timer state
- surviving weaker acts after the event

## Required comparisons

The timeline must keep these comparisons explicit:

- `ready to execute` vs `executed`
- `cooling window running` vs `cooling window satisfied`
- `probation lifted` vs `future burst normalized`
- `successor appointed` vs `prior act ratified`
- `reopen executed` vs `all prior acts void`

## Failure modes the page must prevent

- forgetting that a stronger act may have been unavailable when a weaker act executed
- flattening readiness and execution into one timestamp
- losing surviving weaker acts after a stronger act is withdrawn
- forgetting that cooling windows are action-specific rather than case-global by default
- treating reopen as if it erased every earlier narrow truth automatically

## Stronger-sentence guard

The timeline may show `day 3: funds acknowledged; day 5: provisional settlement executed; day 8: final waiver became eligible after cooling; day 9: reopen executed, final waiver withdrawn, receipt and provisional acceptance preserved`.
It may not flatten that into `closed on day 3`.
