# RFC-0157: Resource governance as evidence (resource-policy / snapshot / receipt / events)

Status: draft  
Last updated: 2026-02-24

## Problem
DeriveBSD is intentionally “ops-first”:
- updates are commits
- config and state transitions are explicit plans + receipts
- supervision and faults are typed events

Resource governance is often where systems regress to folklore:
- daemon-specific flags and unit files
- emergency `sysctl` / `ulimit` / “just reboot it”
- no consistent audit surface or rollout story

For a fleet OS, this is unacceptable.
We need: **resource policy as a first-class artifact** that participates in change orchestration.

## Goals
- A single object (`resource-policy`) can answer: **who is allowed to consume what**.
- Applying policy always emits evidence (`resource-receipt`).
- The system can produce a compact `resource-snapshot` for health gates and incident bundles.
- Violations are typed (`resource-event`) and can trigger actions (throttle/kill/fault/bundle).
- Enforcement is capability-governed (no ambient “root can always do anything”).

## Non-goals
- Replacing all per-application tuning knobs.
- Perfect cross-platform parity with Linux cgroups.
- Solving “fair scheduling” globally (we only provide the primitives + policies).

## Data model

### resource-policy
A policy is a list of *scopes*.
Each scope binds:
- a **subject** selector (service name, workload identity label, jail id, vm id, user/group)
- optional **priority class** (latency-critical, best-effort, batch)
- resource controls:
  - CPU: cap, shares, allowed CPU set
  - Memory: max bytes, swap policy, OOM action
  - IO: read/write rate, iops, device class binding
  - PIDs/threads/fds: count limits
- breach strategy:
  - threshold(s)
  - actions (emit event, throttle, kill, restart, emit fault, capture bundle)

The schema intentionally allows extension.

### resource-receipt
Receipts are append-only evidence of attempts:
- `applied_at`, `result`, `backend`
- rule materialization (strings or structured rules)
- `policy_ref` (digest)
- correlation to the `change-set` step

### resource-snapshot
Snapshots are the query surface:
- effective limits
- current usage summary (coarse)
- pressure summary (cpu/mem/io), when available
- recent violation counters

### resource-event
Events are records in the structured event journal.
Classes include:
- `resource.policy.applied`
- `resource.violation.<resource>`
- `resource.pressure.<resource>`
- `resource.action.<action>`

Each event should carry:
- subject identity
- resource type
- measured value + limit
- action taken (if any)

## Apply semantics

### Where policy comes from
There are two common sources:
1) **Fleet policy**: a `resource-policy` object produced and signed by the org.
2) **Workload hints**: `svcdb` manifests may carry resource “hints” (soft defaults).
   The compiler can materialize them into a concrete policy, but fleet policy wins.

### How it is applied
`change-set` gains an `apply-resource-policy` step:
- the apply engine selects a backend (e.g., rctl/cpuset)
- it computes a minimal diff vs the current rule set
- it applies and emits a `resource-receipt`
- it emits a `resource.policy.applied` event

### On violation
Violation detection can live in:
- kernel enforcement callbacks (preferred when available)
- a minimal userspace watcher reading usage/pressure

On breach, the policy may:
- emit `resource-event`
- emit a `fault-event` (if configured)
- request an incident bundle capture
- request service restarter action (restart/maintenance)

## Security / privacy
- `resource-policy` should avoid leaking sensitive workload names; prefer workload identity labels.
- `resource-snapshot` must be redactable (policy-controlled).
- Delegation: a service may adjust *within* its budget (optional), but must not increase global budgets without authority.
- Violation events must not enable cross-tenant inference (coarse metrics, policy-gated access).

## Integrations
- `docs/214-service-supervision-health-as-evidence.md`: supervision owns the process tree and can enforce “limits apply to the whole service”.
- `docs/213-fault-management-architecture.md`: repeated violations can become faults.
- `docs/215-structured-event-log-as-evidence.md`: journal stores resource events.
- `docs/216-incident-snapshots-and-support-bundles.md`: include snapshot/policy/receipt by default.
- `docs/112-health-gated-updates.md`: pressure can be a gate input.

## Open questions
- Pressure signal implementation on BSD (PSI-like counters vs scheduler wait accounting).
- IO shaping primitives on FreeBSD hosts (per-dataset, per-device, per-jail).
- Delegation model: what knobs can a workload adjust without violating fleet policy?

