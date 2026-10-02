# ADR 0142: Share the v1 object and tree-entry ceiling explicitly

Date: 2026-08-24

Status: accepted

## Context

The `iotox-sync-namespace-v1` field `maximum-objects` bounds two different finite populations. It is
the whole immutable-store object ceiling used during publication and subscriber staged commit, and it
also caps treepack entry parsing and canonical sort memory. The shared bound is conservative and
already frozen in the v1 namespace semantics, but it means a tree namespace cannot set the store
ceiling below the largest tree it promises to accept.

The first genuine object-count experiment made this coupling visible. A two-object ceiling was enough
for one artifact and one manifest, but it was invalid for a six-entry treepack. It also violated the
separate namespace ordering rule while `maximum-retained-revisions` remained four. Neither failure
was transport pressure or an object-store refusal.

## Decision

Keep the shared v1 meaning explicit and test object-store saturation without making the tree itself
inadmissible.

- The canonical fixture has six treepack entries, so the subscriber uses `maximum-objects=6` and
  retains the existing `maximum-retained-revisions=4` ordering.
- Before the first pull, the subscriber installs four private, correctly digest-named one-byte
  immutable objects. The generation-1 artifact and manifest then grow the canonical inventory from
  four to exactly six objects and still activate the six-entry tree.
- The byte ceiling remains 33,554,432. The saturated inventory consumes only 4,981,173 bytes, and the
  complete generation-2 artifact plus manifest would still fit by bytes. A generation-2 staged
  commit can therefore be refused only by object count.
- Candidate refusal must leave all six predecessor objects, accepted HEAD, activation record,
  `current` link, visible payload, and empty staging unchanged. IoTox does not evict an unrelated
  immutable object to make room.
- A future independent tree-entry field requires an explicit namespace-policy revision or a
  backwards-compatible extension with separately frozen validation. It is not silently inferred by
  changing v1.

## Consequences

The direct-UDP and forced-TCP `sync-tree-object-quota` cells now prove the production object-count
boundary while leaving roughly 28 MiB of byte headroom. Operators must configure
`maximum-objects` at least as high as the maximum admitted tree entry population as well as allowing
for retained immutable artifacts and manifests.

This does not prove automatic eviction, destructive collection, quota recovery, a separate future
tree-entry ceiling, peak resident-memory behavior, read-only storage, multi-source convergence, or
arbitrary target-fleet scheduling.
