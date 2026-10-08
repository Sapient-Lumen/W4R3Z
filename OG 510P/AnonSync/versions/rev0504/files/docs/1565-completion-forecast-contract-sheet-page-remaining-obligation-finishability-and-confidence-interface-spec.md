# Completion forecast contract sheet page: remaining obligation, finishability, and confidence interface spec

## Purpose

Once net progress exists, the operator still needs one page that answers:

> what exactly remains, is the work finishable under current conditions, what ETA window is currently honest, and what conditions make the estimate stronger or weaker?

## Core decision

AnonSync must expose one first-class **Completion forecast contract sheet** whenever a work item has proved net progress, partial net progress, churn-dominant progress with some remaining path, reroute after no-net-gain, or any live request for time-to-finish, deadline posture, or finishability.

## Fixed page order

1. **Forecast header**
2. **Remaining-obligation card**
3. **Finishability card**
4. **ETA-window card**
5. **Confidence-and-risk card**
6. **Forecast sentence**

### 1) Forecast header

Show:

- forecast id
- linked progress id
- linked heartbeat id
- linked claim id
- current forecast posture
- current custodian
- remaining-obligation unit
- current finishability grade
- current ETA-window status
- current deadline posture if any
- forecast owner

Supported `forecast_posture` values:

- `drafted-from-progress`
- `remaining-work-shaped`
- `finishability-provisional`
- `eta-window-published`
- `deadline-risk-open`
- `forecast-held-wide`
- `no-honest-forecast`
- `reroute-before-forecast`
- `requalified-after-shift`
- `closed`

Hard rule:

The header may not imply a trustworthy ETA merely because net progress exists.
Net progress is still weaker than a finish forecast.

### 2) Remaining-obligation card

Required rows:

- named obligation still open
- current remaining-work basis
- unit of remaining work
- whether the remaining basis is direct or inferred
- known completed fraction if publishable
- hidden preparation still outstanding
- known external wait still outstanding
- current smallest finishable subgoal

Hard rules:

- `remaining work` must not silently equal `bytes left` unless the contract says bytes are the real obligation unit.
- Hidden preparation such as rescan, hash, merge, approval, wake, or lock release must remain visible when it affects completion.

### 3) Finishability card

Required rows:

- current finishability grade
- strongest basis for that grade
- hardest blocker to finishing
- whether finish is possible under current route
- whether finish needs new evidence or only elapsed work
- whether the route is deadline-compatible

Supported `finishability_grade` values:

- `finishable-now-if-motion-holds`
- `finishable-with-known-delays`
- `finishable-after-prerequisite`
- `finishable-only-after-reroute`
- `finishability-uncertain`
- `not-honestly-finishable-under-current-route`

Hard rule:

`finishable-now-if-motion-holds` requires both a remaining-work basis and no known blocking prerequisite stronger than elapsed time.

### 4) ETA-window card

Required rows:

- current ETA claim class
- earliest honest finish time
- latest honest finish time
- whether the window is local-time or relative-duration based
- main factors widening the window
- next condition that would narrow the window most

Supported `eta_claim_class` values:

- `no-eta-claimed`
- `wide-window-only`
- `bounded-window`
- `checkpoint-based-window`
- `deadline-miss-risk-window`
- `narrow-window-blocked`

Hard rules:

- A single point ETA is disallowed.
- `bounded-window` requires an explicit lower and upper bound.
- `checkpoint-based-window` must name the checkpoint that divides the estimate.

### 5) Confidence-and-risk card

Required rows:

- current confidence grade
- strongest support for confidence
- strongest reason confidence is capped
- whether the estimate depends on hidden work
- whether schedule gates or pause windows apply
- whether source availability risk is live
- whether restart-from-start or whole-file-rework risk is live
- whether locked-resource risk is live

Supported `forecast_confidence_grade` values:

- `high-for-current-window`
- `moderate`
- `fragile`
- `too-fragile-for-eta`

Hard rule:

If any live risk can invalidate the current window without a new external event being noticed quickly, confidence may not exceed `moderate`.

### 6) Forecast sentence

Render:

- strongest allowed finishability sentence
- strongest allowed ETA sentence
- strongest blocked stronger sentence

Examples:

- `Net progress is real, but only a wide finish window is honest because scheduled pauses and hidden merge work still dominate the remaining path.`
- `Current route is finishable after lock release; no honest ETA exists until access to the blocked files returns.`
- `Work appears likely to finish within the current window if source availability and rescan posture do not change, but a tighter claim is blocked.`
