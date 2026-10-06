# Service contract handles and membership (kill the boundary, not the PID)

Service supervision gets dramatically simpler when the supervisor can answer:

> “Which processes belong to this service instance, right now?”

Most Unix ecosystems approximate this with pidfiles, process tree walks, and brittle heuristics.

Illumos/Solaris process contracts are a rare example of treating “a service’s process set” as a first-class boundary.

DeriveBSD should bake in a compatible **service ownership handle** concept that is:
- stable enough to use in receipts, incident bundles, and health gates
- flexible across backends (jail domains, bhyve domains, classic host processes)

## The core idea

Each supervised service instance has a **contract handle**:
- an opaque identifier that represents “the boundary of this service instance”
- used for lifecycle operations (restart/stop/kill)
- used for evidence (membership changes, exit reasons)

### Minimal contract operations

- create boundary
- add a child process (or attach a domain)
- observe events:
  - member spawned
  - member exit/crash
  - boundary empty
  - boundary violated (unexpected parentage / unauthorized exec)
- destroy boundary

## Mapping to DeriveBSD runtime shapes

### 1) Jail-backed services (preferred)

If a service runs in its own jail (or a small set of jails), the jail boundary already provides:
- membership semantics
- kill semantics
- resource control scoping

The “contract handle” becomes a reference to:
- jail id/name
- restarter id
- service id + instance id

### 2) MicroVM-backed services

For microVM-first services, the boundary is the VM itself.
The handle can reference:
- VM instance id
- hypervisor worker domain
- device backend domain(s)

### 3) Classic host-process services

Some services will run as host processes, at least early on.
DeriveBSD should standardize a fallback implementation:

- place the service in a dedicated process group/session
- track membership via procfs + kqueue (or a small supervisor-owned registry)
- record events and emit receipts

This still improves determinism even without kernel-native contracts.

## Evidence integration

### New typed object: `svc-contract-handle`

A contract handle becomes a small evidence object:
- stable handle id
- bound to service id + instance id
- identifies the boundary backend (jail/microvm/procgroup)

See: `spec/svc.contract.handle.schema.json`.

### Wire into `svc.snapshot` and `svc.event`

- `svc.snapshot.services[].contract_handle_digest` (optional)
- `svc-event` adds `contract_handle_digest` for `event_type=contract-event` and crash/restart events when known

### Incident bundles

When a service crashes repeatedly or enters maintenance, bundles should include:
- the latest `svc.snapshot`
- recent `svc-event`s
- the referenced contract handle object

## Why bake this in now?

It’s the difference between:
- “restart the service” meaning “send signals to whatever we think is the service”, and
- “restart the service” meaning “kill/replace the exact boundary we created”.

Once the ecosystem grows around pidfile folklore, it’s extremely hard to retrofit a better model.

## Related

- Service supervision as evidence: `docs/214-service-supervision-health-as-evidence.md`
- Process contracts direction note: `docs/235-process-contracts-and-service-ownership.md`
- Service lifecycle + restarters: `docs/239-service-lifecycle-restarters-and-repo.md`

Last updated: 2026-02-25
