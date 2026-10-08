# Capture brief receipt page — claimed symptom, run outcome, and usable evidence window interface spec

## Purpose

Leave one durable record of what symptom was being pursued, what run actually happened, and whether the resulting evidence window is strong enough to interpret.
This page should answer:

- what brief the run inherited
- what bookmark or time anchor it used
- which participants took part
- whether the target symptom was actually caught
- what evidence window is usable now
- what should reopen or invalidate this receipt later

## Inputs

- incident identifier
- inherited incident brief version
- symptom bookmark if any
- coordinated run outcome
- participant outcomes
- active capture windows and elapsed dwell
- resulting evidence artifacts
- current claim ceiling

## Layout

### A. Brief inheritance strip

Fields:

- incident headline
- brief version used
- target symptom
- bookmark used
- receipt freshness

### B. Run outcome card

Show:

- run state
- target symptom caught or not
- partial-capture notes if any
- participants ready versus missing
- whether the result is usable for local review, witness review, or export

### C. Evidence window card

Show:

- capture start and stop
- dwell achieved versus dwell floor
- event alignment (`before`, `during`, `after`, `uncertain`)
- strongest honest statement about what the evidence window can support
- stronger forbidden statement

### D. Participant and artifact table

Columns:

- participant
- role
- requested artifact family
- run participation state
- returned artifact state
- notes

### E. Reopen and stale boundary card

Show conditions such as:

- newer bookmark supersedes this one
- topology or subject scope changed
- symptom was later caught in a stronger run
- a required participant's run state was actually missing or stale
- chronology trust changed enough to reinterpret timestamps

## Required interactions

- `Copy capture receipt summary`
- `Open incident brief`
- `Open coordinated capture run`
- `Open witness completeness review`
- `Reopen capture planning`
- `Escalate to report send`

## Guardrails

- Never issue a receipt that hides whether the target symptom was actually observed.
- Never imply that a usable artifact window proves the leading explanation unless the receipt says so explicitly.
- Never omit the brief or bookmark version used for the run.
- Never merge `no reproduction` and `capture failed` into one status.
- Never reopen later without preserving this receipt in the incident chronology.

## Output

A durable capture receipt that preserves the claimed symptom, the run actually performed, participant outcomes, usable evidence window, and the exact stale/reopen boundary.
