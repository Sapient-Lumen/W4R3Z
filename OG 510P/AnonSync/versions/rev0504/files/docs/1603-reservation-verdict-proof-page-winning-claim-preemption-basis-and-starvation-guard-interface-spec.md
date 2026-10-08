# Reservation verdict proof page — winning claim, preemption basis, and starvation guard

## Purpose

This page is the durable proof that a contention verdict really happened and why it can be relied on later.

## Required proof blocks

### A. Contest identity

- contention case id
- contested room scope
- verdict time
- decision authority
- co-signers if required

### B. Winning-basis block

- winning claimant
- doctrine class supporting the winner
- reserve rule applied
- fairness rule applied
- whether preemption occurred
- whether allocation was split

### C. Losing-claimant preservation block

For every non-winning claimant preserve:

- claimant identity
- outcome (`split`, `deferred`, `denied`, `preempted`)
- scope not granted
- review time or release trigger
- starvation-protection timer
- strongest blocked sentence still unavailable

### D. Protected-reserve proof

- reserve floor before verdict
- reserve floor after verdict
- whether reserve was touched
- if touched, emergency authority and restoration plan

### E. Confidence and fragility block

- missing fact count
- provisional versus final verdict class
- invalidators
- auto-reopen triggers

## Public truth classes

The page must keep these claims separate:

- `winner-selected`
- `room-allocated`
- `reserve-preserved`
- `reserve-breached-under-emergency`
- `loser-protected-from-starvation`
- `loser-deferred-without-protection` 
- `verdict-provisional`
- `verdict-final`

## Stronger-sentence guard

The page may say `claimant A currently wins this room`.
It may not say `the planning conflict is solved` unless every losing claimant has a preserved route, expiry, or doctrine-grounded denial.
It may not say `reserve integrity maintained` if any protected reserve was borrowed without restoration terms.
