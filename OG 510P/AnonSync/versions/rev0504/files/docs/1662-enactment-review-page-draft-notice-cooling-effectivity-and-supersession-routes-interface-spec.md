# Enactment review page — draft, notice, cooling, effectivity, and supersession routes

## Purpose

This page is the operator workspace for deciding where a typed act sits in its lifecycle right now.
It exists so the archive can distinguish `we executed something` from `the effect is fully in force`.

The page must answer:

> given the current signatures, notice delivery, cooling timers, objections, and later events, what lifecycle state is this act in now, what stronger effect is still blocked, and what supersession or withdrawal routes remain alive?

## Mandatory review sections

### A. Candidate-act section

- requested action family
- current lifecycle state
- nearest weaker state already earned
- next stronger state not yet earned
- urgency class
- whether the act is protective, revisable, or irreversible

### B. Execution section

- execution request submitted or not
- preconditions satisfied or missing
- who executed or attempted execution
- exact execution timestamp if executed
- blockers preventing execution if not yet executed

### C. Notice section

- required notice cohort
- delivered recipients
- missing recipients
- acknowledged recipients
- why any delivery is missing or disputed
- whether missing notice blocks only stronger effectivity or the act itself

### D. Timer section

- cooling start time
- cooling end time
- contest window open or closed
- whether objection during cooling froze effectivity
- whether expedited adjudication replaced ordinary cooling

### E. Supersession section

- later acts that might supersede this one
- whether the later act narrows, widens, or withdraws this effect
- narrower truths preserved if this act is withdrawn
- whether reopen is available now
- strongest sentence still blocked because supersession is unresolved

## Required route outcomes

The page must be able to distinguish at least these outcomes:

- draft remains non-binding
- execution valid but notice incomplete
- notice complete but cooling still running
- protective effect effective now, irreversible effect still pending
- effect fully effective but contest window still open
- effect superseded by narrower later act
- effect reopened and partially withdrawn with receipt lineage preserved

## Required comparisons

The review must keep these comparisons explicit:

- `executed now` vs `effective now`
- `some recipients notified` vs `required cohort completed`
- `cooling started` vs `cooling satisfied`
- `protective effect in force` vs `irreversible closure in force`
- `later act exists` vs `earlier act superseded`
- `reopened` vs `never executed`

## Failure modes the page must prevent

- mistaking a sent notice for completed notice
- mistaking a completed notice for cooling completion
- letting a later narrower act silently erase the earlier wider act without a supersession map
- flattening contest-open and contest-closed into one `effective` badge
- saying `final` when only a protective or provisional effect is actually in force

## Stronger-sentence guard

The review may say `final waiver was executed, notice reached three of four required recipients, protective freeze is effective, but irreversible closure remains blocked pending final notice and cooling`.
It may not say `closed` until the exact stronger lifecycle state is honestly earned.
