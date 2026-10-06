# Verified lazy rootfs + on-demand mounts (composefs / eStargz / Nydus lesson)

Cold-start for microVMs and disposable instances is often dominated by **fetching bytes that never get read**.
Container ecosystems responded with “lazy pulling” formats and verified, content-addressed filesystem layers.

DeriveBSD already has the right conceptual hooks (CAS-first store, signed manifests, explicit transports).
The question is whether we should bake in an **optional** “lazy rootfs mount” lane now so the ecosystem doesn't
invent bespoke downloaders later. The authority / privacy / fallback boundary is now fixed in
`docs/527-verified-lazy-tree-mount-materialization-and-evidence-boundary.md`.

## Prior art (useful, even if we only steal the shape)

- **eStargz / stargz snapshotter**: gzip-compatible image layout that supports on-demand fetching of file ranges.
  Used by containerd snapshotter to start containers before the full image is local.

- **Nydus**: a content-addressable filesystem format (RAFS) designed for on-demand chunk fetch, often paired with
  fscache and/or P2P distribution.

- **composefs**: a verified, mountable filesystem tree that references content-addressed backing data.
  It aims to improve sharing and integrity of image trees without unpacking.

Key shared lesson: treat “filesystem tree bytes” as **addressed objects** and mount a view that can fault in data
lazily *while still verifying everything*.

## DeriveBSD direction

### Keep defaults boring

- Default host/workload deployment remains: **fully materialize** the root tree into a ZFS dataset/BE (or zvol), then
  boot/launch.
- Lazy mounts are **opt-in transports** for specific environments (edge nodes, scale-out clusters, disposable VMs).

### Add an explicit “lazy mount adapter” lane

Introduce an optional adapter that turns a signed tree reference into a mountable view:

Inputs (already consistent with the archive’s posture):
- a **tree identity** (digest) + signed descriptor that binds path→content digests
- allowed transport policy (`spec/transport.policy.schema.json`)
- cache policy (where to store fetched chunks; retention)

Derived artifacts (small, now tightened):
- `tree.mount.plan` — which backend + endpoints + cache location + integrity parameters, plus explicit projection mode (`materialize` / `prefetch` / `lazy`), fallback policy, fetch-evidence scope, and backend constraints
- `tree.mount.receipt` — what was mounted, which posture was actually realized, whether fallback happened, and bounded fetch evidence by default

Schema: `spec/tree.mount.plan.schema.json`, `spec/tree.mount.receipt.schema.json`
Examples: `spec/examples/tree.mount.plan.json`, `spec/examples/tree.mount.receipt.json`

The adapter is allowed to fail closed and fall back to full materialization if policy disallows the remote behavior.

### Where it plugs in

- **MicroVM bundles**: allow a bundle to reference `rootfs.tree_digest` instead of embedding all bytes.
- **Strata**: strata become “tree digests” that can be satisfied by multiple transports (local dataset, HTTP CAS, P2P,
  lazy mount).
- **Component descriptors (`derive.unit`)**: a unit can reference the rootfs tree it expects, and a plan can select
  a transport.

## Security and evidence invariants

### 1) Verify before use

- Every fetched object must be verified against the signed tree manifest (digest binding) before it can satisfy a page
  fault.
- Peers/caches are always treated as **untrusted** sources of bytes.

### 2) Avoid turning “fetch traces” into ambient surveillance

Lazy fetch patterns can reveal which files were touched (which binaries executed, which configs loaded).
So:
- ordinary receipts default to `digest-only` fetch evidence
- stronger path-level fetch traces are a separate explicit debugging/forensics lane
- allow a policy posture that forces `prefetch` or `materialize` for sensitive workloads

### 3) Make fallbacks explicit

If a node can’t do lazy mount (no kernel support, offline), it may fall back to materializing the full tree.
That fallback must be:
- declared in the plan (`fail_closed`, `materialize`, or `prefetch`)
- recorded in receipts as the realized posture
- visible in diff/review outputs (the transport path is part of “blast radius”)

## Why bake this in early?

If we don’t, people will create:
- hidden downloaders in init scripts
- ad-hoc per-team caching daemons
- “just trust the registry” shortcuts

Greenfield advantage: define the lane now so these optimizations remain **policy-bound, explainable, and optional**.

## See also

- Accepted authority/privacy/fallback boundary: `docs/527-verified-lazy-tree-mount-materialization-and-evidence-boundary.md`
- Distribution beyond binary caches (casync/CernVM-FS): `docs/119-casync-cvmfs-distribution.md`
- Bandwidth-efficient deltas: `docs/139-bandwidth-efficient-deltas.md`
- Strata (multi-origin userlands): `docs/295-strata-and-multi-origin-userlands.md`
- Component descriptors → compiled manifests: `docs/297-component-descriptors-and-compiled-runtime-manifests.md`
- Transport policy: `spec/transport.policy.schema.json`

Last updated: 2026-03-16r256
