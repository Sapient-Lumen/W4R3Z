# VM control plane: derive-vmmd

One minimal privileged service owns hypervisor privileges and enforces policy.
Everything else is unprivileged tooling.

DeriveBSD keeps this boundary **host-local**: `derive-vmmd` is not a cluster scheduler.
See: `adrs/ADR-0040-microvm-orchestration-host-local.md`.

## Responsibilities
- verify artifact signatures before launch
- realize a compiled runtime contract into backend calls (bhyve + helpers)
- attach storage/network within policy bounds
- manage lifecycle boundaries (launch + stop are Plan→Receipt; replacement remains explicit future work)
- emit **typed receipts** (who launched/stopped what, with which digests, under which policy)

## The stable contract (Plan → Receipt)

To keep runtime explainable, the control plane is spec-able:

- input: `microvm.launch.plan` (digest-bound request)
- output: `microvm.launch.receipt` (typed evidence, emitted even on denial)

- input: `microvm.stop.plan` (digest-bound request)
- output: `microvm.stop.receipt` (typed evidence, emitted even on denial/failure/timeout)

See: `docs/455-microvm-launch-plans-and-receipts.md`, `adrs/ADR-0041-microvm-instance-idempotency.md`, `adrs/ADR-0042-microvm-stop-semantics.md`.

## Privilege separation
- `derive vm ...` CLI (unprivileged)
- `derive-vmmd` (privileged, minimal API)
- backend helpers (optional; jailed/capsicum’d where possible)

## AuthZ (v1)
- local unix socket API by default
- rules match on signing key / namespace / target kind
- enforce resource ceilings and network attachment constraints

## Audit invariants
Every action logs actor + plan digest + policy digest + instance_id + timestamp.

See: `rfcs/RFC-0013-vmmd-control-plane.md`.

Last updated: 2026-03-04r180
