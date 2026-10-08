# Control rehearsal proof page: drill scope, observed barrier, and stale trust withdrawal interface spec

## Purpose

Some controls cannot be trusted by passive silence alone.
The archive therefore needs one explicit page for the next question:

> when a control needs a drill or synthetic witness, what exactly did we test, what barrier did we observe, and what claim is still blocked afterward?

## Core decision

AnonSync must expose one first-class **Control rehearsal proof** whenever a control requires a synthetic drill, controlled test, or safe barrier observation to remain trusted.

## Fixed page order

1. **Rehearsal header**
2. **Drill design card**
3. **Observed barrier card**
4. **Claim-safety card**
5. **Stale-trust withdrawal card**
6. **Proof sentence**

### 1) Rehearsal header

Show:

- control id
- rehearsal id
- drill time
- drill owner
- drill scope
- risk class
- pass / fail / inconclusive status
- resulting trust state

Supported `risk_class` values:

- `read-only-safe-check`
- `low-impact-synthetic`
- `contained-write-test`
- `world-isolated-drill`
- `too-risky-for-routine-use`

### 2) Drill design card

Required rows:

- hazard being simulated or approximated
- exact test subjects
- required prerequisites
- expected control reaction
- observers and signal sources
- stop / abort condition
- cleanup and rollback plan

Hard rule:

A rehearsal may not be approved unless the expected control reaction is observable and the abort path is explicit.

### 3) Observed barrier card

This card records the actual proof, not the intent.
Required rows:

- whether the control fired
- where it fired
- what signal proved it fired
- what remained ambiguous
- whether any bypass path appeared
- whether the observed barrier matched the intended mechanism

Supported `observed_barrier_verdict` values:

- `barrier-observed-as-designed`
- `barrier-observed-weaker-than-designed`
- `detective-signal-only`
- `mechanism-uncertain`
- `bypass-observed`
- `drill-failed`

### 4) Claim-safety card

Required rows:

- strongest sentence newly safe after this rehearsal
- stronger sentence still blocked
- worlds excluded from the proof
- whether real-repeat evidence is still required
- next rereview due date

Hard rule:

A rehearsal can upgrade trust, but it may not erase a previously recorded same-cause escape.

### 5) Stale-trust withdrawal card

This section defines what happens when rehearsal duty is missed or invalidated.
Required rows:

- stale deadline
- withdrawal trigger
- automatic downgrade target
- who is notified
- what actions become blocked until new proof exists

Supported `automatic_downgrade_target` values:

- `stale-needs-rereview`
- `trust-withdrawn`
- `configured-only`
- `watch-only`

### 6) Proof sentence

The page must end with one sentence in this shape:

> `Rehearsal <id> observed <barrier verdict> for control <id> across <scope>, which supports <strongest safe sentence> but still blocks <stronger sentence>.`
