# Durable fair scan epoch audit — rev0947

## Scope

This audit follows the linked shipping path from the retained folder authority
through local observation, catalog mutation, scan-progress persistence, absence
inference, remote planning, and process-visible status. Its question is narrow:
can bounded repair work eventually reach every admissible regular path without
creating false deletion or restoration authority across restart and concurrent
namespace mutation?

The audited implementation is:

- `src/sync_replica_folder_observer.{hpp,cpp}`;
- `src/sync_replica_folder_scan_owner.{hpp,cpp}`;
- `src/anonsync_folder.cpp`;
- `src/anonsync_sync.cpp`;
- the corresponding observer, owner, and process tests.

The watcher was separately inspected as an accelerator. It is not treated as
completeness authority.

## Original failure

The old traversal was deterministic and bounded, but not fair. Let a scan visit
regular files `p1 ... pn` in the observer's bytewise component preorder and let
`B` be the aggregate classified-byte frontier. If the stable prefix
`p1 ... pk` consumes `B`, the pass aborts before `p(k+1)`. Starting every later
pass at the root repeats the same prefix. No state distinguishes productive work
from an endlessly repeated prefix.

This is more than latency. A suffix file can remain outside repair forever, and
deletion inference is intentionally unavailable until a complete traversal.
Raising `B` only moves the starvation boundary.

## Traversal order and cursor correctness

The filesystem walker sorts each directory's immediate basenames and performs a
preorder depth-first traversal. Persisted cursor order therefore cannot be a
flat comparison of canonical path strings. For example, directory subtree
`a/two.bin` is visited before sibling `a.txt`, even though a naïve character
comparison may order the slash differently from the dot.

`sync_replica_folder_traversal_path_less` compares path components according to
the walk's real ordering. The resumable walker classifies paths at or before the
cursor but does not deliver or charge their regular-file bytes again. It updates
the returned cursor only after the visitor succeeds. When a later file would
cross the aggregate frontier, the walker stops cooperatively, re-proves every
opened directory and the retained root during unwind, and returns
`completed=false`. If the first eligible file cannot fit an empty segment, it
fails instead of manufacturing zero progress.

The caller contract remains that visitor effects are idempotent and that
`maximum_file_bytes <= maximum_total_file_bytes` for productive scheduling.
Shipping configuration composes those limits; the generic observer does not
claim to be a policy owner.

## Durable schema-v3 owner

The folder catalog gains two owned STRICT tables:

`sync_replica_folder_catalog_scan_progress`
: one row containing epoch, continuation path, seen count, cumulative path
  bytes, and chain digest;

`sync_replica_folder_catalog_scan_seen`
: one row per successfully adjudicated canonical path, keyed by ordinal and
  carrying epoch and cumulative chain digest.

The chain is domain separated with
`anonsync:sync-replica-folder-scan-seen-chain:v1`. Each row commits the previous
digest, epoch, ordinal, and path. The progress head commits the exact tail.
Counts and path bytes are bounded by the same durable catalog limits.

Exact schema-v1 and schema-v2 objects are attested before a transactional
migration to v3. A contaminated or near-match schema is not repaired by guess.
The improved schema diagnostic reports expected and observed owned/total object
counts, so future drift is actionable rather than opaque.

## Publication sequence

For one local segment the owner:

1. loads and attests the progress head;
2. resumes the rooted traversal after its exact cursor;
3. opens, freezes, hashes, and re-attests each delivered file;
4. applies that path's idempotent catalog/payload effect;
5. appends the path to an in-memory segment list only after the effect succeeds;
6. re-proves traversal authorities while unwinding;
7. publishes the whole segment list in one immediate SQLite transaction;
8. if traversal completed, re-reads and verifies the complete ordered journal
   before absence inference.

The progress transaction compare-and-swaps the epoch, count, path-byte count,
cursor, and digest head. It reuses one prepared INSERT statement and updates the
singleton head once. Failure before commit leaves no partial scheduling prefix.
Path effects are already durable and can be repeated.

## Why batching is safe and cheaper

A transaction per file would serialize the scan through one SQLite commit for
every regular path. Under WAL plus a FULL durable synchronization policy, each
commit may introduce a WAL synchronization boundary. That is avoidable work and
can dominate many-small-file repair.

Batching the scheduling journal does not batch the path effects themselves.
Therefore a failed journal transaction does not roll back already synchronized
files and does not make them unsafe; it only causes replay. Conversely, the
cursor cannot advance before the walker has re-proved the segment's retained
filesystem authorities.

An internal chunk size was deliberately not added. Publishing a mid-segment
cursor before the walker unwinds and re-attests the retained directory chain
would weaken the identity proof. A later implementation may safely chunk only
if it also introduces an explicit reproof boundary.

## Completion and deletion authority

A `completed=true` traversal is necessary but is not trusted alone. The owner
loads every seen row in ordinal order, validates epoch, strict traversal order,
count, cumulative path bytes, and every hash-chain link, then compares the
journal with the fresh catalog.

For a cataloged regular path omitted by the journal:

