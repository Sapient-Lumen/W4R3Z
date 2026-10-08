# Hydration queue admission page: source witness, budget, and ghost-risk interface spec

## Purpose

This page exists because a pending local-presence request can fail for reasons that ordinary queue UI hides.
A subject may be visible and even prioritized while still lacking a durable path to truth because:

- the only full-copy witness is offline
- all known witnesses are placeholders
- source counts are stale
- queue admission is blocked by budget
- a ghost/no-source condition has already been observed

The operator question is:

> should this subject even be admitted as an honest pending local promise, or has source or budget reality already weakened it too much?

## Core decision

AnonSync should make **hydration queue admission** first-class.
This page sits between policy intent and execution.
It decides whether a request may honestly enter the queue as:

- `admitted-best-effort`
- `admitted-guaranteed`
- `admitted-but-fragile`
- `blocked-no-source`
- `blocked-over-budget`
- `blocked-pending-reread`

## Fixed review order

1. **Admission verdict**
2. **Witness set**
3. **Route and freshness basis**
4. **Budget gate**
5. **Ghost-risk ladder**
6. **Next action**

### 1) Admission verdict

Show:

- verdict class
- current guarantee class requested
- whether the request is safe to expose as queue-visible
- strongest honest summary

### 2) Witness set

Show all known witness classes:

- full-copy witnesses online
- full-copy witnesses offline
- placeholder-only witnesses
- unknown / stale witnesses

Also show:

- quorum confidence
- sole-witness danger
- last witness-basis refresh

### 3) Route and freshness basis

Show:

- best current route class
- whether route is required only for eventual execution or also for proving promise honesty now
- freshness age of discovery / witness evidence
- whether reread is required before admission

### 4) Budget gate

Show:

- budget status (`fits`, `tight`, `over-budget`, `unknown`)
- whether admission is blocked by budget regardless of source health
- whether downgrade to best-effort would unblock admission

### 5) Ghost-risk ladder

Rank the reasons the request may collapse later:

- sole witness may disappear
- known witness already offline too long
- visible name may be placeholder-only everywhere
- stale witness map may be wrong
- queue delay may outlive witness freshness

This section must also show which repair or reread action would strengthen the verdict.

### 6) Next action

Offer only the strongest honest next actions:

- `Admit as guaranteed`
- `Admit as best-effort`
- `Reread witnesses before admitting`
- `Wait for another full-copy witness`
- `Reduce scope to fit budget`
- `Cancel request`

## Rules

### Rule 1 — visible names are not sufficient admission proof

The page may not admit a strong pending promise just because the namespace is visible.

### Rule 2 — sole-witness cases must sound fragile

A request backed by one full copy may still be admissible, but never with the same sentence as a healthy quorum.

### Rule 3 — no-source observations collapse the claim ceiling

If a ghost/no-source condition is observed, the page must stop sounding like a normal delay.

### Rule 4 — budget and source truth both matter

Healthy witnesses cannot rescue an over-budget guarantee, and spare budget cannot rescue a no-source request.

## Acceptance criteria

A later operator can:

- see why a request was admitted, weakened, or blocked
- tell whether witness strength or budget was the main limiter
- distinguish normal queue delay from ghost-risk collapse
- choose a repair or downgrade path without reopening several pages
