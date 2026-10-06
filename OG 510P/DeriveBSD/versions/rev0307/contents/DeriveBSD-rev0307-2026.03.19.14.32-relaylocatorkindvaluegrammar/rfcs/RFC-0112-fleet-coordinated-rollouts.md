# RFC-0112: Fleet-coordinated staged rollouts (optional lane)

Status: **draft**

## Problem

Atomic upgrades and rollbacks are necessary but not sufficient.
At fleet scale we need an *explainable* way to:
- roll out changes gradually
- pause on failures
- respect update windows and reboot coordination

Without a first-class model, rollout logic becomes ad-hoc and unreviewable.

## Goals

- Represent rollout intent as **signed, content-addressed data**.
- Allow both:
  - decentralized “graph-based offer” rollouts
  - centralized “explicit assignment receipts” rollouts
- Integrate with health-gated updates and rollback indices.

## Prior art

Fedora CoreOS: Cincinnati (graph service) + Zincati (host agent) + rollout wariness.

Bottlerocket: TUF-protected updates plus wave schedules (phased rollouts) encoded as data.

## Proposal

### A) `rollout.graph` object
A signed DAG where:
- node = deployment ref digest (or host-image artifact digest)
- edge = allowed transition with optional constraints

Example constraints:
- barrier label (do not cross unless explicitly enabled)
- required attestation receipts
- min rollback index

### B) `rollout.assignment` object (optional)
A signed receipt binding:
- host identity
- approved next deployment ref digest
- policy snapshot digest

### C) Host agent behavior

- fetch and verify graph (and assignment receipts if enabled)
- compute next transition
- stage update
- reboot under local policy + optional external lock
- finalize only after health gate

## Explainability

Add an explain surface:
- `derive explain rollout`:
  - the chosen edge and its constraints
  - why other edges were rejected
  - which receipts were required/validated

## Tradeoffs

- More moving parts for large fleets.
- Needs careful UX defaults so small deployments remain simple.

