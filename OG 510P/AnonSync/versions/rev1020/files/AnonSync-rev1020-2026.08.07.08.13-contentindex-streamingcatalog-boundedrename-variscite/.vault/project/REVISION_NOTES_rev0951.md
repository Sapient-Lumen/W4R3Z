# AnonSync rev0951 revision notes

## Mission

AnonSync exists to replace Resilio Sync in one named real workflow with a
practical C++ folder-synchronization product. Direct TCP, Tor, and I2P remain
routes into the same authenticated synchronization semantics. Rev0951 repairs
remote scheduling fairness, removes an accidental dependency on local scan-
journal lifetime, and eliminates repeated payload-namespace snapshots inside a
single remote pass. It does not create another daemon or expose internal
scheduling state as a user setting.

## Durable cyclic remote scheduling

Rev0950's bounded stable prefix could still starve a suffix when an early path
received a new successor every pass. Rev0951 moves every remote file/tombstone
effect into one planner and persists the last successfully selected canonical
path in catalog schema v4. Complete hard validation still examines the whole
sole-visible projection before any effect. Selection begins strictly after the
cursor, wraps once, and is bounded independently by operation count and file
bytes.

The cursor advances only after selected apply owners complete. A crash can
replay idempotent effects but cannot advance past an uncommitted effect. Cursor
movement joins process cutpoints and diagnostics. A restart proof applies `a`,
gives `a` another successor, proves `z` is selected next under a one-operation
frontier, then proves wrap returns to `a`.

## Crash-order audit: scan progress must not gate remote replacement

The first implementation required a present predecessor to be hashed by the
current local scan invocation. That protected local edits but could delay a
remote successor for a whole epoch after restart. An incomplete journal survives,
whereas a completed epoch resets and deletes its seen rows, so journal membership
could not close the boundary.

Final rev0951 instead allows the durable catalog predecessor to nominate work
after fresh rooted descriptor metadata reproduces its source-snapshot digest.
That metadata is not byte authority. The selected apply owner still reopens and
fully hashes the file, reloads the catalog predecessor, proves causal
supersession, and only then publishes. A stale or racing local edit fails closed.
The authenticated scan journal remains solely local traversal and absence
proof state.

Tests cover restart during an incomplete epoch, restart after completed-epoch
reset while only the first new-epoch path has been scanned, and refusal to
overwrite a locally edited predecessor.

## Payload inventory refactor and readiness semantics

The old one-file apply API took a complete verified payload-store snapshot for
each selected file. A bounded pass applying many files could repeatedly traverse
the same private payload namespace. The convergence pass now shares one frozen
verified inventory across every remote file readiness check and apply. It
refreshes at most once if local publication inserted payloads earlier in the
pass; the standalone one-file API retains its own snapshot.

Authenticated file evidence may arrive before bounded payload transfer. A digest
missing from the frozen inventory is now deferred scheduling work, not a pass-
aborting exception. A missing prefix does not block ready cyclic suffixes. The
next pass observes payloads that arrived after the snapshot. Every selected
payload is still reopened and exactly re-proved before rooted atomic publication.

New report and JSON fields expose one-pass payload snapshot observations and
entry count, missing-payload deferrals, and catalog-predecessor metadata
revalidations. `sync-once` refuses to report settlement while payload candidates
remain deferred.

## Schema and proof-owner cleanup

The v3→v4 migration retains the authenticated scan journal in place. It proves
the complete v3 state, replaces metadata, creates cursor genesis, changes digest
domain, and re-proves catalog, journal, and cursor before one immediate
transaction commits. V1 and v2 migrate directly to v4. A shared modern catalog
loader removes repeated v2/v3/v4 row proof code while preserving exact schema
and digest domains.

The idle audit also found that speculative no-work classification re-proved the
catalog, replica, payload inventory, and cursor but omitted the mutable scan
journal. Rev0951 adds that reproof. The reads remain sequential, not one cross-
database snapshot.

## Exact nonclaims

- Every pass still reconstructs and hard-validates the complete remote
  projection.
- Local fair scans still replay rooted prefixes and fully buffer/sort immediate
  directory names.
- Metadata nomination can race; exact apply fails closed rather than promising
  hostile-writer or race-free progress.
- A payload arriving after the frozen inventory may wait until the next pass.
- Cursor publication is not atomic with replica, catalog, payload, or filesystem
  effects.
- Restart-cold payload snapshots still traverse the complete append-only store.
- Retention, restore, reachability, garbage collection, changed-block production
  transfer, rename/directory metadata, selective sync, many-share ownership,
  cross-platform behavior, and target-workload qualification remain incomplete.

## Research and next refactor

Syncthing's Block Exchange Protocol retains an index identity and monotonic
sequence across connections, useful precedent for an incremental work/index
cutpoint. SQLite's `BEGIN IMMEDIATE` documents the one-writer transaction shape
used by the exact migration and cursor publication. Linux `inotify(7)` documents
queue overflow and state rebuild, reinforcing the existing rule that watchers
accelerate but rooted scans repair.

The next structural move should be one crash-consistent exact metadata/subtree,
remote-work, and payload index with monotonic sequences, bounded queues, and a
rooted rebuild/rotating-scrub path. Version retention, restore, reachability,
quarantine, and garbage collection should share that recovery design.

Sources retained in `REVISION_EVIDENCE/rev0951/RESEARCH.md`.

## Validation

The exact final rev0951 source passed:

- all configured GCC 14.2 Debug targets;
- all 254 registered GCC tests in 35.61 seconds;
- the 35/35 GCC product lane in 26.72 seconds;
- 292 focused folder-scan-owner checks;
- 95 focused sync-once checks;
- the real two-process sync path and service diagnostics;
- the 70/70 payload/folder lexical structural audit;
- a fresh Clang 17 Debug ASan/UBSan product graph, 222/222 steps; and
- all 35 Clang product tests with leak detection across completed one-test runs
  and three serial process shards, with no sanitizer diagnostic.

A parallel compound sanitizer launcher was discarded after subprocess-heavy
tests stalled while overlapping. The exact product set was then enumerated and
run serially; `SANITIZER_SHARDS.json` records every product test exactly once.
