# Stratum stack and runtime composition boundary

**Tier:** B (Base)  
**Profiles:** A, B, C, D  
**Pillars:** isolation, supply-chain, operability  
**Patterns:** Adapter→Shadow→Replace, Plan→Apply→Receipt  

DeriveBSD already wanted explicit userland composition, compat views, and digest-bound runtime trees.
The hard decision it was missing was **which typed objects own runtime composition**.

This doc fixes that boundary for v0.

## Accepted boundary

DeriveBSD uses a three-step runtime-composition contract:

1. **`stratum.manifest`** — one digest-bound userland tree with source + ABI facts.
2. **`stratum.stack`** — the authored ordered composition of one or more strata.
3. **`mount.view`** — the compiled runtime namespace / mount graph derived from the stack plus explicit writable mounts.

`runtime.manifest` (and later launch receipts) is the join surface that must carry the digests operators care about:

- `stratum_stack_digest`
- `mount_view_digest`

That is the minimum needed so “where did this process get its loader, libraries, and runtime tree?” is always answerable.

## Narrow rules

### `stratum.manifest` is the unit of userland provenance

A stratum is not “some tree mounted somewhere.”
It is a typed manifest for one digest-bound runtime tree, including:

- tree digest
- source class (`native`, `adapter`, `vendor`, `foreign`)
- ABI family
- loader path + default library paths
- bounded execution domains (`host`, `jail`, `microvm`, `appvm`, `compat_view`)

This keeps adapter outputs, vendor runtimes, and native base trees in one reviewable vocabulary.

### `stratum.stack` is the only supported authored composition object

Multi-origin composition is allowed, but only through `stratum.stack`.
That prevents ad-hoc chroots, mount scripts, and invisible precedence rules from becoming the unofficial standard.

### Exactly one ABI anchor

Each stack has exactly one **ABI anchor** stratum.
That anchor owns loader/libc resolution for the stack.

Implications:

- no silent host-library fallback
- no “whichever `/usr/lib` happened to win” semantics
- no mixed-ABI native host/jail stacks by accident

### `mount.view` is compiled, not improvised

`mount.view` is the runtime artifact consumed by launchers.
It records:

- which read-only strata are mounted where
- which writable datasets/tmpfs/secrets are attached
- deterministic precedence
- the source `stratum_stack_digest`

Writable state is always separate from strata.
A stratum is not a mutable rootfs.

### Foreign or incompatible strata stay bounded

If a userland tree is foreign or ABI-incompatible, it must live in an explicit bounded lane:

- `compat_view`, when policy allows a compatibility adapter
- `microvm`, when isolation or ABI separation demands it

The host/jail lane does not silently absorb foreign userlands.

## Product-shape fit (A–D without forks)

- **A / fleet host:** keep stacks narrow and service-specific; adapter or foreign strata belong in explicit workload lanes, not the trusted host baseline.
- **B / workstation:** keep the host UI/control plane narrow; AppVMs may carry broader stacks, but host runtime pollution is not the escape hatch.
- **C / general OS:** this is the broadest compatibility profile, so adapter-built stacks are allowed, but they still normalize to the same typed artifacts.
- **D / appliance factory / regulatory:** production stacks stay sealed, approved, and reproducible; broader compatibility remains a maintenance/import lane, not the production baseline.

## Why this is the right narrow decision

This accepts exactly enough structure to make compatibility implementable without letting compatibility become ambient authority.

The point is not “support infinite distro mixing.”
The point is:

- make composition explicit,
- bind it to digested artifacts,
- keep ABI ownership reviewable,
- and preserve one coherent runtime story across A–D.

## Related docs

- `adrs/ADR-0075-stratum-stack-and-runtime-composition-boundary.md`
- `docs/295-strata-and-multi-origin-userlands.md`
- `docs/264-mount-namespaces-and-union-views.md`
- `docs/297-component-descriptors-and-compiled-runtime-manifests.md`
- `spec/stratum.manifest.schema.json`
- `spec/stratum.stack.schema.json`
- `spec/mount.view.schema.json`
- `spec/runtime.manifest.schema.json`
- `spec/examples/stratum.manifest.json`
- `spec/examples/stratum.stack.json`
- `spec/examples/mount.view.json`
- `spec/examples/runtime.manifest.json`

Last updated: 2026-03-07r214
