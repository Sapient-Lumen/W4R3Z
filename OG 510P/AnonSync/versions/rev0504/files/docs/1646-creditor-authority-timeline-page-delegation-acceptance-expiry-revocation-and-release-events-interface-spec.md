# Creditor authority timeline page — delegation, acceptance, expiry, revocation, and release events

## Purpose

This page is the time-ordered witness for how settlement authority changed.
It must answer:

> who could speak for this creditor at each point in time, when did that power narrow or expire, which actions were signed under which scope, and which later events can reopen or invalidate those actions?

## Mandatory event classes

### A. Identity-and-role events

- principal named or reidentified
- representative role attached
- role occupied by new holder
- role exit or suspension
- linked-device or certificate continuity change noted

### B. Delegation events

- delegation granted
- delegation accepted
- delegation scope expanded
- delegation scope narrowed
- countersign requirement added or removed
- delegation expired
- delegation revoked

### C. Action events

- settlement offer received
- partial relief accepted
- capped settlement signed
- waiver attempted
- waiver rejected as over-scoped
- probation lift requested
- final release signed

### D. Challenge events

- authority challenged
- counterevidence filed
- role mismatch discovered
- relink or certificate takeover questioned
- prior closure reopened
- prior stronger sentence withdrawn

## Required fields per event

- event time
- actor presenting or validating the event
- authority state immediately before the event
- authority state immediately after the event
- strongest sentence gained or lost
- whether any prior signed action is now contestable

## Required comparisons

The timeline must keep these comparisons explicit:

- `delegation granted` vs `delegation still current`
- `partial settlement accepted` vs `full release signed`
- `role change observed` vs `authority revalidated`
- `certificate continuity changed` vs `representation preserved`
- `administrative close` vs `final closure`

## Failure modes the page must prevent

- losing track of which scope existed when a release was signed
- collapsing role continuity into authority continuity
- letting revocation erase earlier narrower valid acts without explanation
- allowing later convenience edits to rewrite who actually had power at the time
- forgetting that a reopened case may leave some prior partial acts intact while invalidating the stronger sentence

## Stronger-sentence guard

The timeline may show `partial repayment accepted under limited delegation on day 5; full waiver attempted and rejected on day 9`.
It may not collapse those into `case closed on day 5`.
