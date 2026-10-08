# Delivery commitment contract sheet page: forecast basis, promise conditions, and breach boundary interface spec

## Purpose

Once a finish forecast exists, the operator still needs one page that answers:

> did anyone actually promise a finish, what class of promise is it, what conditions must hold for that promise to survive, and what exactly counts as slip, renegotiation, miss, or breach?

## Core decision

AnonSync must expose one first-class **Delivery commitment contract sheet** whenever a work item has any outward delivery target, any request for deadline language, any published ETA that might be treated as a promise, or any need to distinguish aspiration from commitment.

## Fixed page order

1. **Commitment header**
2. **Forecast-basis card**
3. **Commitment-class card**
4. **Invalidators-and-conditions card**
5. **Breach-boundary card**
6. **Commitment sentence**

### 1) Commitment header

Show:

- commitment id
- linked forecast id
- linked progress id
- named deliverable
- current commitment posture
- current commitment class
- promised window status
- current deadline posture
- current owner
- current audience
- latest surviving sentence

Supported `commitment_posture` values:

- `not-shaped`
- `aspirational-only`
- `target-proposed`
- `conditional-commitment-shaped`
- `hard-commitment-shaped`
- `renegotiation-open`
- `withdrawn-to-forecast-only`
- `missed-window-under-review`
- `breach-open`
- `closed`

Hard rule:

The header may not imply a commitment merely because a forecast exists.
A forecast is still weaker than a promise.

### 2) Forecast-basis card

Required rows:

- linked forecast posture
- remaining-work basis
- finishability grade
- current ETA window
- current confidence grade
- main fragility source
- strongest fact making the estimate believable
- strongest fact keeping the estimate conditional

Hard rules:

- A commitment may not hide its forecast basis.
- If forecast confidence is weak, the card must surface that weakness before any promise language.

### 3) Commitment-class card

Required rows:

- current commitment class
- named audience relying on it
- strongest allowed promise sentence
- whether the commitment is explicit or inferred-from-publication
- whether the operator accepts deadline custody
- whether the commitment can be delegated
- whether breach has an external consequence

Supported `commitment_class` values:

- `no-commitment`
- `aspiration`
- `target`
- `conditional-commitment`
- `hard-commitment`
- `withdrawn-commitment`
- `expired-commitment`

Hard rules:

- `target` is weaker than `conditional-commitment`.
- `conditional-commitment` requires named conditions.
- `hard-commitment` is disallowed if the page still needs unnamed operator optimism to survive.

### 4) Invalidators-and-conditions card

Required rows:

- named conditions required for the commitment to survive
- known invalidators
- known widening triggers
- required check-in cadence
- next event that would force renegotiation
- whether the commitment survives a route change
- whether interruption can restart work from the beginning

Supported `condition_type` values:

- `throughput-holds`
- `source-remains-available`
- `lock-clears`
- `schedule-window-opens`
- `rescan-discovers-change`
- `hidden-preprocessing-finishes`
- `no-restart-from-zero`
- `approval-arrives`
- `operator-action-required`
- `external-dependency-clears`

Hard rules:

- Every published commitment stronger than `aspiration` must name at least one invalidator or explicitly say none are known.
- A route with known restart-from-zero or whole-file-rework risk may not publish as `hard-commitment` unless that risk is already absorbed into the promised window.

### 5) Breach-boundary card

Required rows:

- promised earliest and latest finish bounds
- allowed slip without renegotiation
- when renegotiation becomes mandatory
- when target is officially missed
- when miss becomes breach
- who may declare breach closed
- weaker sentence that survives after breach

Supported `breach_boundary` values:

- `none-no-commitment`
- `soft-slip-only`
- `miss-with-renegotiation-required`
- `hard-breach-on-window-end`
- `hard-breach-on-condition-failure`
- `audience-specific-boundary`

Hard rules:

- `miss` and `breach` may not share one threshold unless the page says so explicitly.
- A breach boundary must be visible before the promise is published, not only after failure.

### 6) Commitment sentence

Format:

`Current commitment: [class] for [deliverable] to [audience], based on [forecast basis], surviving while [named conditions], with renegotiation no later than [boundary] and breach at [boundary if any].`

Examples:

- `Current commitment: target for initial mirror completion this week, based on finishable-with-known-delays forecast, surviving while source peers remain online and no whole-file restart occurs, with renegotiation if the next schedule window is missed.`
- `Current commitment: conditional commitment for staged restore by 18:00 local time, based on bounded-window forecast, surviving while hidden merge work completes as observed and no lock persists past its recheck boundary.`

Hard rule:

The sentence must never let a soft target masquerade as a hard commitment.
