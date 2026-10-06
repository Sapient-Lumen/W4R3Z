# Service supervision + health as evidence (SMF / s6-rc / contracts lessons)

DeriveBSD already treats *builds*, *policy*, and *updates* as structured artifacts.
A missing “ops primitive” most systems bolt on late is: **service supervision as typed, inspectable state**.

The lesson to steal:
- **SMF**: services have explicit dependencies, an explicit state machine (`online/offline/degraded/maintenance/...`), and *restarters* that drive transitions.
- **s6-rc**: service management can be an *offline-compiled database* (graph + bundles), enabling analyzable transitions.
- **Process contracts (illumos) + service ownership**: supervision becomes much more robust when the restarter owns a *fault boundary* around a service’s whole process tree.

DeriveBSD can keep **rc.d/service-jails** as an executor, but should commit to the **data model** early.

See also:
- Lifecycle + restarters deep dive: `docs/239-service-lifecycle-restarters-and-repo.md`, RFC-0171
- Service ownership boundaries: `docs/235-process-contracts-and-service-ownership.md`, RFC-0167
- Activation patterns: `docs/238-portal-activated-services-and-socket-activation.md`, RFC-0170
- Optional host identity leases: `docs/240-dynamic-service-identities.md`, RFC-0172

References:
- SMF overview (`smf(7)`): https://smartos.org/man/7/smf
- SMF state model paper (LISA’05): https://www.usenix.org/event/lisa05/tech/full_papers/adams/adams.pdf
- s6-rc overview (compiled service DB + bundles): https://skarnet.org/software/s6-rc/overview.html
- FreeBSD “service jails” status report (automatic jailing of rc.d services): https://www.freebsd.org/status/report-2024-04-2024-06/service-jails/
- illumos process contracts (`process(5)`): https://smartos.org/man/5/process
- DeriveBSD deep dive: `docs/235-process-contracts-and-service-ownership.md`

## Why bake this in now

If services remain “best-effort scripts”, we lose:
- reviewability (“what changed?”)
- stable observability interfaces (every daemon reinvents “status”)
- reliable rollback/health gating (service failures become ambiguous logs)

A greenfield OS can instead define:
- **the service graph** (what *should* exist)
- **the supervision contract** (who owns failures + restarts)
- **the health snapshot** (what *is* happening right now)
…as first-class artifacts.

## Core artifacts

### 1) `svcdb` (compiled service database)

Derived from the Plan. Think: “offline-compiled service DB” even if the runtime executor is rc.d.

Contains:
- service instances + placement (host/jail/microVM)
- dependency edges
- restart policy (with explicit limits / windows)
- resource budgets + pf anchors + mount sets
- links to capsets / portal grants (optional)

Schema: `spec/svcdb.schema.json`  
Example: `spec/examples/svcdb.json`

### 2) `svc.snapshot` (runtime service state)

A minimal, stable snapshot of current service states:
- observed state (`online/offline/degraded/maintenance/...`)
- last transition / reason
- restart counters
- optional service boundary handle digest (`svc-contract-handle`) for deterministic ownership/kill semantics
- pointers to evidence objects (logs, crash reports, replay capsules, fault events)

Schema: `spec/svc.snapshot.schema.json`  
Example: `spec/examples/svc.snapshot.json`

### 3) `svc.event` (state transitions + supervision events)

When a service crashes, supervision should also emit a `crash-event` and a `crash-report` evidence object (metadata-first; dump capture is policy-gated).


Append-only events emitted by the restarter/activation broker:
- state transition (offline → online)
- restart attempt (with backoff)
- crash / exit
- maintenance entry (operator action required)

Schema: `spec/svc.event.schema.json`  
Example: `spec/examples/svc.event.json`

Note: `svc-event` should be stored in the host **event journal** (see `docs/215-structured-event-log-as-evidence.md`) so supervisors, faults, and audit/policy milestones share one query/export plane.

## The supervision contract (DeriveBSD stance)

### A) Explicit states are operator UX

Adopt the **state vocabulary** early (even if the executor is rc.d):
- `uninitialized`, `offline`, `online`, `degraded`, `maintenance`, `disabled` (+ optional `legacy-run`)

This makes “health gating” and fleet rollouts legible: “booted but `maintenance`” is different from “never started”.

### B) Restarters own failure semantics

A restarter is a small daemon (or activation broker mode) that:
- consumes `svcdb`
- drives transitions toward target bundles (`base`, `net`, `control-plane`, `workloads`)
- emits `svc.event` and `svc.snapshot`
- escalates persistent failure into `fault.event` (see `docs/213-fault-management-architecture.md`)

### C) “Contract boundaries” avoid orphan trees

If the platform supports it, use a contract-like mechanism:
- restarter creates a boundary for a service’s process tree
- events are delivered to the restarter (exit, core dump, resource violations)
- on restart, the restarter can reliably reap/terminate leftover descendants

If BSD lacks a direct analog, emulate via:
- process group/session ownership
- pidfile + procstat enumeration
- jail/microVM boundary as the strongest option

The critical design requirement is **semantic ownership**: “these processes belong to service X”.

## Integration points

- **Resource governance**: the restarter ensures the full service tree is inside the intended resource domain (from `resource-policy`) before declaring `online`.

- Health gating: `boot.health.report` can include a check that consumes `svc.snapshot` and fails commit if critical bundles are not `online`.
- Config transactions: `config-receipt` can request reload/restart actions (for specific bundles), and supervision should record those transitions as `svc.event` (see `docs/218-configuration-transactions-and-receipts.md`, RFC-0153).
- Policy engine: policies can forbid “restart storm” patterns, or require that certain services run only in service jails/microVMs.
- Fault management: repeated service failures become diagnosable faults, not “someone saw syslog”.
- Incident bundles (optional): persistent flapping or crash loops MAY trigger an `incident.bundle` capture for support/postmortems (bounded event window + `svc.snapshot`) (see `docs/216-incident-snapshots-and-support-bundles.md`).

See also:
- `docs/114-service-manifests-smf-lessons.md`, RFC-0082
- `docs/173-compiled-service-database-bundles.md`
- RFC-0149 (service supervision + health evidence)

Last updated: 2026-02-24
