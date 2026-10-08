# Witness-set receipt page — participant scope, actual returns, and reopen boundary interface spec

## Purpose

Leave one durable record of what witness plan this incident used and what actually came back.
This page should answer:

- which participants were required and optional
- which roles they played
- what evidence actually arrived
- which witnesses remained missing or deferred
- what claim ceiling followed from that coverage
- what condition should reopen or widen the witness plan later

## Inputs

- incident identifier
- witness-set strategy
- participant list
- required versus optional status
- actual artifact returns
- completeness verdict
- strongest safe sentence
- reopen / escalation triggers

## Layout

### A. Witness strategy strip

Fields:

- witness-set strategy
- selection basis
- issue headline
- subject scope
- receipt freshness

### B. Participant outcome table

Columns:

- participant
- role
- duty level
- requested artifact family
- returned state (`complete`, `partial`, `missing`, `deferred`, `unreachable`)
- notes

### C. Coverage summary card

Show:

- whether the witness set was complete for the current claim
- which witnesses were missing but non-blocking
- which stronger claims remained blocked
- whether the witness set was later widened or intentionally held narrow

### D. Safe-language card

Show:

- strongest safe sentence
- stronger forbidden sentence
- basis for the safe sentence
- exact missing witness or contradiction preventing the stronger sentence

### E. Reopen boundary card

Show conditions such as:

- required witness later returns
- contradiction persists after retry
- topology changes and witness roles shift
- heavier capture becomes justified
- recurrence opens a new or widened incident

## Required interactions

- `Copy receipt summary`
- `Open incident conclusion receipt`
- `Reopen witness planning`
- `Reissue missing witness request`
- `Escalate to external packet`

## Guardrails

- Never emit a witness receipt that hides missing required participants.
- Never imply that a claim was fully proved if the completeness verdict was only partial.
- Never omit participant roles from the receipt.
- Never merge optional and required witness outcomes into one undifferentiated count.
- Never reopen the incident later without preserving this receipt in the chronology.

## Output

A durable witness-planning receipt that preserves participant scope, actual returns, missing coverage, safe-language ceiling, and the exact boundary for reopening.
