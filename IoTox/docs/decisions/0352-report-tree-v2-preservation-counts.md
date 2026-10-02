# ADR 0352: Report tree-v2 preservation counts

- Status: accepted and implemented
- Date: 2026-09-09

## Context

ADR 0351 made projection preservation observable inside `TreeV2WorktreeUpdateResult`, but the public
reconcile result and `sync-publish` response still only reported source-walk digest counters. That
left operators unable to distinguish three materially different cases:

- complete projection with no unselected preservation work;
- sparse projection preserving excluded or unrelated local data;
- projection bottlenecks caused by selected-tree rebuild rather than local preservation.

The missing signal mattered because sparse sync is now a first-class operating mode, and the next
scale decisions need evidence about which local phase actually costs time.

## Decision

Expose preservation work as additive, content-free counters:

- `TreeV2ReconcileResult::projection_preserved_unselected_entries`;
- `TreeV2ReconcileResult::projection_preserved_unselected_directories`;
- `TreeV2ReconcileResult::projection_preserved_unselected_files`;
- `TreeV2ReconcileResult::projection_preserved_unselected_bytes`.

`reconcile_tree_v2_workspace()` accumulates those counters across any recovery or projection-update
step performed during the reconciliation cycle. `sync-publish` appends the same signal as:

```text
projection-preserved-entries=N
projection-preserved-dirs=N
projection-preserved-files=N
projection-preserved-bytes=N
```

The counters identify amount and shape of preserved local data, never paths, names, contents,
digests, writers, or conflict bodies.

## Consequences

Complete tree-v2 projection should report zeros, proving the ADR 0351 fast path stayed active.
Sparse projection reports the local excluded/unrelated entries copied across the atomic exchange, so
operators can tell when the remaining cost is preservation instead of object transfer, source
hashing, or branch merge.

This does not make sparse preservation incremental. It only makes the remaining work visible enough
to measure and prioritize.
