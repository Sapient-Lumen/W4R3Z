# Evidence synthesis timeline page: arrival, supersession, corroboration, conflict, and claim-shift events interface spec

## Purpose

The operator needs one timeline that answers:

> how did the merged claim change as packets arrived, were superseded, corroborated each other, or opened new contradictions?

## Core decision

AnonSync must expose one first-class **Evidence synthesis timeline** for every synthesis object that survives beyond one reading session.

## Fixed page order

1. **Timeline header**
2. **Packet-arrival lane**
3. **Relation-change lane**
4. **Claim-shift lane**
5. **Conflict lane**
6. **Supersession-and-expiry lane**
7. **Timeline sentence**

### 1) Timeline header

Show:

- synthesis id
- first packet arrival time
- latest packet or witness arrival time
- latest integrated claim time
- current synthesis posture
- current strongest safe integrated sentence

### 2) Packet-arrival lane

Supported `arrival_event` values:

- `packet-arrived`
- `packet-opened`
- `packet-validated`
- `packet-added-to-active-basis`
- `packet-held-out`
- `packet-rejected`

### 3) Relation-change lane

Supported `relation_change_event` values:

- `duplicate-marked`
- `independent-corroboration-established`
- `soft-conflict-opened`
- `hard-conflict-opened`
- `unknown-relation-cleared`
- `relation-reweighted`

### 4) Claim-shift lane

Supported `claim_shift_event` values:

- `sentence-strengthened`
- `sentence-weakened`
- `sentence-narrowed`
- `sentence-broadened-with-proof`
- `fallback-claim-only`
- `integrated-claim-issued`

Hard rule:

A sentence may not be marked `strengthened` unless the timeline records whether the change came from new independence, resolved conflict, improved freshness, or scope narrowing.

### 5) Conflict lane

Supported `conflict_event` values:

- `conflict-opened`
- `conflict-reclassified`
- `conflict-capped-claim`
- `conflict-resolved`
- `conflict-reopened`
- `alternative-interpretation-killed`

### 6) Supersession-and-expiry lane

Supported `supersession_event` values:

- `packet-superseded`
- `packet-expired`
- `proof-recalled`
- `proof-reissued`
- `basis-shifted`

Hard rule:

When a source expires or is superseded, the timeline must show whether the merged sentence stayed the same, shrank, or required reissue.

### 7) Timeline sentence

Render exactly two lines:

- **How the integrated claim reached its current ceiling**
- **What event would most likely change that ceiling next**
