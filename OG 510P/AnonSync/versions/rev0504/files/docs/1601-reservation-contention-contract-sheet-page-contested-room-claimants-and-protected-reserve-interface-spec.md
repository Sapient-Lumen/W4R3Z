# Reservation contention contract sheet page — contested room, claimants, and protected reserve

## Purpose

This page is the canonical object for any case where two or more future-room claimants compete for the same promise capacity or protected reserve.
It must answer the first operator question before any winner is declared:

> what exact room is contested, who is claiming it, what reserve may not be touched, and what stronger promise would become possible if the room were freed?

## Primary questions the page must answer

1. What capacity slice is actually contested?
2. Which claimants are inside the contest and which are merely adjacent background load?
3. What portion is ordinary free room versus protected reserve?
4. What deadlines, service classes, fairness rules, or policy classes bind the allocation?
5. What stronger promise or reservation stays blocked until a verdict is made?

## Required fields

### A. Contested-room identity

- capacity pool name
- current free room estimate
- protected reserve amount
- reserve policy source
- contest open time
- review deadline

### B. Claimant table

Each claimant row must include:

- claimant name
- claimant class (`soft-hold`, `hard-reservation`, `protected-reserve request`, `urgent override request`, `recovery make-good request`, `ordinary future demand`)
- scope requested
- earliest-needed time
- expiry time
- owner
- current doctrine weight
- starvation age
- current stronger sentence blocked if denied

### C. Arbitration constraints

- protected-reserve floor
- anti-starvation rule
- emergency-preemption rule
- split-allocation permission
- co-sign requirement if any
- mandatory no-touch claimants

### D. Risk and consequence block

- consequence if claimant wins
- consequence if claimant loses
- consequence if claimant is deferred
- consequence if reserve is breached
- cross-impact on already-published promises

## Required states

The page must keep these states separate:

- `contest-open`
- `waiting-for-missing-fact`
- `eligible-for-verdict`
- `winning-claimant-proposed`
- `split-allocation-proposed`
- `preemption-proposed`
- `defer-proposed`
- `deny-proposed`
- `verdict-published`
- `contest-closed`

## Page obligations

- never collapse claimants into one blended demand number
- never hide protected reserve behind generic remaining capacity
- never let a prior manual override act as silent doctrine without being re-shown here
- always preserve the strongest blocked sentence for each losing claimant
- always link forward to arbitration review and backward to capacity and reservation receipts

## Stronger-sentence guard

The page may say `capacity is contested`.
It may not say `winner decided` until the arbitration review publishes a typed basis.
It may not say `everyone is accommodated` unless protected reserve, split logic, and claimant-specific outcomes are all explicit.
