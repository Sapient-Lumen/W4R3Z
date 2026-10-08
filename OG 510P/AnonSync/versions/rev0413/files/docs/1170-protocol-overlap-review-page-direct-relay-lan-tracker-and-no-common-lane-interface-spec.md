# Protocol overlap review page: direct, relay, LAN, tracker, and no-common-lane interface spec

## Purpose

This page answers one ordinary question:

> after these protocol and route constraints, what lanes can these peers still actually use to find and carry bytes?

The page exists because `allowed direct`, `relay fallback`, `LAN discovery`, `tracker reach`, and `no common lane` are not the same truth.

## Core decision

Every material transport narrowing or troubleshooting step must compile into one first-class **Protocol overlap review**.

The review owns:

- lane candidates
- lane prerequisites
- overlap verdict
- fallback order
- failure floor
- apply verdict

## Fixed page order

1. requested lane change
2. lane candidate matrix
3. overlap verdict card
4. fallback order card
5. apply verdict

### 1) Requested lane change

Show:

- target pair or cohort
- requested lane posture (`direct-only`, `relay-allowed`, `LAN-only`, `tracker-disabled`, `protocol-subset`, `unknown`)
- strongest safe pre-apply sentence
- stronger rejected sentence

### 2) Lane candidate matrix

Minimum rows:

- tracker-mediated discovery
- LAN multicast discovery
- LAN broadcast discovery
- direct TCP tunnel
- direct UDP / uTP tunnel
- relay tunnel
- predefined-host dial path

Columns:

- configured locally
- configured remotely
- prerequisite present
- common overlap verdict (`yes`, `no`, `residue-only`, `unknown`)
- notes

### 3) Overlap verdict card

Possible honest outcomes:

- `direct-and-relay remain`
- `relay-only remains`
- `LAN-only remains`
- `discovery-only; no transfer lane proven`
- `no-common-lane`
- `ambiguous-overlap`

The operator must be able to answer:

> what actual transport classes survived this change?

### 4) Fallback order card

Show:

- expected lane order if the preferred class fails
- whether proxy posture suppresses incoming directness
- whether relay remains the last surviving lane
- whether tracker disable now requires LAN or predefined-host proof instead

### 5) Apply verdict

Possible outcomes:

- `apply narrowed protocol set`
- `apply with relay-only warning`
- `apply with LAN discovery proof requirement`
- `block; no common lane would remain`
- `cancel and reopen transport profile`

## Rules

### Rule 1 — discovery lane and transfer lane may not collapse

The page must keep `can find peer` separate from `can carry bytes`.

### Rule 2 — fallback order is first-class

An operator must not learn only after slowdown that the surviving lane is relay-only.

### Rule 3 — no-common-lane must be explicit

If peers share no common protocol or route lane, the page must say so plainly instead of surfacing only a generic connection failure.
