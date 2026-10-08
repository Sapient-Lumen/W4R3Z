# Remote apply prefix, scan cutpoint, and settlement audit — rev0950

## Mission and scope

AnonSync exists to replace Resilio Sync in a named real workflow with one
practical C++ folder-synchronization product. Direct TCP, Tor, and I2P remain
routes into the same authenticated semantics. This audit stays on that shipping
spine. It follows one `anonsync_sync once` cycle through the folder scan owner,
remote visible projection, file/tombstone effect owners, durable scan journal,
process cutpoint, terminal disposition, JSON diagnostics, and real two-process
test.

The questions are operational:

1. Can a valid remote suffix make bounded progress when all missing files do not
   fit one pass?
2. Can zero-byte files or tombstones trigger effectively unbounded effect work in
   one service turn?
3. Can a process claim `settled=true` while durable scan or remote apply work is
   still scheduled for a later turn?
4. Can a crash-surviving scan cursor advance while the process falsely reports
   no durable progress?

## Finding 1: aggregate remote bytes were a permanent zero-progress failure

The prior post-scan planner collected every sole-visible remote candidate,
starting its aggregate with bytes already materialized during local traversal.
If the sum of all still-missing remote files crossed
`maximum_total_file_bytes`, it threw before applying any planned candidate.

That was not merely conservative admission. The projection and sort order were
deterministic. A later invocation normally saw the same candidates, calculated
the same oversized sum, and failed at the same point again. A valid remote tree
whose missing files fit individually but not collectively in one pass could
therefore remain permanently unmaterialized. Increasing the aggregate default
would only move the dead boundary.

This differed from the local fair-scan correction in rev0947/rev0948: local work
had a durable cursor and could commit a prefix, while general remote apply still
required the whole selected set to fit before making any progress.

## Finding 2: bytes did not bound zero-byte files or tombstones

The same planner reserved candidate storage proportional to the complete remote
projection. A zero-byte file spends no aggregate file bytes, and a tombstone
spends no payload bytes at all. In a valid 100,000-path projection, one pass
could therefore retain and execute close to the entire remote set even though
local scan journal work was cooperatively segmented at 4,096 regular files.

The consequence was asymmetric service behavior: local observation had a count
frontier, but remote effects had only a byte frontier. This was a latency,
memory, filesystem-I/O, and shutdown-responsiveness risk even when every effect
was individually correct.

## Correction: hard full-projection admission, bounded deterministic effects

Rev0950 separates hard admission from scheduling.

Before any selected **post-scan remote prefix** is applied, the planner still
walks the complete current visible projection and fails closed on:

- more than `maximum_remote_paths` visible paths;
- a non-sole-visible or inconsistent operation shape according to the existing
  conflict rules;
- canonical path bytes beyond the configured limit;
- directory depth beyond the configured limit;
- a regular file beyond the per-file byte limit; or
- missing operation evidence.

Only after those hard checks does the planner select work. It takes one sorted,
deterministic prefix bounded independently by:

- remaining aggregate regular-file bytes for this pass; and
- remaining remote apply-owner calls for this pass.

The production operation frontier is 4,096. It counts completed calls into the
remote file or tombstone apply owner, including `Applied`, exact adoption, and
catalog no-op dispositions. It must be at least the local delivered-regular-file
frontier, because local traversal may apply one remote successor per delivered
path. Production compile-time assertions also place the default at or below the
100,000 remote-path admission default. Runtime configuration deliberately does
not require the fixed scheduling value to be at or below every user-selected
remote-path limit; a smaller admitted projection is already an intrinsic upper
bound on effects.

Once either scheduling frontier is reached, the first non-fitting candidate and
all later otherwise eligible candidates are deferred. A later small file is not
allowed to jump around an earlier large file. This preserves one simple progress
argument: committed prefix effects become exact catalog/filesystem no-ops on the
next pass, so the first still-missing suffix candidate can then spend the freed
allowance. The candidate vector reserves at most the remaining operation
allowance rather than the whole remote projection.

The report now exposes:

- `remote_apply_operations`;
- `deferred_remote_apply_candidates`; and
- `remote_apply_stop_reason`, one of `not_started`, `end_of_projection`,
  `aggregate_file_byte_frontier`, or `operation_count_frontier`.

These fields are scheduling diagnostics. They are not replicated evidence,
catalog authority, or permission to infer deletion.

## Hard-suffix preflight remains fail-closed

Prefix scheduling must not turn hard validation into “validate only what will be
executed.” A focused regression places a valid first candidate before a later
path that exceeds the configured path-byte limit while the operation frontier
would otherwise select only the first item. The pass rejects the later invalid
path and proves that neither the valid prefix nor catalog state changed.

This property is intentionally narrower than a global point-in-time transaction.
Local scan effects may already have committed before the post-scan remote plan is
formed, and every authoritative remote apply revalidates evidence, catalog state,
and pathname immediately before its effect. The claim is that a selected
**post-scan remote prefix** is not applied while a hard-invalid suffix remains in
that same visible projection.

## Finding 3: bounded success could be falsely reported as settled

The old `sync-once` completion classifier treated only explicit conflict and
skipped-tombstone counters as unresolved. A pass that successfully materialized
one bounded remote prefix could therefore return `complete_changed` and
`settled=true` while `deferred_remote_apply_candidates` was nonzero. The service
would have made useful progress, but the terminal contract overstated completion.

Rev0950 makes the final post-pull folder pass the settlement fence. A completed
cycle is still unresolved when that final pass:

