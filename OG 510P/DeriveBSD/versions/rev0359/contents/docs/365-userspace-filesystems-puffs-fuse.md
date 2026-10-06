# Userspace filesystem servers (puffs/FUSE) as capability-governed components

Filesystems are another “driver-shaped” risk:
- huge state surface
- complex parsing
- historically in-kernel

DeriveBSD should treat “filesystem implementation” as *just another component* whenever possible.

## Prior art worth stealing

- NetBSD puffs: a **pass-to-userspace** VFS framework; kernel attaches via `/dev/puffs`.  
  https://www.netbsd.org/docs/puffs/  
  https://man.netbsd.org/puffs.4
- ReFUSE (NetBSD): compatibility layer over puffs to run FUSE-style servers.  
  https://www.netbsd.org/docs/puffs/refuse.pdf

## The DeriveBSD framing

A userspace filesystem server is a component with explicit capabilities:

- backing store capability (block device, object store, remote channel)
- cache budget capability (memory/disk budget)
- egress capability (if remote)
- observability capability (budgeted)
- recovery/snapshot capability (if allowed)

The kernel side is a small adapter:
- marshals VFS operations into a message protocol
- enforces size limits, timeouts, and backpressure
- supports restart/reconnect semantics

## Why bake this in

- Crash containment: fs bug ≠ kernel panic.
- Supervision + receipts: restarts are evidence.
- “Filesystem mounts” become declarative runtime artifacts:
  - manifest says what backs it and what it may do
  - caproute makes authority explicit

Tie into:
- `docs/239-service-lifecycle-restarters-and-repo.md`
- `docs/349-supervision-trees-and-restart-strategies.md`
- `docs/140-capability-routing-manifests.md`

## Compatibility posture

This is not “support every random FUSE thing forever”.
Instead:

- support a **small, reviewable core** of operations
- define contract digests for the VFS<->server protocol
- gate new operations via the UAPI registry  
  See: `docs/362-uapi-surface-registry-and-compat-gates.md`

## Open questions

- Do we want a “filesystem portal” to mediate mounts for desktop apps?
- What’s the best default timeout/backpressure policy for remote-backed filesystems?
- Can we provide a test harness that replays recorded VFS traces against an FS server (hermetic)?

## Related docs

- `docs/172-device-backend-isolation-bhyve.md`
- `docs/355-rump-kernels-and-userspace-driver-testing.md`
