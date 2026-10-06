# RFC-0167: Process contracts and service boundaries

- Status: draft
- Author(s):
- Created: 2026-02-25
- Last updated: 2026-02-25

## Summary

Define a **service boundary** abstraction that makes “which processes belong to this service?” deterministic and auditable.
Steal the semantic shape of **illumos process contracts** (SMF’s “secret sauce”), while allowing multiple implementations:

- preferred: jail/microVM placement boundaries
- fallback: proc-tree tracking with stable handles
- optional long-term: a native contract subsystem

## Motivation

Service supervision is only as good as service ownership.
Pidfiles and daemonization patterns create:

- ambiguous restarts (old trees linger)
- rollback that doesn’t fully roll back
- flapping and split-brain behavior
- confusing incident bundles (what was running?)

Illumos solved this by pairing SMF with process contracts (fault boundary + event delivery).
DeriveBSD should bake the *contract* into the data model early.

Primary references:
- contract filesystem (`contract(4)`): https://docs.oracle.com/cd/E26502_01/html/E29042/contract-4.html
- process contracts (`process(4)`): https://docs.oracle.com/cd/E86824_01/html/E54775/process-4.html
- SMF (`smf(7)`): https://smartos.org/man/7/smf

## Goals

- A stable cross-runtime concept: “service boundary” works for host services, service jails, and microVMs.
- The svcdb compiler emits explicit boundary intent.
- Restarters can:
  - query membership
  - apply deterministic kill semantics
  - emit boundary events into the structured journal

## Non-goals

- Perfect compatibility with illumos contract semantics.
- A large general-purpose kernel policy facility.

## Proposal

### 1) Extend `svcdb` with optional service boundary intent

In `spec/svcdb.schema.json`, extend `services[].security` with a new optional object:

- `service_boundary.mode`: `jail | microvm | proc-tree | contractfs`
- `service_boundary.escape_policy`: `deny | allow-with-cap | allow`
- `service_boundary.owner`: restarter id

Backwards compatible: absent fields mean “legacy/best-effort”.

### 2) Runtime reporting

Restarters MUST write into `svc.snapshot` and `svc.event`:
- boundary mode
- boundary id (`jail_id`/`vm_id`/`contract_id`)
- membership summary (count, last scan)
- restart/kill actions

### 3) Fault escalation

A “boundary breach” (unowned processes detected, or escape policy violated) SHOULD:

- emit `fault.event` + diagnosis
- optionally trigger an `incident.bundle`
- transition the service to `maintenance` rather than thrash

### 4) Preferred implementation order

- **First choice**: run the service in a jail/microVM boundary.
- **Second choice**: proc-tree tracking with a stable handle and reconciliation.
- **Optional**: a minimal kernel contract facility, if the platform chooses to build it.

## Security considerations

- Boundaries reduce persistence-by-accident but do not replace MAC/lockdown.
- Escape must be policy-gated; “allow” should be rare and reviewed.
- Boundary ids and membership summaries are sensitive metadata; treat them as observability surfaces governed by capability.

## Open questions

- Should we introduce a dedicated evidence object (e.g., `proc.tree.snapshot`) or keep it embedded in `incident.bundle` payloads only?
- What is the minimum viable proc-tree tracking mechanism on FreeBSD (procdesc/procctl/kqueue) that yields good semantics?

See also: `docs/235-process-contracts-and-service-ownership.md`, `docs/214-service-supervision-health-as-evidence.md`.
