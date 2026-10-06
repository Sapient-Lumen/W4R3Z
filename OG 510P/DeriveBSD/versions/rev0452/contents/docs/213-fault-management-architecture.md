# Fault management as evidence + self-healing (FMA lessons)

Traditional UNIX systems treat hardware and service faults as “logs you grep later”.
Some ecosystems (notably Solaris/illumos) treated this as a *first-class subsystem*:
structured **event reports**, diagnosis engines, response agents, and a persistent fault log.

DeriveBSD is already built around **evidence objects** and **health-gated activation**.
We should steal the FMA mindset and integrate it into the Derive pipeline *early*.

## Lessons to steal

- **FMA (Fault Management Architecture)**: detectors emit structured *ereports*; a daemon (`fmd`) runs diagnosis engines and response agents; events are stored in a persistent log and can trigger “self-healing” actions.  
  - High-level overview: https://docs.oracle.com/en/servers/management/hardware-management-pack/2.4/linux-fma-guide/fault-management-architecture-overview.html  
  - `fmd(8)` (fault manager daemon) overview + UUIDs: https://man.omnios.org/man8/fmd  
  - `fmdump(8)` (fault log viewer): https://smartos.org/man/8/fmdump  
  - `fmadm(8)` (fault manager administration): https://man.omnios.org/man8/fmadm  
  - Solaris FMA I/O fault services (ereports → diagnosis engines → agents): https://docs.oracle.com/cd/E18752_01/html/816-4854/fmaiofs.html  
  - Joyent/SmartOS background (FMA + `fmd`): https://github.com/joyent/rfd/blob/master/rfd/0006/README.md
- **ZFS event daemons** (OpenZFS / platform-specific): ZFS emits structured events that can be routed to automation.  
  - ZFS events: https://openzfs.github.io/openzfs-docs/man/v2.0/5/zfs-events.5.html

## Why DeriveBSD should care

Fault handling becomes much easier if we treat it like everything else in DeriveBSD:

- faults are **typed data**, not free-form text
- diagnosis is **separable** from detection
- remediation is **policy-bound**, auditable, and reversible where possible
- activation/rollouts can be **health-gated** on *known-bad* conditions

This is operational leverage we don’t want to bolt on later.

## Proposed primitive

Introduce an optional host service: `derive-fmd` (name placeholder).

### Inputs (detectors)

`derive-fmd` consumes event streams from:
- kernel/userland error reporters (e.g., `devd`, `crash-report` evidence objects)
- ZFS events (zevents)
- storage lane evidence (`storage-event`, `storage-health-snapshot`, `storage-scrub-receipt`)
- SMART/drive telemetry (if present)
- host-side health probes (boot + runtime)
- resource governance violations / pressure events (`resource-event`)

Detectors should be “dumb”: emit evidence, don’t make fleet policy decisions.

### Core (diagnosis + ledger)

`derive-fmd`:
- normalizes detector events into **evidence objects**
- runs small, pluggable **diagnosis rules/engines** (as modules, possibly WASM)
- persists a signed, append-only **fault ledger** (ZFS dataset recommended)

### Outputs (responses)

Responses are *policy-governed* actions such as:
- mark host generation “degraded” (affects health-gated commit)
- offline a device / drain a workload / fence a domain
- request operator attention via notification portal
- emit an actionable, stable “suspect list” for replacement

## Evidence objects

Note: `fault-event` should be stored in the host **event journal** (see `docs/215-structured-event-log-as-evidence.md`) so faults can be queried and exported uniformly with other ops signals.


Minimum v0 objects (schemas in `spec/`):

- `fault.event` — a raw, structured report (origin + class + severity + payload)
- `fault.diagnosis` — diagnosis engine output referencing one or more events
- `fault.snapshot` — a signed summary of active faults (useful for boot health gating)

Schemas:
- `spec/fault.event.schema.json`
- `spec/fault.diagnosis.schema.json`
- `spec/fault.snapshot.schema.json`

## Interaction with health-gated updates

Extend `boot.health.report` checks to include:
- “no new critical faults since last committed generation”
- “no unresolved faults in blocking classes (policy-defined)”

This allows a safe default:
- you can roll forward, but you won’t *commit* a new generation on a sick host.

Optional escalation:
- when a new **critical** fault appears, policy MAY request an `incident.bundle` capture (bounded event window + `fault.snapshot` + `svc.snapshot`) for operator/support workflows (see `docs/216-incident-snapshots-and-support-bundles.md`).

## Threat model notes

- Fault signals can be spoofed (especially from less-trusted domains). Treat each detector as an identity-bearing source.
- The ledger is part of the evidence chain: it must be tamper-evident and exportable for audits.
- Self-healing actions must be conservative by default; avoid “automations that brick machines”.

## RFC

See: `rfcs/RFC-0148-fault-management-architecture.md`

Last updated: 2026-02-24
