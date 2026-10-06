# SMF-style service lifecycle, restarters, and repository semantics

DeriveBSD already leans on service supervision as a *typed* surface (`svcdb`, `svc.snapshot`, `svc.event`).
This document tightens the model by stealing the **best parts of SMF** (Solaris/illumos) without importing its entire ecosystem.

The goal: make “what is happening on the machine?” answerable as a **diffable state machine** with **clean ownership boundaries**.

## Key lesson to steal (SMF)

SMF’s big win is not “a daemon starts other daemons”.
It’s that *every service instance* is driven by:

- a **restarter** (master or delegated) that owns lifecycle transitions
- a **repository** that persists desired config and last-known state
- a **state model** with explicit “operator attention required” states (`maintenance`) and “running but impaired” (`degraded`)

DeriveBSD direction: express the same contract with smaller primitives and stronger evidence guarantees.

## DeriveBSD model (tightened)

### 1) Service identity vs service instance

- **service_id**: logical service name (stable across boots and updates)
- **instance_id**: instance discriminator (default: `"default"`)

Most deployments will be single-instance; instance_id exists for:
- templated services (e.g. “per-interface DHCP client”)
- sharded services (e.g. multiple fetchers with distinct resource envelopes)
- multi-tenancy (same service definition bound to multiple placements)

### 2) Desired vs observed

**Desired** comes from config + policy (compiled into `svcdb`), and is intentionally simple:

- `enabled`
- `disabled`

**Observed state** is the restarter’s evaluation of reality.
It must be *monotonic with evidence*: every transition has an attributable reason and optional evidence digests.

### 3) Lifecycle states (canonical set)

DeriveBSD standardizes the following states (already used in `svc.snapshot`):

- `uninitialized` — seen, but not yet evaluated/attempted
- `offline` — enabled, but not currently running (may be pending deps)
- `online` — running and meeting health criteria
- `degraded` — running, but health criteria are failing / partial functionality
- `maintenance` — stopped and will not auto-restart until operator (or automation) intervenes
- `disabled` — administratively disabled
- `legacy-run` — managed by legacy rc(8) path / transitional mode

### 4) Restarters: separation of concerns

DeriveBSD uses **restarter separation** to keep special execution environments out of the “general” supervisor.

- **master restarter**: dependency evaluation, ordering, retries, and state storage for most services
- **delegated restarters**: implement specialized execution environments:
  - jail restarter (jail lifecycle, resource envelopes)
  - microvm restarter (bhyve/firecracker orchestration)
  - activator (socket/portal activation, fd handoff)
  - (future) anykernel/rump test restarter for “kernel-adjacent” components

Restarters are *pluggable components* but the contract is stable: all restarters emit `svc.event` and contribute to `svc.snapshot`.

### 5) Ownership boundary (contracts / compartments)

A restarter must be able to answer: “what processes belong to this service?”
Preferred ownership boundaries:

1. **Compartment boundary** (microVM / jail): strongest semantics, simplest accounting
2. **Contract boundary** (process contract concept): restarter holds an unforgeable handle that represents the subtree
3. **Fallback** (proc-tree tracking): best-effort for legacy host services

See: `docs/235-process-contracts-and-service-ownership.md`.

### 6) Repository semantics: “svc.snapshot is a product”

SMF has a persistent repository; DeriveBSD’s equivalent is:

- compiled intent: `svcdb` (from plan/apply)
- persistent observed state: `svc.snapshot` (periodic + on-change)
- structured transitions: `svc.event` (append-only)

Important rule: **boot success and update promotion can only rely on `svc.snapshot`**, never on ad-hoc `ps`/pidfile scraping.

## Integration points

### Health-gated updates
A/B commit should require:
- platform posture ok (`docs/226-*`)
- no services in `maintenance` for required bundles
- a bounded number of `degraded` services (policy-defined)

See: `docs/231-ab-updates-and-recovery-semantics.md`.

### Fault management
Fault diagnoses can drive lifecycle:
- `online → degraded` when impairment detected
- `online/degraded → maintenance` when continuing would risk corruption or safety

See: `docs/213-fault-management-architecture.md`.

### Activation
Socket/portal activation moves “listening endpoint ownership” to the activator restarter, and simplifies upgrades.

See: `docs/238-portal-activated-services-and-socket-activation.md`.

## Evidence contract additions (minimal, immediate)

- Add optional `instance_id` to `svc.event` and `svc.snapshot` entries.
- Tighten `from_state`/`to_state` to the canonical enum set, to prevent drift.
- Encourage (optional) `meta.contract_id` and `meta.restarter_kind` for better observability.

## Related lessons

- Supervision trees + restart intensity (OTP vocabulary): `docs/349-supervision-trees-and-restart-strategies.md`.
- Crash-only recovery discipline (MTTR-first): `docs/352-crash-only-and-roc-for-system-services.md`.

## Open questions

- Do we want `refresh` as a first-class transition (SMF has it)?
- Do we model `degraded` with typed sub-reasons (health checks vs dependency impairment)?
- How do we represent “dependency-induced offline” vs “execution-induced offline” succinctly?

See RFC: `rfcs/RFC-0171-service-lifecycle-states-and-restarters.md`.
