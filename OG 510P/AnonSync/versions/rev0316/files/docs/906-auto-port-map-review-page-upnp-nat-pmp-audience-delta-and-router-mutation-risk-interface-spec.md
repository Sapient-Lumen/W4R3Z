# Auto port-map review page: UPnP, NAT-PMP, audience delta, and router-mutation risk interface spec

## Purpose

Enabling or disabling automatic port mapping should never feel like a tiny tuning change.
This review exists to answer:

> if I apply this change, what network-edge mutation may occur, what inbound audience may widen or narrow, and what collateral router/device risks do I accept?

## Core decision

Every serious change to automatic port-mapping posture must compile into one first-class **Auto port-map review**.

The review owns:

- requested delta
- affected listening port
- audience delta
- helper / fallback consequences
- router-side-effect warning
- post-apply strongest safe sentence

## Fixed page order

1. requested delta
2. inbound audience delta
3. route consequence card
4. router-side-effect warning
5. decision rail

### 1) Requested delta

Show:

- current state
- requested state
- acting scope (`seat`, `runtime`, `config-owned seat`, `unsupported here`)
- whether the listening port is fixed, random, or changing simultaneously

### 2) Inbound audience delta

Render rows for at minimum:

- same-LAN peers
- known external peers
- broader internet-capable peers
- future peers that learn the address through discovery helpers

Each row shows:

- before
- after if apply succeeds
- confidence
- conditions still required

### 3) Route consequence card

Show whether enabling or disabling auto-mapping:

- increases chance of direct path
- decreases relay dependence
- leaves discovery helper dependence unchanged
- becomes meaningless because proxy or policy still blocks inbound directness
- requires external proof after apply

### 4) Router-side-effect warning

This card is mandatory whenever automatic mapping may be requested.
Show:

- that UPnP / NAT-PMP is a request to the network edge, not only a local preference
- whether current evidence about router compatibility is absent, known good, degraded, or previously problematic
- collateral-risk sentence for other network equipment or services
- least-strong alternative path (`manual forwarding`, `predefined hosts`, `stay relay-capable`, `cancel`)

### 5) Decision rail

Possible outcomes:

- `apply and issue ingress receipt`
- `apply, but require direct-proof test`
- `switch to manual-forwarding workflow`
- `keep relay/helper posture instead`
- `cancel; router-mutation risk not justified`

## Rules

### Rule 1 — auto-mapping changes publish audience delta

The product must not let automatic mapping masquerade as internal tuning.

### Rule 2 — random-port coupling is explicit

If the listening port is unstable or changing, the review must say that mapping continuity becomes less predictable.

### Rule 3 — router-side-effect warning stays adjacent to apply

The caution must not be buried in docs or tooltips away from the decision point.

## Acceptance criteria

A later operator can:

- tell what network-edge mutation was requested
- tell which inbound audience could widen or narrow
- tell whether relay / helper dependence changes or stays
- tell what router-side-effect risk was accepted
- tell what receipt family proves the result afterward
