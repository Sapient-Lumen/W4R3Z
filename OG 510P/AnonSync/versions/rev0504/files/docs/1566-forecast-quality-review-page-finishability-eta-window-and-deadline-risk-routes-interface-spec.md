# Forecast quality review page: finishability, ETA window, and deadline-risk routes interface spec

## Purpose

The contract sheet defines what remains and what would count as an honest forecast.
The review page must decide:

> based on current evidence, can this work be finished under the current route, what ETA window is still justified, and is the operator dealing with healthy uncertainty, fragile forecasting, or no honest forecast at all?

## Core review rule

AnonSync must separate **remaining-work evidence**, **finishability evidence**, **ETA evidence**, **deadline evidence**, and **forecast fragility**.
No review may collapse those into one optimistic progress label.

## Fixed page order

1. **Review banner**
2. **Remaining-work review**
3. **Finishability review**
4. **ETA-window review**
5. **Deadline and slip review**
6. **Blocked stronger sentence**

### 1) Review banner

Show:

- current review verdict
- current finishability grade
- ETA claim class
- confidence grade
- active deadline posture if any
- current forecast owner

Supported `review_verdict` values:

- `forecast-supported`
- `wide-forecast-only`
- `checkpoint-forecast-only`
- `finishable-no-eta`
- `deadline-risk-rising`
- `forecast-broken-reroute-needed`
- `no-honest-forecast`

Hard rule:

`forecast-supported` is disallowed unless both remaining-work basis and finishability basis are fresh enough for the requested decision horizon.

### 2) Remaining-work review

Required rows:

- strongest current basis for what remains
- whether remaining work is directly observed or inferred
- whether hidden preparation is already included
- whether remaining work is shrinking monotonically
- whether new debt is still appearing
- reviewer who accepted the remaining-work basis

Route rules:

- If remaining-work basis is stale or scope-mismatched, route to `no-honest-forecast`.
- If remaining work depends on a known checkpoint not yet cleared, route to `checkpoint-forecast-only`.

### 3) Finishability review

Required rows:

- strongest basis that finishing is possible
- strongest basis that finishing is blocked
- whether current route can complete without mutation
- whether source, lock, approval, or wake dependency is unresolved
- whether reroute would change forecast materially

Route rules:

- `finishable-no-eta` is valid when the route still looks viable but elapsed-time forecasting is too fragile.
- `forecast-broken-reroute-needed` is required when current route no longer honestly supports finishing.

### 4) ETA-window review

Required rows:

- strongest current ETA basis
- whether the basis is throughput, checkpoint, or policy-window driven
- whether recent net progress is representative or merely bursty
- whether scheduled pauses or rescan windows widen the estimate
- whether recent interruption risk is live

Route rules:

- Throughput-only ETA may not stand if hidden work or schedule gates dominate.
- `wide-forecast-only` is required if only a broad window survives honest review.
- `no-honest-forecast` is required when lower/upper bounds would be theatrical rather than evidenced.

### 5) Deadline and slip review

Required rows:

- named deadline if any
- current deadline posture
- strongest basis for on-time or late risk
- first reason the estimate could slip
- next condition that would restore confidence most

Supported `deadline_posture` values:

- `no-deadline-bound`
- `comfortably-inside-window`
- `inside-but-fragile`
- `checkpoint-critical`
- `likely-slip`
- `deadline-miss-probable`
- `deadline-claim-blocked`

Hard rule:

Deadline posture may not exceed the strength of the ETA claim class.
A weak ETA cannot support a strong on-time claim.

### 6) Blocked stronger sentence

Render:

- strongest allowed forecast sentence
- strongest blocked stronger forecast sentence
- missing fact or event that would unlock the stronger sentence

Examples:

- `Work is finishable with known delays, but a bounded ETA is blocked by the next rescan and lock recheck windows.`
- `A broad completion window is honest, but an on-time deadline claim is blocked by schedule pauses and source-availability fragility.`
- `Net progress is real, yet no honest ETA survives because remaining work is still changing as conflict debt appears.`
