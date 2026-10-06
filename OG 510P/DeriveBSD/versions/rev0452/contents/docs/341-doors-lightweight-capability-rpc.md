# Solaris/illumos Doors: lightweight RPC as file descriptors (capability IPC)

Solaris/illumos **Doors** are a fascinating (and under-copied) IPC primitive:
- a server creates a *door* and receives a **file descriptor**
- the FD can be passed to clients (or attached into the filesystem)
- clients invoke the server via `door_call()` using that FD

The important design lesson is not “implement Doors on FreeBSD tomorrow”.
The lesson is that a **capability-carrying handle (an FD) can *be* the RPC endpoint**,
which makes local IPC naturally compatible with least authority.

## Why this is relevant to DeriveBSD

DeriveBSD wants:
- a coherent “crossing primitive” (`docs/183-object-capability-rpc.md`)
- explicit grants and receipts (`docs/182-capability-leases-and-revocation.md`)
- debuggable control planes (avoid bespoke daemons speaking custom admin protocols)

Doors point to an elegant local-first pattern:

1) **Authority = the handle**
   - if you don’t have the FD, you cannot call

2) **Handles are passable**
   - capability handoff is a primitive (sendmsg/SCM_RIGHTS family)

3) **Endpoints can be named *optionally***
   - attach into FS for discoverability without making the FS path the authority

## DeriveBSD mapping: “door-shaped” interfaces (even without Doors)

Even if we don’t implement kernel Doors, we can adopt “door-shaped” interfaces:

- expose broker/control endpoints as **revocable handles** (FDs)
- make portals return FDs (proxies), not ambient paths
- keep the call surface small and typed (contract digests; see `docs/339-singularity-manifests-and-contract-channels.md`)

Implementation options:
- Unix-domain sockets with `sendmsg()`-passed FDs + a tiny RPC framing
- Cap’n Proto RPC over Unix sockets (already capability-friendly)
- vsock transports for microVM crossings

The design goal is the same: *capability-first IPC*.

## A “bake-in now” ecosystem feature

**Standardize an FD-first broker API**

Make it a rule:
- every privileged broker offers:
  - `open()` → returns a handle (FD)
  - `ioctl`/RPC on the handle → performs a policy-checked operation
  - receipts are emitted for every operation

This aligns with:
- portals/powerbox (`docs/179-portals-and-powerbox.md`)
- capability activation and escrow (`docs/196-capability-activation-and-escrow.md`)

## References

- Oracle Solaris 11.4 “Doors Overview”: https://docs.oracle.com/en/operating-systems/solaris/oracle-solaris/11.4/prog-interfaces/doors-overview.html
- illumos man page `door_call(3C)` (SmartOS mirror): https://smartos.org/man/3C/door_call
- (Interesting prior art) FreeBSD Doors implementation work: https://github.com/bnovkov/freebsd-doors

Last updated: 2026-02-27
