# ADR 0355: Report tree-v2 projection rebuild counters

- Status: accepted and implemented
- Date: 2026-09-09

## Context

ADR 0354 made local CAS import work visible, but a tree-v2 reconcile can still spend significant
time rebuilding the visible projection and conflict material. Before this change, `sync-publish`
reported only whether the workspace exchanged and how much unselected sparse data was preserved.
That was not enough to separate a cheap metadata/frontier update from a rebuild that copied many
selected files or conflict alternatives.

## Decision

Accumulate `TreeV2ProjectionResult` into `TreeV2ReconcileResult` and append these content-free fields
to tree-v2 `sync-publish` output:

- `projection-dirs=N`;
- `projection-files=N`;
- `projection-bytes=N`;
- `projection-conflict-files=N`; and
- `projection-conflict-tombstones=N`.

The counters are zero when no visible projection materialization occurs. When recovery or a normal
reconcile performs more than one projection update in one cycle, counters add together with overflow
checks. They describe only aggregate shape; paths, object identities, writers, and contents remain
private.

## Consequences

The ordinary sync surface now exposes the complete local work shape needed for the next scale gates:

- source walk and digest reuse;
- CAS inspection/install/reuse;
- selected projection copy volume;
- conflict material copy volume; and
- sparse unselected preservation volume.

This is still observability only. It does not make projection incremental, does not relax
post-exchange validation, and does not authorize deleting a changed old projection.

## Evidence

The owned unit/integration registry now verifies that an initial one-file tree-v2 reconciliation
reports one projected file and 14 projected bytes, while unchanged stable reconciliations report zero
projection materialization.

Accepted local check:

```text
nix develop -c bash -lc 'cmake --build build -j2 --target iotox_tests && ctest --test-dir build -R "^iotox\\.unit-and-integration$" --output-on-failure'
```
