# Hypervisor-centric DeriveBSD

This document defines a DeriveBSD direction where **virtualization is the default runtime isolation boundary** for services and workloads.

The core idea:
- **DeriveBSD remains the factory and control plane** (secure build, signing, provenance, rollbacks).
- The system prefers to run *most* workloads inside **microVMs** (and sometimes jails), rather than directly on the host.

This is “Dom0, but sane”: keep the host small, locked down, and auditable; push complexity into replaceable, signed artifacts.

---

## Why hypervisor-centric?

### Security goals it helps
- **Blast-radius reduction**: compromise of one workload doesn’t imply compromise of neighbors.
- **Clear boundaries**: VM boundary is hardware-enforced; policy is centralized.
- **Safer upgrades**: workloads roll by replacing images, not mutating live systems.
- **Mixed assurance**: different workloads can have different TCB sizes.
- **Hardware blast-radius reduction**: isolate risky device classes in dedicated device domains (driver VMs) instead of expanding the host TCB (see `docs/204-device-isolation-domains.md`).

### Security risks it introduces
- More moving parts (hypervisor + virtual devices + network layers).
- Device/DMA complexity if passthrough enters the picture.
- Control-plane compromise is high impact → host must be minimal + constrained.

---

## Principles (hypervisor edition)

1. **Least authority**
   - Workloads cannot manage the host or other VMs.
   - A minimal control daemon owns hypervisor privileges.

2. **One workflow, multiple targets**
   - Still: Spec → Lock → Plan → Artifact.
   - Add a first-class artifact target: **microVM images**.

3. **Immutable, verifiable images**
   - Deploy signed images + manifests.
   - Updates = build new image, switch pointer, restart.

4. **Jails for builds; VMs for runtime**
   - Build isolation: jails (default).
   - Runtime isolation: microVMs (default), jails (optional lighter-weight).

5. **ZFS as rollback substrate**
   - Host rollback: ZFS boot environments.
   - VM images: ZFS snapshots/clones when available.

---

## Architecture overview

### Host (“control plane”)
- Minimal DeriveBSD system closure:
  - builder/store/verifier
  - vm manager + bridge + pf policy
  - logging/metrics (minimal)
- Host itself is generation-based and rollbackable.

### Workloads
- MicroVM workloads:
  - image payload derived from closure
  - explicit config injection
  - explicit secrets interface
  - minimal network surface
- Optional jails:
  - used when shared-kernel isolation is acceptable
  - still derived and policy-governed

---

## Measurable outcomes
- A service can ship as a signed microVM artifact with provenance.
- A node can roll back host and workloads cleanly.
- We can answer: “who signed this image?” and “which sources produced it?”


Last updated: 2026-02-23
