# ADR 0345: Group tree-v2 path work before scan, merge, and projection decisions

Status: accepted. Implemented 2026-09-09.

## Context

ADR 0344 removed repeated content hashing for stable source files, but large tree-v2 reconciles still
paid avoidable CPU and allocation overhead after the filesystem walk. Several hot paths repeatedly
rebuilt candidate vectors for the same manifest path:

- local source scans searched the observed tree and baseline manifest for each path;
- merge summarization built a path set, then extracted each path's candidates again;
- multi-writer merge repeatedly extracted the same per-snapshot path candidates while checking
  dominance; and
- projection materialization repeated the same path extraction before selecting the visible value.

That work is not a protocol rule. It is an implementation detail on already validated canonical
manifests, and it scales poorly as ordinary directories approach the current file-count gates.

## Decision

Group path work once per phase instead of repeatedly searching and copying the same manifest slices.

The implementation keeps all existing semantics:

- `scan_tree_v2_worktree()` still walks the complete selected source tree, validates ownership and
  path safety, hashes or reuses file digests under ADR 0344, and creates the same local events and
  tombstones;
- scan reconciliation now indexes observed entries and baseline entries by path before deciding
  whether each path retains prior causality or receives a new local event;
- `summarize_tree_v2_manifest()` now walks contiguous canonical path groups directly;
- `merge_tree_v2_snapshots()` builds one per-snapshot path index after each snapshot verifies, then
  reuses those groups for candidate collection and dominance checks; and
- `materialize_tree_v2_merge()` walks contiguous manifest path groups directly when choosing the
  ordinary projection value.

No wire frame, signed branch, manifest format, object-store identity, workspace transaction, source
watch, or authority rule changes.

## Consequences

This reduces local CPU/allocation amplification during large clean reconciles and conflict-heavy
merge/projection work. It is a prerequisite-quality optimization for larger ordinary directories,
but it does not implement true path-level incremental scanning or projection:

- every reconcile still performs a complete selected filesystem walk;
- a changed source may still force complete manifest/projection reasoning;
- projection exchange still constructs a complete replacement tree when the signed merge changes;
- dishonest storage and missed filesystem events remain outside the supported claim; and
- Sandwurm near-ceiling repetition is still required before changing product guidance.

## Evidence

The owned unit/integration registry now includes a grouped-merge regression with 256 stable shared
paths plus one real concurrent conflict. The test checks that grouped candidate handling preserves
the exact merged manifest, path count, live-file count, and conflict candidates.

Accepted local check:

```text
nix develop -c bash -lc 'cmake --build build -j2 --target iotox_tests && ctest --test-dir build -R "^iotox\\.unit-and-integration$" --output-on-failure'
```
