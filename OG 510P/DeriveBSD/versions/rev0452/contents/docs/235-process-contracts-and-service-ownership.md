# Process contracts + service ownership (SMF’s “secret sauce”)

DeriveBSD already treats **service supervision** as a typed, inspectable subsystem (`svcdb`, `svc.snapshot`, `svc.event`).
One of the hardest real-world failure modes to eliminate is still:

- a service “daemonizes”
- grandchildren outlive the parent
- pidfiles lie, processes get reparented
- restarters restart the “main” pid while the old tree keeps running
- rollback/health gating becomes ambiguous (“is the old one still there?”)

Solaris/illumos solved this *architecturally* with **process contracts** and then built **SMF restarters** on top.
This doc captures the lesson in a DeriveBSD-native shape.

References (primary):
- contract filesystem (`contract(4)`): https://docs.oracle.com/cd/E26502_01/html/E29042/contract-4.html
- process contract type (`process(4)`): https://docs.oracle.com/cd/E86824_01/html/E54775/process-4.html
- SMF overview (`smf(7)`): https://smartos.org/man/7/smf
- Oxide RFD note (SMF + contracts): https://26.rfd.oxide.computer/

## What “service ownership” means

A service restarter needs a stable answer to:

1) **Which processes belong to service X?**
2) **When is service X *really* dead?**
3) **What exactly must be killed/reaped before restart/rollback?**

DeriveBSD stance:

- “Service ownership” is a **boundary object**.
- It is allowed to be implemented by multiple mechanisms.
- But it must present a **single semantic contract** to `derive switch`, health gates, rollbacks, incident bundles, and operators.

## The contract lesson (illumos)

A process contract is a kernel-supported **fault boundary** around a process tree:

- a restarter can create a contract, start the service inside it
- descendants are tracked under the contract
- events are delivered (exit, core, errors)
- the restarter can kill *the contract* rather than guessing pids

DeriveBSD doesn’t have to copy the implementation, but we should steal the **shape**:

- a stable identifier: `contract_id`
- a policy for escapes (“can this service spawn unowned daemons?”)
- a query surface for membership (“show me the tree”)
- deterministic kill semantics (“terminate everything in the boundary”)

## DeriveBSD design: “service boundaries” (portable layers)

### Layer 0: boundary by placement (strongest, already aligned)

For many services, the best answer is: **put it in a container boundary**.

- service-jail boundary (host jails)
- microVM boundary (workload VMs)

This gives:
- clean process ownership
- crisp resource accounting
- easy teardown

### Layer 1: boundary by process descriptor + tree tracking (BSD-friendly)

If a service must run on the host, DeriveBSD can emulate “contract semantics” with:

- a *stable handle* to the parent process (procdesc/pidfd-like)
- explicit tracking of descendants at spawn time
- periodic reconciliation (walk `procstat`/kvm, verify membership)
- best-effort kill semantics over the tracked set

This is weaker than kernel contracts (races exist), but still much better than pidfiles.

### Layer 2: native contract subsystem (long-term, optional)

A greenfield BSD derivative can consider a small kernel facility:

- a contract object with membership rules
- a minimal event stream (delivered to the restarter)
- “kill contract” as a privileged operation

If we do this, we should keep it **narrow**:
- only what service supervision needs
- avoid general-purpose “policy engines in kernel”

## How it plugs into existing DeriveBSD artifacts

### `svcdb` (compile-time intent)

Add (optional) fields under `services[*].security`:

- `service_boundary.mode`: `jail | microvm | proc-tree | contractfs`
- `service_boundary.escape_policy`: `deny | allow-with-cap | allow`
- `service_boundary.owner`: which restarter owns this boundary

The important part is that **the compiler emits an analyzable choice**, not a runtime guess.

### `svc.snapshot` / `svc.event` (runtime truth)

Restarters should record:
- boundary type + boundary id (`jail_id`, `vm_id`, `contract_id`)
- membership summary (counts, last scan)
- kill/restart actions as explicit `svc.event`

### Evidence + incident bundles

When services flap, a contract boundary makes “support bundles” safer and more useful:

- include a **bounded** `proc.tree.snapshot` (metadata only)
- include the boundary id and recent boundary events

See: `docs/216-incident-snapshots-and-support-bundles.md`, `docs/214-service-supervision-health-as-evidence.md`.

To make boundaries concrete in evidence surfaces, DeriveBSD introduces an explicit contract handle object:
`docs/243-service-contract-handles-and-membership.md` (RFC-0175), `spec/svc.contract.handle.schema.json`.

## Lints (meta-engineering)

Service-boundary intent is lintable:

- “daemonizes” without boundary escape declared → warn
- “spawns workers” but boundary is `proc-tree` and restart policy is aggressive → warn
- boundary is `host` but promise profile requests `proc_exec` → require explicit justification

See: `docs/232-service-promise-profiles.md`, `docs/237-lint-reports-and-contract-testing.md`.

## Threat model impact

- **Reduces persistence-by-accident**: orphaned subprocesses are a common “rollback didn’t really roll back” failure mode.
- **Reduces stealth**: boundary membership is queryable and auditable.
- **Makes kill semantics explicit**: “kill the service” has deterministic meaning.

## Failure modes

- If boundary enforcement fails (kernel bug / escape), the restarter must:
  - emit a `fault.event` (“service-boundary-breach”)
  - optionally capture an `incident.bundle`
  - enter `maintenance` rather than thrash

See: `docs/213-fault-management-architecture.md`, RFC-0167.

Last updated: 2026-02-25
