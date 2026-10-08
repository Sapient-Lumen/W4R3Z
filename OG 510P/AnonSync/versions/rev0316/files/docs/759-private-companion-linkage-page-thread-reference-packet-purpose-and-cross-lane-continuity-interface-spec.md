# Private companion linkage page — thread reference, packet purpose, and cross-lane continuity interface spec

## Purpose

Confirm how a private evidence packet relates to a broader public or semi-public case.
This page should answer:

- what companion summary or thread this packet belongs to
- what the private packet is meant to add beyond the public artifact
- which details are private-only and why
- whether the link between the artifacts is strong enough for future handoff
- how continuation should move between lanes without losing the case story

This page exists so `mention ticket number` or `include forum link` becomes a typed product object instead of prose ritual.

## Inputs

- companion-case object
- private packet or evidence manifest summary
- destination confirmation for private lane
- public summary reference if any
- operator-entered thread URL / ticket ID / case ID if any
- withheld-detail ledger
- continuation expectations

## Primary questions this page must answer

1. What public or companion artifact does this private packet belong to?
2. What private value does this packet add?
3. Which details remain intentionally private-only?
4. Is the cross-reference durable enough for later responders?
5. What future reply should continue in which lane?

## Layout

### A. Linkage strip

Fields:

- private lane
- companion reference state
- packet purpose
- continuity verdict (`strong`, `provisional`, `weak`, `missing`)

### B. Companion reference card

Show:

- referenced public summary / thread / case id
- reference source (`system-issued`, `imported`, `operator-entered`, `missing`)
- whether the reference resolves cleanly
- ambiguity warnings

### C. Packet purpose card

Show:

- why this packet exists
- what question it is meant to answer
- what it adds beyond the public summary
- what it is *not* claiming to prove on its own

### D. Private-only details card

Show categories withheld from the public side and why, such as:

- raw logs / dumps
- precise identifiers and paths
- peer topology and seat ownership
- timestamps or screenshots too revealing
- licensing/account details

### E. Continuity card

Show:

- whether future discussion should continue publicly, privately, or in both lanes
- what public reply may safely reference the private packet
- what private reply may assume from the public summary
- what conditions reopen summary review or lane review

## Required interactions

- `Confirm companion linkage`
- `Edit reference`
- `Strengthen public summary first`
- `Split packet further`
- `Keep packet private-only without public companion`
- `Issue companion receipt`

## Guardrails

- Never allow `same case` without a visible reference basis.
- Never let a private packet rely only on operator memory for continuity.
- Never claim that a companion reference proves package sufficiency.
- Never let public-safe and private-only details blur together.
- Never hide whether the continuation contract is one-lane or dual-lane.

## Output

A reviewed private-companion-linkage object that preserves companion reference, packet purpose, private-only scope, continuity verdict, and next-lane expectations.

