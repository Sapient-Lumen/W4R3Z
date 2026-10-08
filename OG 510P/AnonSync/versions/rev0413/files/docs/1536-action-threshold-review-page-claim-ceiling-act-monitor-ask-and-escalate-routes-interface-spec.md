# Action-threshold review page: claim ceiling, act, monitor, ask, and escalate routes interface spec

## Purpose

The contract sheet defines the target decision.
The operator still needs one review page that compares live routes side by side and answers:

> is the right next move to act, monitor, ask, defer, or escalate, and what exact evidence difference makes that route stronger than the others right now?

## Review layout

1. **Route-comparison strip**
2. **Claim-ceiling panel**
3. **Threshold-crossing panel**
4. **Uncertainty-spend panel**
5. **Cheapest-upgrade panel**
6. **Decision pressure panel**
7. **Review verdict**

### 1) Route-comparison strip

Show one card for each route:

- `wait`
- `monitor`
- `ask`
- `bounded-action`
- `heavy-escalation`
- `publish`
- `halt`

Each card must show:

- current eligibility
- key supporting basis
- key blocker
- reversibility
- risk of acting too early
- risk of waiting too long

Hard rule:

The interface may not hide non-selected routes entirely.
It must show why they lost.

### 2) Claim-ceiling panel

Required rows:

- strongest safe sentence
- strongest sentence needed for each route
- routes supported only by weaker sentences
- routes blocked by unresolved contradiction

Hard rule:

A route cannot be marked `eligible` if its required sentence is above the current claim ceiling.

### 3) Threshold-crossing panel

For each route, show:

- threshold status
- what evidence cleared it
- what evidence failed it
- whether failure is reversible or structural

Supported `threshold_failure_class` values:

- `missing-fact`
- `stale-basis`
- `world-mismatch`
- `conflict-unresolved`
- `cost-disproportionate`
- `scope-too-wide`

### 4) Uncertainty-spend panel

Required rows:

- uncertainty still open
- whether this route tolerates that uncertainty
- what harm follows if uncertainty is wrong
- whether the route increases or decreases future certainty

Hard rule:

The review must publish when a route is chosen *despite* open uncertainty, not just when the route waits for certainty.

### 5) Cheapest-upgrade panel

Required rows:

- next cheapest fact that would upgrade the current route
- next cheapest fact that would downgrade the current route
- next cheapest artifact or observation that would unlock the blocked stronger route

Hard rule:

`collect more logs` is invalid unless named as the cheapest upgrade relative to all other currently available asks.

### 6) Decision pressure panel

Required rows:

- time pressure
- safety pressure
- operational pressure
- evidence decay pressure
- cost of continued indecision

Supported `decision_pressure_posture` values:

- `low-and-patient`
- `watch-closely`
- `time-sensitive`
- `harm-rising`
- `freeze-first`

Hard rule:

High pressure may justify a lower-certainty route, but the review must publish that trade explicitly.

### 7) Review verdict

Render:

- selected route
- why it beats the nearest alternative
- what stronger route stays blocked
- what event reopens route comparison
