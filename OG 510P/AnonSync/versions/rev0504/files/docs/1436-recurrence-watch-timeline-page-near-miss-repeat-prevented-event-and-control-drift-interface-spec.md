# Recurrence watch timeline page: near miss, repeat, prevented event, and control drift interface spec

## Purpose

Once a control activates, the product still needs one durable page for the evidence that follows:

> did the hazard recur, did the control actually stop it, did it only detect it earlier, or did the control silently drift out of truth?

## Core decision

AnonSync must expose one first-class **Recurrence watch timeline** for every promoted control during its watch window and for every later escape or near miss.

## Fixed page order

1. **Timeline header**
2. **Expected repeat window card**
3. **Observed events stream**
4. **Effectiveness verdict ladder**
5. **Control-drift card**
6. **Reopen hooks**

### 1) Timeline header

Show:

- control id
- linked source case ids
- watch start
- watch end or ongoing flag
- current effectiveness verdict
- latest confidence grade

Supported `current_effectiveness_verdict` values:

- `no-relevant-events-yet`
- `quiet-window-only`
- `near-miss-detected`
- `repeat-detected-earlier`
- `repeat-contained`
- `repeat-prevented-with-strong-basis`
- `repeat-escaped`
- `control-drifted`
- `superseded`

### 2) Expected repeat window card

Required rows:

- why a repeat is expected or feared
- normal recurrence horizon
- seasonal / workload / topology triggers
- signal freshness requirement
- what counts as silence
- what counts as meaningful absence of evidence

Hard rule:

`quiet-window-only` must stay visibly weaker than `repeat-prevented-with-strong-basis`.

### 3) Observed events stream

Each timeline row must include:

- event time
- event class
- linked subjects
- signal source
- hazard match strength
- control response
- operator interpretation
- whether confidence rose or fell

Supported `event_class` values:

- `no-event-window-closed`
- `near-miss`
- `same-symptom-repeat`
- `same-cause-repeat`
- `control-fired`
- `control-bypassed`
- `control-disabled`
- `version-drift`
- `world-fork`
- `manual-override`

### 4) Effectiveness verdict ladder

The page must preserve the following non-collapsible ladder:

1. `quiet-window-only`
2. `near-miss-detected`
3. `repeat-detected-earlier`
4. `repeat-contained`
5. `repeat-prevented-with-strong-basis`

Hard rule:

A higher rung may not be claimed unless the lower-rung evidence is preserved and visible.

### 5) Control-drift card

Required rows:

- drift class
- drift source
- first drift signal
- subjects affected
- whether the drift invalidates prior prevention claims
- whether rereview or reopen is automatic

Supported `drift_class` values:

- `version-behavior-change`
- `world-scope-change`
- `setting-precondition-lost`
- `service-or-config-fork`
- `ownership-gap`
- `signal-source-stale`

### 6) Reopen hooks

Each hook row must show:

- trigger description
- linked case or control to reopen
- automatic vs manual reopen
- next required review page
- strongest sentence that becomes unsafe again

Hard rule:

A same-cause escape must automatically reopen the source case family and downgrade the control's strongest safe sentence.
