# RFC-0171: Service lifecycle states, restarters, and repository semantics

Status: Draft  
Last updated: 2026-02-25

## Problem

DeriveBSD already has the right primitives for supervision as evidence (`svcdb`, `svc.snapshot`, `svc.event`),
but the contract is underspecified:

- events don’t consistently identify *which instance* (future multi-instance support)
- state names risk drifting between components
- “restarter separation” is referenced but not made explicit in data contracts
- boot/update gates need a stable, canonical state model

## Goals

- Define a **canonical lifecycle state enum** for service supervision outputs.
- Introduce **instance_id** as an optional discriminator across supervision artifacts.
- Clarify “repository semantics”: `svc.snapshot` is the authoritative observed-state surface.
- Keep the design compatible with:
  - delegated restarters (jails, microVMs, activators)
  - process ownership boundaries (contracts/compartments)
  - health-gated A/B updates

## Non-goals

- Full SMF manifest language compatibility.
- Replacing `svcdb` with an SMF repository clone.
- Defining every restarter plugin API in detail (that can be a later RFC).

## Proposal

### 1) Canonical lifecycle states

Standardize the observed states to:

- `uninitialized`
- `offline`
- `online`
- `degraded`
- `maintenance`
- `disabled`
- `legacy-run`

These are already present in `svc.snapshot`; this RFC makes them canonical across:
- `svc.snapshot`
- `svc.event` (from_state/to_state)

### 2) Add optional instance_id

Add optional `instance_id` (string) to:
- `svc.event` (default semantic: `"default"`)
- `svc.snapshot.services[*]`

This is forward-compatible with templated/sharded services without changing `service_id` formats.

### 3) Tighten `svc.event` transitions

- `event_type="state-transition"` MUST include `from_state` and `to_state`
- `event_type in {"maintenance-enter","maintenance-exit"}` SHOULD include states
- `event_type="contract-event"` MAY include `meta.contract_id`

### 4) Repository semantics

- `svc.snapshot` is the authoritative observed state.
- Supervisors SHOULD emit:
  - periodic snapshots (for “last known state”)
  - transition events (for forensic and gating context)

Boot/upgrade gates MUST NOT be implemented via process scraping; they should query `svc.snapshot`.

## Data contract changes

- Update `spec/svc.event.schema.json`:
  - add `instance_id`
  - constrain `from_state`/`to_state` to enum
- Update `spec/svc.snapshot.schema.json`:
  - add optional `instance_id` per service
- Update examples accordingly.

## Rollout plan

1) Bump examples and schema versions (still `0.x`).
2) Update the master restarter and any delegated restarters to populate `instance_id="default"` for now.
3) Update gating policy modules to treat missing instance_id as `"default"`.

## Risks / tradeoffs

- Slightly tighter schemas may reveal previously “loose” implementations.
- Multi-instance semantics can be overused; the default remains single-instance.

## Related

- `docs/214-service-supervision-health-as-evidence.md`
- `docs/235-process-contracts-and-service-ownership.md`
- `docs/238-portal-activated-services-and-socket-activation.md`
- `docs/231-ab-updates-and-recovery-semantics.md`
