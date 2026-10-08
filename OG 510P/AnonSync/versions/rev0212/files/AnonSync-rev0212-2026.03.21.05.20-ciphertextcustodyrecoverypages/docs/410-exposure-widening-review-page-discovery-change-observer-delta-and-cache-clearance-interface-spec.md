# Exposure widening review page — discovery change, observer delta, and cache clearance interface spec

## Purpose

The archive already had route-exposure and discovery-publication specs.
What it still lacked was one ordinary review page for the action that operators actually take:

> if I enable tracker, relay, LAN discovery, known hosts, or broader directness here, who newly learns what, what route classes become eligible, and what residue survives if I later narrow it back?

Current official Resilio docs make this seam concrete.
They still say tracker learns share identity plus local/public endpoints, LAN discovery multicasts share identity and `IP:port`, predefined hosts receive share identity and peer IP when contacted, relay adds public infrastructure to transit but not plaintext storage, and `LAN only` tightening may still need cache-clearing plus restart because remembered public endpoints can survive.
That is useful truth.
It should not remain split between privacy prose, key flow, settings, and a special-case LAN-only article.

## Core decision

AnonSync must expose one first-class **Exposure widening review** page whenever an action would widen discovery, transit, or published endpoint visibility.

The page exists to answer five things in one place:

1. what exact change is being proposed
2. which new observers or audiences that change creates
3. what new facts those observers can learn
4. what route classes or repairs become newly eligible
5. what residue and rollback work remain even after later narrowing

## Fixed page order

1. **Requested widening**
2. **Observer and fact delta**
3. **Route-eligibility delta**
4. **Residue, rollback, and cache clearance**
5. **Decision verdict**

### 1) Requested widening

Show:

- `exposure_widening_review_id`
- subject / pair scope
- requested change set
- baseline posture
- strongest honest summary

The operator must be able to answer:

> what exactly am I widening?

### 2) Observer and fact delta

Show for each requested change:

- new observer class (`lan-neighbor`, `approved-public-infra`, `peer-pinned-target`, `none`)
- newly published facts (`share handle`, `local endpoint`, `public endpoint`, `relay eligibility`, `known-host target`, `none`)
- whether the observer learns discovery-only truth, transit truth, or both

This section should answer:

> who newly learns what if I accept this change?

### 3) Route-eligibility delta

Show:

- newly eligible route classes
- whether the change improves only discovery, only transit fallback, or both
- whether directness, relay fallback, or recovery speed improves
- whether a matching remote-side change is still required

### 4) Residue, rollback, and cache clearance

Show:

- whether remembered endpoints may survive later narrowing
- whether restart or explicit cache clearing is required for the narrower claim to become fully true
- whether existing sessions remain on the wider route until re-established
- what rollback receipt the product will keep

The page must make it ordinary to answer:

> if I undo this later, what wider residue might still remain for a while?

### 5) Decision verdict

Possible outcomes:

- `accept widening`
- `accept temporary widening`
- `defer and use narrower repair`
- `reject as disclosure-disproportionate`

Each verdict must name the recommended alternative if the change is not accepted.

## Public object

### Exposure widening review page

Fields:

- `exposure_widening_review_id`
- `subject_ref`
- `peer_pair_ref` nullable
- `requested_change_rows[]`
- `observer_delta_rows[]`
- `fact_delta_rows[]`
- `route_delta_rows[]`
- `residue_rows[]`
- `rollback_rows[]`
- `decision_verdict`
- `generated_at`

## Compact row contract

A compact row should preserve this order:

1. scope
2. requested widening
3. new observer class
4. strongest route gain
5. residue warning

Example:

```text
Media share     enable tracker     approved-public-infra     wan-direct discovery     clear cached public endpoints on later narrowing
```

## Non-goals

This page does **not** diagnose a current failure by itself and does not replace the pairwise route page.
It exists so disclosure-changing repairs and optimizations stop hiding inside innocent-looking toggles.

