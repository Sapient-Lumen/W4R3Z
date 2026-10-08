# Remedy-hardening-attestation policy-conformance lineage receipt page — current conformance, drift state, and blocked still-governing sentences

## Purpose

This page is the durable one-receipt summary for current conformance claims after rollout.
It lets a later operator read one artifact and know exactly whether the deployed policy is still governing the named slice now, merely believed to be, or blocked by stale proof, suspected drift, or confirmed breach.

## Receipt fields

- receipt identifier
- policy conformance identifier
- source policy-rollout receipt identifier
- current policy-conformance class
- named estate slices currently covered by fresh proof
- estate slices explicitly uncovered or stale
- witness freshness summary
- inherited-coverage summary
- drift and breach summary
- containment and repair summary
- recertification summary
- highest honest current conformance sentence
- blocked stronger still-governing sentence
- evidence bundle references
- issued-at timestamp

## Primary sentence block

The receipt must begin with exactly two lines:

- **Highest honest current conformance sentence**
- **Blocked stronger still-governing sentence**

## Required sections

1. **Why the rollout basis did or did not survive into present-time conformance**
2. **Which populations are freshly covered now and which are not**
3. **Which drift, world splits, or inheritance gaps still matter**
4. **What containment, repair, and recertification state remains**
5. **Why the next stronger `still governing` sentence is blocked**

## Hard rules

The receipt must never let:

- `policy was deployed` impersonate `policy still governs now`
- `fresh witness exists somewhere` impersonate `whole slice freshly proved`
- `new arrivals inherit` impersonate `older populations were reconciled`
- `repair applied` impersonate `recertified conformance`
- `no new alarm surfaced` impersonate `no drift or breach exists`
