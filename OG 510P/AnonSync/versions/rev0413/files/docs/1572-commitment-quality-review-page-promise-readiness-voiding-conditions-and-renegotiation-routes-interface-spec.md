# Commitment quality review page: promise readiness, voiding conditions, and renegotiation routes interface spec

## Purpose

This page decides whether a current forecast is strong enough to publish as aspiration, target, conditional commitment, hard commitment, or not honestly promiseable yet.

## Review questions

The page must answer, in order:

1. Is there a credible forecast basis at all?
2. Are the invalidators named and small enough to tolerate?
3. Does the audience need a promise or only a forecast?
4. What is the cheapest truthful promise class?
5. What exact event would force renegotiation first?

## Fixed page order

1. **Review header**
2. **Forecast sufficiency panel**
3. **Promise-readiness ladder**
4. **Invalidator pressure panel**
5. **Renegotiation route panel**
6. **Outcome panel**

### 1) Review header

Show:

- review id
- linked commitment id
- linked forecast id
- current review posture
- current candidate promise class
- strongest blocked stronger promise
- current reviewer
- audience at risk

Supported `review_posture` values:

- `forecast-only-review`
- `promise-readiness-open`
- `conditionality-pressure-open`
- `renegotiation-route-open`
- `ready-to-publish`
- `not-ready-to-publish`
- `breach-boundary-open`
- `closed`

### 2) Forecast sufficiency panel

Required rows:

- remaining-work basis quality
- finishability grade quality
- ETA-window quality
- confidence fragility
- freshness of inputs
- whether the forecast is already stale for the intended audience

Hard rule:

A forecast that is already stale for the audience may not be upgraded into a stronger promise class.

### 3) Promise-readiness ladder

The page must show one rung per class:

- `aspiration`
- `target`
- `conditional-commitment`
- `hard-commitment`

Each rung must state:

- minimum evidence required
- named invalidators tolerated at that rung
- surviving sentence if that rung fails
- exact reason the next stronger rung is blocked

Hard rules:

- The ladder must default to the weakest truthful rung.
- Skipping straight from weak forecast to hard commitment is disallowed unless lower rungs are explicitly satisfied and preserved in lineage.

### 4) Invalidator pressure panel

Required rows:

- current top invalidator
- invalidator class
- estimated pressure on the promise
- whether it is within tolerance
- whether it is already active
- whether it should force immediate downgrade

Supported `invalidator_class` values:

- `throughput-collapse`
- `discovery-delay`
- `pause-window`
- `hidden-preprocessing`
- `restart-risk`
- `lock-risk`
- `source-risk`
- `operator-dependency`
- `external-dependency`
- `unknown-fragility`

Hard rule:

Active invalidators must never stay hidden behind the original promised window.

### 5) Renegotiation route panel

Required rows:

- earliest required renegotiation trigger
- who must be notified
- best downgraded sentence if triggered
- whether the route allows widening without calling it a miss
- whether the audience must re-accept the new commitment
- whether a failure to renegotiate in time escalates to breach automatically

Supported `renegotiation_route` values:

- `no-renegotiation-needed`
- `widen-window-and-republish`
- `downgrade-to-target`
- `withdraw-to-forecast-only`
- `breach-with-recovery-plan`
- `replace-with-new-commitment-id`

### 6) Outcome panel

Supported `review_outcome` values:

- `publish-aspiration`
- `publish-target`
- `publish-conditional-commitment`
- `publish-hard-commitment`
- `keep-forecast-only`
- `publish-with-renegotiation-watch`
- `downgrade-existing-commitment`
- `declare-breach-open`

Hard rule:

The page must state both the chosen promise class and the next stronger class that remains blocked.
