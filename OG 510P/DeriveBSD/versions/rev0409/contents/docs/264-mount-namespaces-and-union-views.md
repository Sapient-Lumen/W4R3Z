# Mount namespaces and union views (Plan 9 + unionfs lessons)

A recurring pain in “immutable base” systems is needing *temporary* or *local* filesystem views:
- compat shims for foreign binaries
- per-workload overlays
- incident-only debug tooling
- developer sandboxes that should not pollute the host

Plan 9’s answer is conceptually simple:
- **the filesystem namespace is per-process**
- processes can share a namespace as a group
- `bind` can build **union directories** by stacking trees

## DeriveBSD target

Accepted runtime-composition contract: `docs/485-stratum-stack-and-runtime-composition-boundary.md`.

Make “filesystem view” a first-class derived object:
- produced by activation planning
- consumed by jails/microVM launchers
- recorded in evidence (so it is explainable and reproducible)

This unifies existing DeriveBSD ideas:
- compat views (`docs/105-compat-view-foreign-binaries.md`)
- system extensions (`docs/122-system-extensions.md`)
- per-service jail mount maps (`docs/86-host-activation-rcd-and-service-jails.md`)
- store view minimization (`docs/152-store-view-minimization.md`)

## Design sketch

### 1) A canonical `mount.view` object

A hashable manifest describing:
- base roots (store paths / datasets)
- extension roots (read-only bundles)
- writable layers (explicit dataset or tmpfs)
- precedence rules (which tree wins at a mountpoint)
- any required “pinning” (e.g., a specific rtld/lib set for a compat stack)
- the source `stratum.stack` digest when the view is built from explicit strata

The accepted boundary is deliberately narrow: `mount.view` is compiled from `stratum.stack` plus explicit writable mounts, every stack has exactly one **ABI anchor**, and host-library fallback is forbidden.

### 2) Namespace groups (make “the view” a joinable handle)

Plan 9’s namespaces aren’t just per-process; they can be shared among related processes.
DeriveBSD can model this explicitly:
- a running service points at a specific `mount.view` digest
- children inherit that view
- debugging shells can *attach* an additional extension view (with a timeboxed lease) rather than mutating the host

Treat the view as part of the service’s identity: if the view changes, that should show up in diffs and receipts.

### 3) Strict creation rules

- views are created by the activation/launch broker, not by random processes
- writable layers are explicit and quota’d
- view creation is policy-controlled (e.g., forbid writable overlays on `/usr` outside breakglass)

### 4) Enforcement mapping

On FreeBSD, we can implement view composition with a combination of:
- jail mount visibility controls
- ZFS datasets + mount ordering
- (optional) union mounts where appropriate

Union filesystem implementations have tricky corner cases; treat them as an optimisation, not a dependency.

## Why this is a greenfield advantage

Older ecosystems accrete ad-hoc overlays:
- “just mount this here”
- “just bind this directory”

DeriveBSD can instead make view composition:
- typed
- diffable
- traced into receipts

So “my incident shell had these debug tools attached” is not folklore — it’s evidence.

## References

- Plan 9 — the use of namespaces (per-process views; solve problems without exotic mechanisms): https://9p.io/sys/doc/names.html
- Plan 9 `bind(1)` man page (union directories): https://9p.io/magic/man2html/1/bind
- LWN — Union file systems (Plan 9/BSD/Linux implementations): https://lwn.net/Articles/325369/

Last updated: 2026-03-07r214
