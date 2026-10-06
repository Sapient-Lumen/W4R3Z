# ADR-0075: Stratum stack and runtime composition boundary

Date: 2026-03-07
Status: Accepted

## Context

DeriveBSD already had the right ingredients for bounded compatibility:
`docs/105-compat-view-foreign-binaries.md`, `docs/108-ports-pkg-adapter-lane.md`,
`docs/264-mount-namespaces-and-union-views.md`, `docs/295-strata-and-multi-origin-userlands.md`,
and even a placeholder `strata` field in `spec/derive.unit.schema.json`.

What remained unresolved was the **authoritative runtime-composition contract**.
The archive could say “use strata” or “compose a mount view”, but not yet answer the questions that matter under pressure:

- what is the typed artifact for one userland tree?
- what is the typed artifact for a multi-origin stack?
- where is ABI ownership declared?
- how do we stop silent host-library fallback?
- and which digests must runtime evidence carry so “where did this executable / library come from?” is always answerable?

Without a crisp boundary, DeriveBSD risks re-inventing the standard compatibility failure mode:
ad-hoc chroots, hand-mounted trees, silent precedence rules, and adapter outputs that quietly become the real runtime.

## Decision

DeriveBSD will treat multi-origin runtime composition as a **small typed contract**, not a convention.

The accepted v0 boundary is:

1. `stratum.manifest` is the authoritative description of one digest-bound userland tree.
   It records the tree digest, source class, ABI family, loader path, default library paths,
   and the bounded execution domains in which the tree may run.
2. `stratum.stack` is the only supported authored object for composing multiple userland trees.
   It is an ordered list of strata plus strict resolution rules.
3. Every `stratum.stack` has exactly **one ABI anchor**.
   Loader / libc resolution comes from that anchor; there is no silent host fallback.
4. `mount.view` is the compiled runtime view derived from `stratum.stack` plus explicit writable mounts.
   Writable state remains separate (datasets/tmpfs/secrets); strata stay read-only.
5. Foreign or ABI-incompatible strata are not mixed into native host/jail stacks by accident.
   They must stay in an explicitly bounded lane such as `compat_view` or `microvm`.
6. Compiled launch artifacts must carry the composition join points.
   At minimum, `runtime.manifest` and launch/evidence receipts must be able to bind
   `stratum_stack_digest` and `mount_view_digest`.

## Consequences

### Positive

- The archive now has a compact answer to “what is the official runtime-composition object?”
- Compatibility breadth stays possible without making ad-hoc chroots the real product.
- ABI ownership becomes reviewable instead of folklore.
- Evidence can answer “which stack did this process run with?” using stable digests.
- `mount.view` becomes a concrete derived artifact instead of a recurring hand-wave.

### Negative / trade-offs

- Adapter-produced userlands now need a little more normalization work.
- Some historically convenient tricks (“just mount this tree into the jail”) are explicitly outside the supported lane.
- The archive now has one more join surface to keep wired (`stratum.manifest` → `stratum.stack` → `mount.view` → runtime manifest/receipts).

## Non-goals

This ADR does **not** decide:

- the final frontend syntax for authoring component descriptors,
- the full ABI taxonomy for every future foreign ecosystem,
- whether `compat_view` is implemented with libmap, loader indirection, or another adapter detail,
- or the exact runtime receipt kinds that will record composition joins.

Those remain follow-on implementation work.

## Why this shape

The coherence win is deliberately narrow:

- one manifest per userland tree,
- one stack per explicit composition,
- one compiled mount view for runtime realization,
- one ABI anchor,
- no host fallback,
- and mandatory digest joins in runtime evidence.

That is enough to keep DeriveBSD viable across A–D without forcing a fork,
while refusing the usual slide into invisible compatibility folklore.
