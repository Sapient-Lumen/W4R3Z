# Network policy delta page — seat-wide vs share-wide widening and observer-delta interface spec

## Purpose

The archive already has helper-policy, route, exposure, and transfer-budget language.
What it still lacked was one exact page for the operator question:

> if I widen or narrow network eligibility here, am I changing only this share, the whole seat, or both, and what future detection / transfer / exposure delta follows?

## Core decision

Any non-trivial network-policy mutation must render one first-class **Network policy delta** page.
That page is the semantic home of:

- current seat-wide network rule
- current share-wide network rule
- requested delta and scope
- resulting eligibility on common network classes
- exposure / cost / freshness consequences
- safer narrower alternative if the operator declines the broader scope

## Primary page layout

The page always renders the same top-level regions in the same order:

1. delta verdict strip
2. scope card
3. common-network-class comparison card
4. exposure / cost delta card
5. fallback / receipt card

### 1) Delta verdict strip

Show:

- current rule(s)
- requested mutation
- scope (`seat-wide`, `share-only`, `both`, `unknown`)
- strongest honest one-line summary

Allowed summaries:

- `Widen only this share from Wi‑Fi only to any allowed network; seat-wide cellular policy unchanged`
- `Enable mobile data seat-wide; all inheriting shares may now participate on cellular`
- `Pin this share to the current Wi‑Fi; future cellular and other Wi‑Fi participation will stop`
- `No policy widening; waiting for approved network remains the narrowest path`

### 2) Scope card

Show:

- exact object being changed
- who inherits the change
- what objects remain unchanged
- whether the requested edit narrows or widens observation / transfer eligibility

The operator must be able to answer:

> am I changing the whole seat or only this share?

### 3) Common-network-class comparison card

Show side by side for at least:

- current Wi‑Fi
- current cellular
- alternate Wi‑Fi / future network
- offline / sleeping state

For each class show:

- before eligibility
- after eligibility
- detection floor
- transfer floor

### 4) Exposure / cost delta card

Show:

- whether broader network classes may now carry traffic
- whether future observation freshness improves
- whether metered/cellular cost risk rises
- whether the share becomes more observable to peers or simply more reachable

This card exists to keep product honesty when a small-seeming toggle broadens participation significantly.

### 5) Fallback / receipt card

Show:

- nearest lower-power alternative
- capability lost by choosing it
- whether continuity is preserved
- whether another seat or current-network wait is safer
- resulting receipt class

## Behavior rules

- This page must appear when seat-wide and share-wide network rules do not mean the same thing.
- The product must not pretend `enable mobile data` and `widen this share` are equivalent.
- If a same-goal narrower path exists, it must be shown before the broader mutation is treated as routine.
- A network-policy mutation must preview both participation gain and claim-ceiling changes.

## Compact row contract

A compact row should preserve this order:

1. target scope
2. current rule
3. requested rule
4. strongest changed eligibility
5. safest alternative

Example:

```text
This share     Wi‑Fi only     Any allowed network     eligible on current cellular if seat allows it     Wait for Wi‑Fi
```

## Non-clone reason

Current official Resilio docs are candid about global `Use mobile data`, per-share `Allowed network`, and sleep policy, but they still do not give one stable page proving scope, consequence, and fallback together.
AnonSync should.
