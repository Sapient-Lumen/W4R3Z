# MINIX 3 lessons: self-healing components and the “reincarnation server”

MINIX 3 is a reminder that reliability can be *architected*:
move risky code (drivers/servers) out of the kernel, restrict their authority,
then restart/replace them when they fail.

Its most distinctive idea is the **reincarnation server**:
- monitors OS services/drivers
- detects crashes/hangs
- restarts components from a known-good image
- aims for recovery without reboot

DeriveBSD is not a microkernel project, but the *operational lesson* maps cleanly:
**treat privileged subsystems as restartable units with explicit state boundaries**.

## Why this is relevant to DeriveBSD

DeriveBSD already leans toward:
- compartmentalized control planes (`docs/115-compartmentalized-control-planes.md`)
- jailed hypervisor workers (`docs/121-jailed-hypervisor-workers.md`)
- service supervision and restarters (`docs/214-service-supervision-health-as-evidence.md`)

MINIX adds a useful discipline:
- assume components fail
- ensure they can be replaced without corrupting state
- make the replacement itself observable and auditable

## DeriveBSD mapping

### 1) Make state boundaries explicit

For every privileged subsystem (network broker, secrets broker, update applier, device backend):
- identify the state it owns
- push durable state into a ZFS dataset or a small state service (`docs/217-state-datasets-and-migrations-as-evidence.md`)
- keep the worker itself as close to “stateless” as possible

If the worker crashes:
- restart is safe
- the system can emit a receipt capturing “restart happened” and why

### 2) Restart-as-evidence

If we bake this in, component restarts become first-class evidence objects:
- which unit restarted
- what watchdog triggered
- what state epoch it was operating on
- whether recovery was clean

This supports:
- incident bundles
- fleet rollouts (detect regressions by restart rates)
- policy gates (“too many restarts → fail health gate”)

### 3) Apply to “danger zones” first

High-leverage targets:
- hypervisor workers and device backends
- update/install appliers (avoid bricking loops)
- network brokers / egress gateways
- key/crypto brokers

This is compatible with the DeriveBSD posture:
- use jails/microVMs as the fault containment boundary
- use supervision + evidence for diagnosis and rollbacks

## “Bake-in now” feature

**A restart budget + restart receipts**

Add to the system contract:
- every critical unit has a restart budget
- every restart emits a typed event/receipt
- health-gated updates can consult restart evidence

This makes “self-healing” measurable and keeps it from turning into silent flapping.

## References

- “A Lightweight Method for Building Reliable Operating Systems” (Herder et al.): https://www.minix3.org/doc/reliable-os.pdf
- “MINIX 3: Status Report and Current Research” (Tanenbaum, ;login: 2010): https://www.usenix.org/system/files/login/articles/61781-tanenbaum.pdf
- MINIX 3 OSR 2006 paper (multiserver reliability work): https://minix3.org/doc/OSR-2006.pdf

Last updated: 2026-02-27
