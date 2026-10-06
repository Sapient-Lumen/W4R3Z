# ADR-0042: MicroVM stop semantics (Plan→Receipt, graceful vs force)

- Status: **accepted**
- Date: 2026-03-04

## Context

DeriveBSD made microVM launch spec-able via `microvm.launch.plan` / `microvm.launch.receipt` and fixed strict launch idempotency (`ADR-0041`).

But v0 still lacked a standardized way to stop an instance without forking behavior across product shapes:

- Fleet hosts (A) need robust, receipted termination for rollouts and containment.
- Workstations (B) need reliable “stop the AppVM now” semantics.
- General-purpose (C) and appliances/regulatory (D) need explicit, auditable termination without hidden side effects.

If “stop” remains an ad-hoc backend command (signals, helper scripts, mutable state), we lose the pillars:

- **operability/forensics:** no stable join key; denials/timeouts disappear into logs
- **isolation:** stop becomes a privileged footgun with unclear authorization
- **supply chain integrity:** runtime actions stop being receipted evidence

## Decision

### 1) Stop is a first-class Plan→Receipt operation

DeriveBSD defines:

- input: `microvm.stop.plan`
- output: `microvm.stop.receipt` (emitted even on denial/failure)

This mirrors the launch contract and keeps runtime actions queryable.

### 2) Stop is host-local and bounded

`derive-vmmd` owns the host-local authority boundary:

- verify policy
- attempt stop according to requested mode
- emit receipts that bind the decision and observed state

Distributed orchestration remains external (adapter lane concern).

### 3) Two modes: graceful and force

`microvm.stop.plan.requested.mode` is:

- `graceful` (default): attempt an orderly shutdown request if the backend supports it, bounded by `timeout_ms` (policy may cap).
- `force`: terminate/destroy the backend instance (may risk data integrity).

Backends differ (bhyve, firecracker, …); the contract is intentionally abstract but implementable.

### 4) Idempotency and safety guards

On a given host:

- If the instance is not running, `derive-vmmd` emits `outcome: already-stopped`.
- If `expect_running_plan_digest` is provided and the running instance’s plan digest differs, `derive-vmmd` MUST deny with a reason such as `plan-digest-mismatch`.

This guard prevents accidental stops after explicit replacement/identity transitions.

## Consequences

- A–D share a single coherent stop surface.
- Operators and fleet tooling can always answer: “who stopped what, under which policy, and what was running then?”
- Replacement/upgrade remains explicit future work (stop + launch under a new identity or a future replace plan).

See: `docs/29-vm-control-plane.md`, `docs/455-microvm-launch-plans-and-receipts.md`, `spec/microvm.stop.plan.schema.json`, `spec/microvm.stop.receipt.schema.json`.
