# AnonSync rev0950 revision notes

## Mission

AnonSync exists to replace Resilio Sync in one named real workflow with a
practical C++ folder-synchronization product. Direct TCP, Tor, and I2P remain
routes into the same authenticated synchronization semantics. Rev0950 corrects
remote convergence liveness, bounds remote effect work, and makes process
settlement and durable progress reporting match the real folder owners. It does
not add another daemon, route-specific engine, or persisted configuration knob.

## Primary correction: aggregate remote bytes caused permanent zero progress

The post-scan remote planner previously collected all eligible missing remote
files and rejected the pass when their aggregate bytes exceeded the pass limit.
Because the same sorted projection was reconsidered on every invocation, a valid
set of files that fit individually but not together could fail before applying
any file forever.

Rev0950 keeps complete-projection hard checks for remote path count, path bytes,
depth, operation shape, and per-file bytes, then schedules one deterministic
prefix under the aggregate byte frontier. The first non-fitting candidate and
all later eligible candidates are deferred. Successfully committed prefix values
become exact no-ops on the next pass, allowing the suffix to advance.

A regression now proves two files under a one-file aggregate budget converge in
two passes. Another proves that a valid selected prefix is not applied when a
later projection path violates a hard path limit.

## Audit/refactor: an independent remote effect frontier

Zero-byte files and tombstones spend no payload bytes. The old byte-only planner
could reserve and execute work proportional to the full 100,000-path admission
ceiling in one service turn.

A new fixed production scheduling frontier bounds completed remote file and
tombstone apply-owner calls to 4,096 per pass. It composes at or above the local
regular-file segment frontier, because local traversal may apply one remote
successor per delivered path. The post-scan candidate vector reserves only the
remaining effect allowance. A mixed zero-byte/tombstone fixture proves `2 + 2`
progress under a two-effect test frontier.

Reports and CLIs now expose completed remote apply operations, deferred eligible
candidates, and an exact remote stop reason. Installed-service `check-config`
reports the effective 4,096 default. The field remains an internal scheduling
contract rather than a persisted user setting.

## Settlement correction: bounded progress is not settled convergence

The former completion classifier considered explicit conflict/tombstone skips
but not scan or apply continuation. A cycle could materialize one bounded prefix
and still report `complete_changed` with `settled=true`.

Settlement now requires the final folder pass to finish its authenticated local
scan epoch, leave no deferred remote candidates or unadjudicated absence fence,
and reach the end of the remote projection. Earlier-pass remainder is ignored
when the final pass has already completed it during the same cycle.

The real two-process test forces three files through a one-file byte frontier.
The first cycle commits one remote prefix and is unsettled. The second
materializes the remaining files but remains unsettled because the final local
scan has a suffix. The third changes only the durable scan journal, completes the
epoch, and then settles. The duplicate cycle remains a no-op.

## Durable cutpoint correction: scan-only progress is real progress

A bounded authenticated scan segment can commit epoch/cursor/journal state while
catalog and replica content remain unchanged. `sync-once` previously omitted that
state from its before/after cutpoint.

The folder scan owner now exposes a validated progress snapshot containing epoch,
resume path, seen count, seen path bytes, and chain digest. Those fields join the
process cutpoint and JSON, so restart-surviving scan continuation counts as
durable progress. Catalog, scan, and replica observations remain sequential
owner reads, not a claimed cross-database atomic transaction.

## Exact nonclaims

- Every pass still examines the complete visible remote projection for hard
  suffix checks and exact deferred counts.
- There is no persisted remote apply cursor. Fair suffix progress assumes an
  already-applied prefix remains an exact no-op; sustained early-path churn can
  delay later work.
- Local continuation still re-enumerates and classifies its root prefix.
- A wide immediate directory is still fully buffered and sorted.
- Watcher notifications remain acceleration only; rooted scans repair loss.
- Catalog and payload history remain append-only with no coordinated retention,
  restore, reachability, or garbage-collection owner.
- Changed-block transfer, rename/directory semantics, selective sync, recovery
  UX, multi-share ownership, target-scale qualification, and cross-platform
  behavior remain incomplete.

## Research and next refactor

Current Syncthing protocol and product documentation provides useful precedent
for persistent index identity/sequence, incremental index updates, block hashes,
local block reuse, bounded pending work, and watcher plus full-scan repair. Linux
`inotify(7)` documents event loss on overflow and racy rename pairing. Resilio's
current selective-sync and Archive documentation reinforces that placeholders
and retained-version recovery are ordinary replacement-product obligations.

The next structural move should be a crash-consistent exact metadata/subtree and
remote-work index with monotonic sequence, bounded queues, and a rebuild path.
The rooted descriptor scanner should remain the rebuild and rotating-scrub
oracle. A durable payload index, changed-block manifests, retention/restore, and
safe garbage collection should attach to that owner rather than creating more
whole-namespace loops.

Sources consulted 2026-07-30:

- https://docs.syncthing.net/specs/bep-v1.html
- https://docs.syncthing.net/users/syncing.html
- https://docs.syncthing.net/users/tuning.html
- https://man7.org/linux/man-pages/man7/inotify.7.html
- https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync
- https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

## Validation

The frozen rev0950 implementation passed:

- the complete GCC 14.2 Debug target graph;
- every one of 254 registered GCC tests across bounded completed shards;
- 35/35 GCC product tests in 16.04 seconds;
- 260 focused folder-scan-owner checks;
- 94 focused sync-once checks;
- the real direct/Tor/I2P and installed-service process paths;
- the 65/65 payload/folder structural audit;
- a fresh Clang 17 Debug ASan/UBSan product graph, 222/222 build steps; and
- 35/35 Clang product tests in seven completed serial shards, 87.20 cumulative
  real test seconds, with leak detection and no sanitizer diagnostic.

One compound sanitizer launcher did not return buffered output for the final
shard. No result from that attempt is used. The final six-test shard was rerun
independently and completed cleanly.
