# sandboxfs-accelerated store views (optional)

Store view minimization (“each build step only sees its declared input closure”) is security-correct but can be operationally expensive if implemented as “mount N inputs” for large closures.

Bazel ran into the same problem and introduced **sandboxfs**: a FUSE filesystem that exposes an arbitrary *virtual* view of the host filesystem under a mount point, used to create per-action sandboxes quickly.

FreeBSD has a `sandboxfs` port, making this a plausible optimization on DeriveBSD hosts.

## Goal

Reduce storeview creation overhead **without** widening visibility.

- keep `storeview.manifest` as the source of truth
- keep the view digest bound into the Plan digest
- change only the *mechanism* that projects the view into the sandbox

## Two mechanisms

### A) mount composition (baseline)

- create a jail/microVM sandbox root
- `nullfs` mount each allowed store path into the sandbox

Pros: kernel fast-path I/O. Cons: mount storms for large closures.

### B) sandboxfs virtual view (optimization)

- store remains mounted read-only at a stable location
- start sandboxfs with a mapping derived from `storeview.manifest`
- mount sandboxfs once into the sandbox root

Pros: avoids thousands of mounts/symlinks; view construction becomes “write mapping + mount once.” Bazel’s docs explicitly call out sandboxfs as avoiding expensive per-action setup.

Cons: FUSE introduces runtime overhead on filesystem operations; sandboxfs becomes part of the *sandboxing TCB*.

## Threat model notes

- The sandboxfs process must run outside the hostile build sandbox.
- The mapping file is derived deterministically from the Plan’s `storeview.manifest`.
- The sandboxfs mount must be read-only for store paths; writable outputs must be separate (tmpfs/ZFS clone).

## Policy + planner integration

Add a policy knob:

- `sandbox.storeview.strategy = "nullfs" | "sandboxfs"`

Planner heuristics can switch automatically when `storeview.entries` exceeds a threshold (but the chosen strategy must be reflected in the Plan hash).

## Relation to existing docs

- correctness + contract: `docs/152-store-view-minimization.md`
- performance + instrumentation: `docs/157-storeview-performance.md`

## References

- Bazel sandboxing (mentions sandboxfs motivation): https://bazel.build/docs/sandboxing
- sandboxfs repo: https://github.com/bazelbuild/sandboxfs
- FreeBSD port (FreshPorts): https://www.freshports.org/filesystems/sandboxfs/

Last updated: 2026-02-23
