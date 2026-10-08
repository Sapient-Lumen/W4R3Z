# Remedy-hardening-attestation policy-conformance contract sheet page — live conformance, drift budget, and recertification clock

## Purpose

This page is the compact contract for deciding whether a policy that was already rolled out for a named estate slice is still honestly governing that slice right now.
It exists so the product can distinguish `deployed once`, `currently conforming with fresh witness`, `recertification overdue`, `suspected drift`, `confirmed breach`, `repair in progress`, `restored after recertification`, and `broader still-governing sentence blocked`.

## Core fields

- policy conformance identifier
- source policy-rollout receipt identifier
- current governing receipt identifier
- current policy-conformance class
- named estate slice under present review
- estate slices explicitly not covered by this conformance claim
- last trusted rollout-verdict class
- current witness freshness class
- latest conformance witness set
- next required recertification time
- inherited-coverage status for newly arrived objects or members
- pre-existing object reconciliation status
- service-world or principal-world continuity status
- reconnect or path-split exposure status
- suspected drift count
- confirmed breach count
- containment status
- repair owner
- repair due time
- highest currently safe conformance sentence
- strongest blocked still-governing sentence
- next evidence that upgrades confidence now
- next evidence that forces downgrade or breach declaration now

## Policy-conformance classes

The page must model at least these distinct classes:

- deployed policy, current conformance unverified
- current conformance evidenced for named slice only
- current conformance evidenced but inherited coverage incomplete
- recertification overdue, stronger sentence blocked
- suspected drift under investigation
- confirmed breach with containment active
- confirmed breach without adequate containment
- repair applied, recertification pending
- conformance restored after fresh recertification
- conformance narrowed, paused, or retired
- broader still-governing sentence blocked

## Drift axes

The page must support at least these drift axes:

- manual override emergence
- new-object inheritance failure
- pre-existing object residual variance
- service-world or principal-world split
- reconnect or path fork
- platform or surface control gap
- rescan or reread delay
- stale witness horizon
- containment adequacy
- repair verification gap

## Fixed rendering order

Every policy-conformance contract sheet must render the same sections in the same order:

1. **Highest currently conformance-safe sentence**
2. **Named estate slice, current conformance class, and witness freshness**
3. **Fresh drift and breach ledger**
4. **Containment, repair owner, and recertification clock**
5. **Next evidence that upgrades or collapses the still-governing claim**

## Hard rules

The contract sheet must never let an operator hide:

- an old rollout receipt behind a `still governing now` sentence
- stale witness behind a `current conformance proved` sentence
- a new-arrival inheritance gap behind `policy covers the slice`
- a service or principal world split behind `same deployment still applies`
- suspected or confirmed drift behind `no known issue` wording
