# Template microVMs and disposable instances (Qubes disk model lessons)

Qubes OS shows a very practical split between:
- an **immutable base root** shared by many VMs (template)
- per-VM **private persistent** storage
- per-boot **volatile** storage that is discarded on restart

Qubes documents this as multiple block devices per VM, including a base root device plus separate private and volatile devices. (ref: “Template implementation” https://doc.qubes-os.org/en/latest/developer/system/template-implementation.html)

Qubes also highlights that updates are naturally centralized because updating a template updates all VMs based on it after restart. (ref: “Templates” https://doc.qubes-os.org/en/latest/user/templates/templates.html)

## DeriveBSD mapping (microVM-first)

DeriveBSD can standardize a similar model for microVM workloads:

- **Base (template)**: an Artifact-provided root dataset/zvol/image (read-only by default)
  - identified by bundle digest
  - fully explainable (“why/what/where-from”) and rollbackable

- **Private (persistent)**: per-instance state volume
  - contains only workload state (e.g., `/var`, app data)
  - NOT part of the Artifact closure; it is attached by policy + instance identity
  - can be encrypted and/or stored on a different pool

- **Volatile (ephemeral)**: per-boot scratch volume
  - discarded at shutdown/reboot
  - used for swap, temp files, crash dumps, staging

Optional:
- **Modules/firmware disk** for cases where the guest needs a separate, tightly scoped set of kernel modules/firmware (mirrors Qubes’ “modules.img” idea).

## Why this is worth baking in early

- **Updates without state churn**: a new base digest can roll out without migrating app state.
- **Storage efficiency**: instances share base bytes; private storage grows only with real state.
- **Blast-radius clarity**: base compromise vs state compromise is explicit; volatile state is intentionally discardable.
- **Disposable workloads**: a “DispVM-like” mode is just: (base + volatile only) with no private volume.

## v1 invariants (tight)

- The runtime manifest MUST explicitly declare which devices are:
  - base (immutable)
  - private (persistent)
  - volatile (ephemeral)

- Policy MUST be able to enforce:
  - “no private volume” (disposable mode)
  - “private is encrypted”
  - “private cannot be shared between instances”

- `derive explain` MUST show:
  - base bundle digest
  - private volume identity + encryption status
  - whether the instance is disposable

## Where this plugs in

- Control plane isolation: `docs/115-compartmentalized-control-planes.md`
- Storage layout: `docs/27-vm-storage-zfs.md`
- Workload rollout/rollback: `docs/35-workload-rollout-rollback.md`

Last updated: 2026-02-23
