# Hypervisor device backend isolation (bhyve hardening lane)

MicroVM-first reduces blast radius, but **guest→host escapes** frequently target **emulated devices** (virtio/net/disk/frontends).

DeriveBSD already assumes:

* treat builders hostile
* run `bhyve` in a jail where possible

This doc adds a more ambitious *future hardening lane*: isolate device backends **out of the main VMM process**.

See also: `docs/363-driver-safety-tiering-rust-and-user-mode.md` (driver tiers) and `docs/365-userspace-filesystems-puffs-fuse.md` (pull driver-shaped surfaces out of kernel space when possible).


## The lesson to steal

OpenBSD’s `vmd(8)` work includes experiments on isolating emulated devices using privilege separation and process compartmentalization (e.g. fork+exec, chroot, pledge/unveil-style tightening).

Even if DeriveBSD does not copy OpenBSD’s design directly, the idea maps cleanly:

> **The VMM process should not be the “device emulator + everything else”**.

## DeriveBSD-shaped architecture sketch

For each microVM:

* **VMM worker**: owns `/dev/vmm/*`, vCPU run loops, minimal control plane.
* **Device workers** (one per device class or per device):
  * virtio-blk backend: holds only the disk file descriptor(s)
  * virtio-net backend: holds only the tap/vionet endpoint
  * console/log backend: write-only to a log sink

Workers communicate over **pre-opened file descriptors** and small RPC surfaces (vsock/Unix domain sockets). No ambient filesystem access.

## Policy hooks

Device isolation must be **policy-selectable**:

* `hypervisor.device_isolation = off|per-class|per-device`
* `hypervisor.device_backend = inproc|worker`

Bind these decisions into `policy_decision_digest` so the artifact identity captures the security regime.

## Evidence objects

Emit:

* `vm.device-map` — device list + backend realization + fd provenance
* `vm.backend-profiles` — jail profiles / capsicum profiles applied

These become part of the “why/what/where-from” explanation chain.

## v0 scope recommendation

* v0: run `bhyve` inside a jail (already in scope) and treat device isolation as **non-goal**.
* v1+: prototype a single isolated backend first (e.g., network backend) to validate feasibility.

## References

* OpenBSD papers/slides on hardening emulated devices in `vmd(8)`.
* `bhyve(8)` manual page (FreeBSD).
