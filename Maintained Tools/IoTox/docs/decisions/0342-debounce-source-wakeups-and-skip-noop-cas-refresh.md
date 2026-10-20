# ADR 0342: Debounce source wakeups and skip no-op refresh work

Status: accepted. Implemented 2026-09-09.

## Context

ADR 0341 added native Linux source-tree wakeups for local `publish`, `writable`, and
`bidirectional` automation. That closed the biggest everyday latency gap between a local file edit
and the next eligible publish/reconcile cycle, but it left two operational problems:

- write bursts can produce many `inotify` events for one logical edit;
- a source change observed while a local publish is already busy must survive that publish's
  completion rather than being erased by ordinary success scheduling.

The same frontier also exposed two smaller local waste paths. A stable tree-v2 workspace with an
unchanged source scan repeated the full source-object CAS import/revalidation path on every no-op
wake, then called the marker-only projection update path, which performed another complete worktree
scan before returning. That behavior was safe, but it made source-watch overtrigger more expensive
than necessary.

The tempting larger optimization is a durable or long-lived metadata scan cache. That is not yet
safe. A signed tree-v2 manifest describes file content, path, mode, deletion, and branch causality;
it does not by itself prove that the current source file's inode, mtime, size, and descriptor
identity are unchanged across a future scan. A real incremental scanner needs its own volatile
identity contract before it can skip source hashing or projection work.

## Decision

Keep automation records, sync peer frames, branch records, manifests, authority, and conflict
semantics unchanged. Add only two runtime optimizations:

1. `SyncAutomationScheduler::trigger_source_change` now accepts a debounce interval. The Agent uses
   a default 250 ms debounce for native source-watch events. The direct scheduler API defaults to
   zero milliseconds so existing tests and explicit callers keep immediate behavior unless they opt
   in.
2. Source-change wakeups use one pending local-publish clock for every local-source mode:
   `publish`, `writable`, and `bidirectional`. For bidirectional policies this remains separate from
   the existing per-peer pull clocks.
3. Debounce coalescing is non-sliding. A burst keeps the earliest pending due time instead of
   repeatedly delaying publication.
4. A source change observed while a local publish is busy remains pending after that publish
   completes. Success schedules the ordinary future interval but never discards a newer pending
   source due time; failure schedules the existing bounded retry.
5. A tree-v2 reconcile against an existing stable workspace skips `store_tree_v2_scan_objects` when
   the source scan is unchanged. Startup, repair, pull finalization, conflict materialization, and
   any effect that actually consumes an object still verify the object it consumes.
6. That same no-op reconcile also skips the marker-only `update_tree_v2_worktree` call when the
   existing projection marker has already authenticated the current projection policy, the workspace
   was not newly initialized, no source change was observed, and the signed frontier is unchanged.
   First projection, projection-policy transition, remote frontier change, local edit, and recovery
   paths still go through the full update/exchange machinery.

## Consequences

Ordinary editor-save bursts should produce one near-term local publish rather than a cluster of
redundant publish attempts. A local change that lands during a busy publication is not lost behind
the next periodic interval. This is a latency and churn improvement only; correctness still comes
from signed branch state, immutable CAS objects, transactions, and the periodic fallback.

No-op source-watch reconciles no longer repair or refresh missing local CAS objects by accident, and
they avoid the second marker-only worktree scan when the current projection marker was already
authenticated. That is deliberate. Integrity repair belongs to explicit repair/health paths or to
the fail-closed effect that later tries to consume a missing object. Treating every no-op wake as an
implicit repair would hide storage faults and reintroduce unnecessary complete-store work.

This ADR does not implement a true incremental source scanner, a source metadata cache, incremental
projection, file-range transfer, object bundling, or a new large-directory throughput claim. ADR
0344 later adds a volatile in-process digest cache while keeping durable source-metadata trust
absent.

## Evidence

The owned unit/integration registry now covers both new contracts:

- source-change debounce, non-sliding burst coalescing, and preservation of a source change observed
  while publication is busy;
- stable unchanged tree-v2 reconcile skipping refresh work, including a regression where the old CAS
  object is deliberately removed and the no-op reconcile does not recreate it.

Accepted local check:

```text
nix develop -c bash -lc 'cmake --build build -j2 --target iotox_tests && ctest --test-dir build -R "^iotox\\.unit-and-integration$" --output-on-failure'
```
