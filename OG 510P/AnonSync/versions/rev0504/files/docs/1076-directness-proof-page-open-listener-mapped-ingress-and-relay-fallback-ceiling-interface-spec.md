# Directness proof page, open listener, mapped ingress, and relay-fallback ceiling interface spec

## Purpose

The product needs one stable place to answer a deceptively simple question:

> what is the strongest honest connectivity sentence right now?

Current official Resilio docs still preserve the relevant ladder:

- a listener can exist locally
- a router mapping can be attempted
- a relay can still be used if direct connection is not possible
- direct connection may still fail because ports, firewalls, routes, or remote posture do not line up

AnonSync should therefore publish directness as a proof ladder rather than a binary success icon.

## Proof ladder

The page should order evidence from weakest to strongest:

1. **local listener only**
2. **router-mapping attempted**
3. **lease or forwarding visible**
4. **outside reachability plausible**
5. **direct peer session demonstrated**
6. **directness continuity stable over time**

The product must never skip upward without evidence.

## Evidence sections

### 1) Listener evidence

Show:

- actual local listener state
- port value
- bind result and timestamp
- whether listener continuity is fixed or random

### 2) Ingress evidence

Show:

- mapping or forwarding evidence class
- whether evidence is host-observed, router-reported, operator-declared, or absent
- expiry or invalidation conditions

### 3) Remote-pair evidence

Show:

- which peer pair or cohort the proof applies to
- whether the current path was direct or relayed
- whether the proof generalizes to all peers or only one reviewed pair

### 4) Relay ceiling

Show:

- whether relay remains enabled
- whether current success still depends on relay
- whether the stronger sentence `direct route earned` is blocked

### 5) Strongest safe sentence

Examples:

- `listener exists locally; outside reachability not yet shown`
- `mapping attempt recorded; direct route still unproven`
- `lease visible; peer-pair directness still absent`
- `direct connection demonstrated for peer pair A↔B`
- `directness was demonstrated once, but continuity over time remains unproven`

## Public object

### `directness_proof`

Fields:

- `directness_proof_id`
- `runtime_namespace_ref`
- `listener_evidence_class`
- `ingress_evidence_class`
- `pair_scope`
- `current_route_class`
- `relay_enabled`
- `proof_ceiling`
- `blocked_stronger_sentence`
- `observed_at`

## Main surface

A compact row should read like one of these:

- `listener up · mapping attempted · relay fallback still part of envelope`
- `lease visible · no direct peer proof yet`
- `direct pairwise route proven · not yet generalized to all peers`
- `relay currently carrying traffic; outside reachability claim withheld`

## Event language

Use phrases such as:

- `directness proof updated`
- `pairwise direct route observed`
- `relay ceiling still active`
- `outside reachability still below proof threshold`

Avoid phrases such as:

- `open port confirmed`
- `internet access works`
- `fast path established`

Those are too broad unless separately proven.

## Design tests

The page fails if any of these remain true:

- a mapping attempt can still upgrade the UI straight to `direct`
- pairwise evidence still looks like cohort-wide truth
- relay dependence can remain hidden under a general success badge