- did not complete its authenticated local scan epoch;
- deferred remote apply candidates;
- deferred an unadjudicated local absence behind an exact remote file;
- did not reach `end_of_projection`; or
- observed the existing conflict/tombstone unresolved states.

Only the final pass contributes scheduling remainder. An earlier pass may stop
at a frontier and the later pass in the same `sync-once` cycle may finish that
exact suffix. Treating any earlier remainder as permanently unresolved would
create the opposite reporting error.

## Finding 4: scan-only durable progress was absent from the process cutpoint

The scan journal owns crash-surviving scheduling state: epoch, continuation
path, seen-path count, cumulative path bytes, and a domain-separated chain
digest. A bounded segment can commit that state while every catalog mapping and
replica operation remains unchanged. The former process cutpoint observed only
catalog and replica values, so a real durable continuation transition could be
misclassified as a no-op.

The folder owner now returns a validated
`SyncReplicaFolderScanProgressSnapshot`. `sync-once` includes its five fields in
the before/after cutpoint and JSON. Equality therefore recognizes scan-only
progress without inventing catalog mutations.

Catalog content, scan progress, and replica state are observed in sequence under
their existing SQLite owners. They are not one cross-database atomic snapshot.
That limitation is explicit and preferable to pretending a process-level read
has transaction authority it does not possess.

## Executable proof

Focused folder-owner tests establish:

- two individually valid remote files under a one-file aggregate budget converge
  as one committed prefix and one later suffix, rather than failing forever;
- two zero-byte files followed by a tombstone and another zero-byte file converge
  as two effects plus two effects under a count frontier;
- the selected-prefix/later-invalid-suffix case makes no post-scan remote effect;
- zero or composition-invalid operation frontiers fail before catalog mutation;
- scan-progress snapshots match the durable journal head before and after
  restart-backed epoch completion.

The real two-process product test forces three 42-byte files through a 42-byte
aggregate frontier:

1. cycle one pulls all authenticated evidence, materializes exactly the first
   sorted file, defers two candidates, and reports complete-but-unsettled;
2. cycle two materializes the remaining remote files across its two folder
   passes, but the final authenticated local scan still has a suffix, so the
   cycle remains unsettled; and
3. cycle three changes no catalog or replica content, completes the durable scan
   epoch, reports that scan-only transition as progress, and only then settles.

A fourth duplicate cycle is a durable no-op. Reverse-direction convergence still
uses the same peer server and wire protocol.

## Remaining costs and failure modes

This revision fixes a liveness defect and bounds effects; it does not make the
remote planner indexed or asymptotically cheap.

1. **Complete visible projection work remains.** Every pass still snapshots and
   examines up to the admitted remote-path ceiling so hard suffix checks and the
   deferred count remain exact.
2. **No durable remote apply cursor exists.** Progress relies on already-applied
   prefix values remaining exact no-ops. Continuous mutation of an early path
   can repeatedly consume bytes or an effect slot and delay a later suffix.
3. **The local fair cursor still replays its root prefix.** Semantic reachability
   is fixed, but metadata work grows with the skipped prefix.
4. **Immediate directory names are still buffered and sorted.** A very wide
   directory can retain far more than 4,096 basenames before the delivered-file
   frontier stops callbacks.
5. **Watcher events are not completeness authority.** Queue overflow, watch
   invalidation, mounts, and rename pairing can lose or ambiguously relate
   events. The rooted scanner remains repair authority.
6. **History is append-only.** Catalog and payload capacity still describe a
   current composition boundary, not guaranteed edit/delete churn headroom.
7. **Whole-file identity remains the shipping transfer baseline.** A one-byte
   edit can require a complete new payload through bounded ranges.

## Research and architectural inference

Sources consulted 2026-07-30:

- https://docs.syncthing.net/specs/bep-v1.html
- https://docs.syncthing.net/users/syncing.html
- https://docs.syncthing.net/users/tuning.html
- https://man7.org/linux/man-pages/man7/inotify.7.html
- https://help.resilio.com/hc/en-us/articles/205458095-Selective-Sync
- https://help.resilio.com/hc/en-us/articles/204754239-Using-Archive-for-file-versioning-and-restoring-deleted-files

Syncthing's current protocol documents persistent index identity plus monotonic
sequence numbers for delta index exchange, smaller incremental index updates,
block hashes, bounded block requests, and possible local block reuse. Its product
documentation describes a persistent index database and combines watcher wakes
with periodic full scans because notifications may miss changes. Its tuning
surface separately limits pending pull bytes and concurrent writes rather than
assuming one byte bound controls every resource.

Linux `inotify(7)` explicitly documents queue overflow with dropped events and
recommends cache rebuild as a robust recovery option. It also documents that the
paired rename events are not atomically inserted or guaranteed consecutive.
This supports AnonSync's existing division: watcher state may prioritize work,
but a durable index plus rooted scan/scrub must own truth.

Resilio's current user documentation treats selective placeholders and retained
old/deleted versions as ordinary workflow behavior. Those are product obligations
for replacement, not reasons to clone Resilio internals.

The architectural inference is that AnonSync should not add another cursor to
every whole-state loop independently. The next scale owner should be one
crash-consistent exact metadata/index layer with a monotonic change sequence and
bounded work queues. It should provide indexed local subtree successors and
remote effect candidates, while the descriptor-rooted walker remains a rebuild
and rotating-scrub oracle. Admission must remain hard and transactionally bound;
operation/byte frontiers should control service-turn work; queue state must be
reconstructible after a crash. A durable payload metadata index, block manifests,
version retention, restore, and garbage collection should then attach to that
same ownership model rather than creating parallel truth stores.
