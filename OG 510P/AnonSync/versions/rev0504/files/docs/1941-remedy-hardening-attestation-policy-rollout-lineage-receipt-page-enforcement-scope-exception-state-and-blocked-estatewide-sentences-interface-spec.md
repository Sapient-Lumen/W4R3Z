
# Remedy-hardening-attestation policy-rollout lineage receipt page — enforcement scope, exception state, and blocked estate-wide sentences

## Purpose

This page is the durable one-receipt summary for rollout claims after precedent portability.
It lets a later operator read one artifact and know exactly whether the portable rule stayed undeployed, became active for a named estate slice, or became enforced with bounded exceptions only.

## Receipt fields

- receipt identifier
- policy rollout identifier
- source precedent receipt identifier
- current policy-rollout class
- named estate slices currently in scope
- estate slices explicitly out of scope
- deployment mechanism summary
- verification coverage summary
- manual override summary
- waiver and grandfather summary
- exception debt summary
- review or expiry summary
- highest honest rollout sentence
- blocked stronger estate-wide sentence
- evidence bundle references
- issued-at timestamp

## Primary sentence block

The receipt must begin with exactly two lines:

- **Highest honest rollout sentence**
- **Blocked stronger estate-wide sentence**

## Required sections

1. **Why the source precedent was or was not rollout-eligible**
2. **Which estate slices are actually covered now**
3. **Which deployment lanes, overrides, and drifts still matter**
4. **What waivers, grandfathered populations, and expiry debt remain**
5. **Why the next stronger estate-wide sentence is still blocked**

## Hard rules

The receipt must never let:

- `portable rule` impersonate `deployed policy`
- `deployed default` impersonate `effective enforcement`
- `named slice covered` impersonate `whole estate covered`
- `temporary waiver` impersonate `silent compliance`
- `policy once enforced` impersonate `immune to drift, expiry, narrowing, or retirement`
