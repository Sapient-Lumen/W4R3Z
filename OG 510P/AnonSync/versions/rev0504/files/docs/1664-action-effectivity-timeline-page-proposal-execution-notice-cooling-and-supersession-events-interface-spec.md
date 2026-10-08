# Action effectivity timeline page — proposal, execution, notice, cooling, and supersession events

## Purpose

This page is the time-ordered witness for how a typed act moved through its lifecycle.
It must answer:

> at each point in time, was the act merely proposed, executed, noticed, effective, contested, superseded, or withdrawn, and which narrower truths still survived each transition?

## Mandatory event classes

### A. Proposal events

- draft created
- draft edited
- draft abandoned
- execution requested
- execution blocked before attempt

### B. Execution events

- execution performed
- execution rejected
- execution rolled back before notice
- protective effect turned on immediately
- irreversible effect held pending notice or cooling

### C. Notice events

- notice sent
- notice delivered
- notice acknowledged
- notice failed
- required cohort completed
- required cohort reopened because notice became disputed

### D. Timer events

- cooling started
- cooling paused
- cooling resumed
- cooling satisfied
- contest window opened
- contest window closed
- adjudication override applied

### E. Aftermath events

- effect became active for narrow scope
- effect became active for stronger scope
- superseding act issued
- earlier effect narrowed
- earlier effect withdrawn
- reopen executed
- surviving narrower truth preserved in lineage

## Required fields per event

- event time
- lifecycle state before the event
- lifecycle state after the event
- scope affected
- strongest sentence gained or lost
- weaker truths preserved after the event
- exact blocker or unlocker involved

## Required comparisons

The timeline must keep these comparisons explicit:

- `drafted` vs `executed`
- `executed` vs `notice complete`
- `notice complete` vs `effective`
- `protective effect active` vs `irreversible effect active`
- `superseded` vs `withdrawn`
- `reopened` vs `void from the beginning`

## Failure modes the page must prevent

- flattening proposal and execution into one timestamp
- flattening execution and effectivity into one timestamp
- forgetting that notice may complete after execution by days or weeks
- forgetting that supersession can preserve narrower lineage rather than erase it
- forgetting that a reopen may withdraw stronger effect while leaving weaker earlier truths intact

## Stronger-sentence guard

The timeline may show `day 1 draft; day 2 execution; day 3 notice completed for core cohort; day 6 cooling satisfied for undisputed core; day 9 reopen executed and case-wide effect withdrawn while receipt acknowledgment survived`.
It may not flatten that into `resolved on day 2`.
