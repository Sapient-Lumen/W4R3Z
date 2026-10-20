# ADR 0348: Group tree-v2 time-machine diff paths

Status: accepted. Implemented 2026-09-09.

## Context

The synchronization time machine is read-only until an operator explicitly uses a checked
forward-restore plan. Its `sync-diff` path compares retained signed tree-v2 records and reports
candidate-set and projected-content changes.

After ADRs 0345--0347 removed repeated path extraction from reconciliation, merge, projection, and
branch acceptance, `sync-diff` still built a complete path set and then repeatedly searched both
manifests for each path.

## Decision

Build per-path indexes for the `from` and `to` manifests inside `diff_manifests()`, then compare
indexed candidate groups.

The diff semantics are unchanged:

- exact candidate sets, including origin provenance, decide whether a path entry changed;
- added/removed/modified counters retain their existing meaning;
- projected-content change remains a separate selected-value comparison; and
- summaries still validate both manifests before diffing.

No restore-plan ID, restore mutation, branch, manifest, object-store, or protocol behavior changes.

## Consequences

Large retained-history comparisons do less repeated allocation and binary-search work. This improves
operator inspection and restore planning scale without making history a backup and without changing
the forward-only restore safety model.

## Evidence

The owned unit/integration registry now includes a grouped `sync-diff` regression with 128 stable
paths and three visible changes: one added file, one modified file, and one file-to-tombstone
transition. The diff must report the same changed path and projected-content counters.

Accepted local check:

```text
nix develop -c bash -lc 'cmake --build build -j2 --target iotox_tests && ctest --test-dir build -R "^iotox\\.unit-and-integration$" --output-on-failure'
```
