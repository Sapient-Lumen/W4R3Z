# Witness completeness review page — required returns, missing witnesses, and claim ceiling interface spec

## Purpose

Decide whether the current witness set is complete enough for an honest conclusion.
This page exists so the operator does not confuse `some evidence came back` with `the case is sufficiently witnessed`.

## Inputs

- incident identifier
- chosen witness set
- required and optional participants
- returned artifacts by participant
- artifact freshness and validity
- contradictions across witnesses
- current leading explanation
- candidate stronger claims

## Primary questions this page must answer

1. Which required witnesses have returned usable evidence?
2. Which required witnesses are still missing or stale?
3. Do the returned witnesses agree, conflict, or leave a gap?
4. What can we say honestly with this witness coverage?
5. Is the next step to close, widen, retry, or escalate?

## Layout

### A. Completeness scoreboard

Fields:

- required witnesses total
- required witnesses returned
- required witnesses missing
- optional witnesses returned
- stale witnesses
- current completeness verdict (`complete-for-current-claim`, `partial`, `blocked`, `contradictory`, `unknown`)

### B. Role coverage matrix

Rows may include:

- source
- destination
- bridge / route witness
- observer / alternate source
- controller / seat-local witness

Columns:

- required now
- returned usable evidence
- stale or incomplete
- not yet requested

### C. Contradiction map

For each conflicting pair or cluster show:

- participants involved
- contradiction summary
- whether contradiction is about chronology, presence, route, queue, or local state
- cheapest next clarifying witness or route

### D. Claim ceiling block

Four lines:

- strongest safe sentence now
- stronger forbidden sentence now
- missing witness or contradiction blocking the stronger sentence
- whether closing now is acceptable or dishonest

### E. Next-step card

Possible recommendations:

- `Issue witness-set receipt and close`
- `Retry missing required witness`
- `Widen witness set`
- `Shrink witness set because redundancy is proven`
- `Escalate to heavier capture`

## Required interactions

- `Approve sufficient witness coverage`
- `Retry missing witness request`
- `Widen witness set`
- `Downgrade requirement after review`
- `Escalate to heavier capture`
- `Issue witness-set receipt`

## Guardrails

- Never treat a missing witness as contradictory evidence.
- Never let one participant stand in for a whole route or share without an explicit justification.
- Never hide stale returns inside a `complete` verdict.
- Never allow closure if the leading claim depends on a missing required witness.
- Never escalate to heavier capture without naming which missing witness question it would replace or answer.

## Output

A reviewed witness-coverage verdict that states whether the case is complete enough for the current claim, what stronger claim is blocked, and what the next cheapest witness step is.
