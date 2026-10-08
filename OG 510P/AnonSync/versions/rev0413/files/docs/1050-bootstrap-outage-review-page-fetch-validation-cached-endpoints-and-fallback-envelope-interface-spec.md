# Bootstrap outage review page, fetch validation, cached endpoints, and fallback-envelope interface spec

## Purpose

The archive already had connectivity repair language, route basis, and some warning semantics.
What it still lacked was one explicit review page for the moment when bootstrap authority degrades:

> the source that normally defines discovery infrastructure is missing, stale, unreachable, or no longer trusted — what still works, what stopped being provable, and what should the operator do next?

Current official Resilio docs make that moment very real.
They still say peer connection may fail because the client cannot reach `config.resilio.com/sync.conf`; that tracker loss can be partially mitigated by predefined hosts; and that `No tracker connection` is not equal to total sync failure when relay, LAN discovery, or predefined hosts still remain.

That is not just an alert.
It is a reviewed fallback situation.

## Core decision

A degraded bootstrap source must always produce a **bootstrap outage review** before the product upgrades the situation into `broken`, `healthy enough`, or `safe to ignore`.
The review must separate:

- fetch failure
- validation failure
- stale but still trusted authority
- cached endpoint residue
- surviving manual or LAN discovery
- expected effect on existing peers versus new peers

## Fixed review order

Every bootstrap-outage review should render the same sections in the same order:

1. **Failure class**
2. **Residual authority and cache**
3. **Fallback envelope**
4. **Impact on existing peers and new joins**
5. **Recommended next move**

### 1) Failure class

This section should show:

- `transport-unreachable`
- `TLS-validation-failed`
- `signature-failed`
- `parse-failed`
- `stale-timeout`
- `authority-disabled-by-policy`

The operator must be able to answer: **what kind of outage is this?**

### 2) Residual authority and cache

This section should show:

- whether any last-known-good catalog remains
- whether cached endpoints are still considered usable
- age of cached material
- whether manual hosts or LAN discovery lie outside the failed authority

The operator must be able to answer: **what infrastructure knowledge survives the outage?**

### 3) Fallback envelope

This section should show one explicit envelope:

- `existing cached peers may still connect`
- `manual-host direct only`
- `LAN discovery only`
- `relay still available from cached endpoints`
- `new public discovery blocked`
- `no discovery fallback remains`

The operator must be able to answer: **what exactly still works right now?**

### 4) Impact on existing peers and new joins

This section should separately show:

- whether already known peers may still transfer
- whether newly added peers are likely to fail discovery
- whether pairwise route posture changed
- whether the seat is now effectively isolated unless manual/pinned paths are supplied

The operator must be able to answer: **who is affected first — current peers, future peers, or both?**

### 5) Recommended next move

The review must end with exactly one primary next action:

- `retry fetch`
- `pin private authority`
- `switch to manual-host fallback`
- `wait; cached continuity still acceptable`
- `treat as isolated until repaired`

## Public objects

### `bootstrap_outage_review`

Fields:

- `bootstrap_outage_review_id`
- `seat_ref`
- `authority_ref` nullable
- `failure_class`
- `cached_authority_findings[]`
- `fallback_envelope`
- `existing_peer_impact_summary`
- `new_join_impact_summary`
- `recommended_next_action`
- `generated_at`

## Main surface

A compact row should read like one of these:

- `bootstrap unreachable · cached endpoints still usable`
- `bootstrap validation failed · manual/LAN fallback only`
- `bootstrap stale · existing peers may continue, new public discovery blocked`
- `bootstrap absent · seat isolated except for manual pins`

## Event language

Use phrases such as:

- `bootstrap fetch failed; cached authority still within trust window`
- `bootstrap authority no longer trusted; route claims narrowed`
- `public discovery blocked; manual-host continuity remains`
- `new peer joins likely to fail until bootstrap is restored`

Avoid phrases such as:

- `tracker issue`
- `network error`
- `peer discovery unavailable`

Those lines are too vague to guide action.

## CLI shape

```text
anonsync discovery outage review --seat self
anonsync discovery outage explain --seat self
anonsync discovery authority retry --seat self
anonsync discovery authority pin --source manual-static
```

## Edge cases

### Existing peers still connect

That does not clear the outage.
The review must explicitly say that cached or manual knowledge preserved partial continuity while public bootstrap remains degraded.

### Tracker failed but relay or LAN still works

The review must keep lane truth separate instead of collapsing to one generic connectivity verdict.

### Authority disabled by policy

That is not an error.
It must still produce an outage-style review if an operator expected public discovery and now lacks it.

## Non-clone reason

Current official Resilio docs still leave the operator to infer fallback envelope from `Peers aren't connecting`, `Core warnings`, and architecture pages.
AnonSync should instead publish one ordinary outage review that owns failure class, residual cache, fallback envelope, and next action together.
