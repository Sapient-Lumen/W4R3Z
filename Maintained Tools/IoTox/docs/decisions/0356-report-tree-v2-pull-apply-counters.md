# ADR 0356: Report tree-v2 pull apply counters

- Status: accepted and implemented
- Date: 2026-09-09

## Context

Tree-v2 pull status already reported transfer-side work: requested objects, committed objects,
fetched bytes, lane batches, source behavior, late-offer cleanup, and CAS inventory scans used by
the object receiver. After ADRs 0354--0355, local reconciliation can also report source, CAS,
projection, conflict, and sparse-preservation work. Pull completion still dropped that final apply
shape and retained only the conflict count.

That hid an important distinction during scale tests: a pull may finish network/object transfer
quickly but then spend time accepting branches, reconciling the writable workspace, or rebuilding the
projection. Operators need to see that boundary without enabling path/content logging.

## Decision

Store the final `TreeV2ReconcileResult` inside each retained `TreeV2PullSnapshot` and render it from
`sync-status` with `reconcile-` prefixes:

- `reconcile-local-events`;
- `reconcile-branch-advances`;
- `reconcile-source-inspected`, `reconcile-source-hashed`, `reconcile-source-reused`;
- `reconcile-cas-inspected`, `reconcile-cas-inspected-bytes`, `reconcile-cas-installed`,
  `reconcile-cas-installed-bytes`, `reconcile-cas-reused`;
- `reconcile-projection-dirs`, `reconcile-projection-files`, `reconcile-projection-bytes`;
- `reconcile-projection-conflict-files`,
  `reconcile-projection-conflict-tombstones`; and
- `reconcile-projection-preserved-entries`,
  `reconcile-projection-preserved-dirs`, `reconcile-projection-preserved-files`,
  `reconcile-projection-preserved-bytes`.

The existing transfer-side counters remain unchanged. The existing top-level `conflicts` field stays
as a compatibility summary for the final reconcile conflict count.

## Consequences

`sync-status` can now distinguish transfer bottlenecks from local apply bottlenecks in completed and
retained tree-v2 pulls. This makes future near-ceiling evidence more useful without changing any peer
wire frame, signed record, authority rule, durable state format, or object-transfer scheduler.

The fields are content-free aggregates. They do not expose paths, filenames, object digests, branch
records, writers, or file contents.

## Evidence

The owned unit/integration registry now verifies that a four-file tree-v2 pull records the final
local projection apply counters in its retained `TreeV2PullSnapshot`: four projected files, 22 bytes,
and zero conflict files/tombstones.

Accepted local check:

```text
nix develop -c bash -lc 'cmake --build build -j2 --target iotox_tests && ctest --test-dir build -R "^iotox\\.unit-and-integration$" --output-on-failure'
```