- if the path is physically absent under rooted no-follow observation, absence
  may become a causal tombstone;
- if it is physically present, the epoch is restarted because the path appeared
  behind the cursor or the namespace otherwise invalidated the sweep;
- an observation error fails closed.

After completion, the journal is reset to a new epoch. Partial or failed scans
never infer deletion.

## Concurrent mutation matrix

The owner implements a conservative asynchronous sweep, not snapshot isolation.

| Mutation relative to cursor | Rev0947 treatment |
|---|---|
| Existing cataloged file edited before it is visited | New exact observation is applied in this epoch. |
| Existing cataloged file edited after it was visited | Deferred to the next epoch. |
| Existing cataloged file deleted before it is visited | May become a tombstone after complete epoch proof. |
| Existing cataloged file deleted after it was visited | Exact old remote predecessor is fenced; next epoch adjudicates deletion. |
| Cataloged path appears behind cursor but is absent from journal | Completion proof sees it physically present and restarts the epoch. |
| New uncataloged path appears behind cursor | Found in the following epoch; it cannot cause false deletion because it has no predecessor. |
| Remote tombstone arrives while an unadjudicated local regular file exists | Generic tombstone removal is skipped. |
| Distinct remote successor arrives while local path is absent | Existing remote-successor/conflict rules remain available. |

## The completed-epoch restoration race

Audit of the first implementation found a severe edge:

1. segment one visits `a` and journals it;
2. the user deletes `a`;
3. a later segment reaches the end and completes the epoch;
4. `a` is in the journal, so absence inference does not select it;
5. the remote inventory still contains the exact catalog predecessor;
6. generic remote planning restores `a` immediately.

The repair is not to call the journal a snapshot. The owner now recognizes an
absent local path whose remote file is exactly the retained catalog predecessor
and defers that file as `deferred_unadjudicated_local_absence_remote_file_count`.
The next epoch either observes a recreation or publishes the deletion. A remote
file with a genuinely different operation/content identity is not hidden behind
this fence.

The regression `test_completed_epoch_does_not_restore_deleted_seen_prefix`
requires precisely this sequence and then requires one later deletion
publication rather than restoration.

## Watcher audit

The Linux watcher requests a rebuild and wakes the service on queue overflow,
watch invalidation, topology change, or its own observation-bound exhaustion.
Unsupported/inactive watching is retried. The service caps long waits and still
runs periodic repair reconciliation.

This is the correct authority split. Inotify events can race names, overflow,
lose watches on unmount/invalidation, and do not cover every storage topology.
Events accelerate likely paths; the rooted scan and catalog state decide
completeness.

## Performance and storage model

The fairness gain removes repeated payload work on a stable prefix, but skipped
paths are still re-enumerated and `lstat`-classified from the root. For `S`
segments over `N` sorted paths, metadata work can still approach repeated-prefix
quadratic behavior in an unfavorable distribution. This is acceptable as a
correctness bridge, not the final huge-tree design.

The journal retains one path and one digest per observed regular file until the
epoch completes. A segment containing very many zero-byte files may create a
large immediate transaction. The hard path-count/path-byte limits bound it, but
that bound is an admission ceiling rather than a latency qualification.

A stronger next design should use a durable metadata index and subtree-aware
continuation token so that a resumed sweep can avoid root-prefix reclassification
while retaining descriptor-rooted identity proof. It should also distinguish the
regular-file catalog ceiling from the all-directory-entry traversal ceiling.

## Tamper and startup behavior

Startup validates the singleton progress head, exact row geometry at the first
and tail positions, and absence of rows beyond the declared tail. It does not
rehash every middle row on every service start. Before deletion authority, the
entire ordered hash chain is always loaded and checked. Thus middle corruption
cannot authorize a false deletion, though it may be reported only when the epoch
reaches completion.

This is a deliberate availability/cost tradeoff, not cryptographic protection
against a hostile process with database write access. SQLite ownership,
filesystem permissions, and the existing catalog authority model remain the
security boundary.

## Validation map

- Observer ordering, bounded progress, first-file failure, cursor disappearance,
  root/directory substitution, and resumed completion: 49 checks.
- Durable epoch continuation, restart, migration, tampering, deletion delay,
  resurrection, remote tombstone fencing, completed-epoch absence race, and
  batched progress publication: 225 checks.
- Real CLI process restart through two bounded segments and one idle completion.
- Complete GCC registry: 254/254.
- Clang ASan/UBSan product lane with leak detection: 35/35; no diagnostics.
- Structural source audit: 51/51, explicitly non-semantic.

## Recommended next work

1. Name the first Resilio uninstall workload and measure its real tree geometry.
2. Add a durable exact metadata index or subtree continuation owner that removes
   repeated root-prefix classification without making watcher events authority.
3. Separate cataloged regular-file capacity from the all-entry traversal budget
   and expose truthful diagnostics for both.
4. Add journal chunking only with a preserved rooted re-attestation boundary.
5. Continue with changed-block transfer, bounded history/GC/restore, rename and
   metadata semantics, and target-route qualification.
