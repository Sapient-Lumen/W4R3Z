# AnonSync rev0948 revision notes

## Mission

AnonSync exists to replace Resilio Sync in a named real workflow with one
practical C++ folder-synchronization product. Direct TCP, Tor, and I2P remain
routes into the same authenticated reconciliation semantics. This revision
strengthens the shipping folder owner and observer. It does not add another
daemon, policy plane, sync engine, or operator-facing scheduler setting.

## Primary correction: byte bounds did not bound path effects

Rev0947 made local repair semantically fair by persisting a traversal cursor and
an authenticated seen-path journal. Its segment frontier, however, was expressed
only in classified file bytes. A folder containing many zero-byte or very small
regular files could therefore deliver every admissible path in one segment. At
the current hard namespace ceiling that meant as many as 100,000 independently
committed path effects could be retained as path strings and published by one
SQLite journal transaction.

That was not a SQLite correctness limitation. Current SQLite supports large WAL
transactions. It was an application scheduling and composition defect: the byte
frontier did not bound callback count, in-memory acknowledgement staging,
prepared INSERT work, or the duration for which one immediate writer transaction
owned the scan-progress publication cutpoint.

Rev0948 adds an independent delivered-regular-file frontier:

- the explicit resumable observer overload accepts
  `SyncReplicaFolderTraversalSegmentLimits`;
- production defaults to at most 4,096 delivered regular paths per local scan
  segment;
- paths at or before the durable cursor are still classified against the
  whole-walk entry limit but do not spend the delivered-file frontier;
- the count check occurs before size classification and before the next visitor
  call, leaving that path for the following segment;
- a successful visitor remains the only operation that advances the in-memory
  cursor;
- a count stop unwinds the same descriptor-rooted walker, rebinds every opened
  directory, and verifies the retained root before a cursor can be published;
- the folder owner reserves only the effective path segment, stages a path only
  after its independently committed effect, and then publishes one bounded
  authenticated journal segment;
- zero is rejected before any catalog mutation, and production compile-time
  assertions bind the default to the ordinary entry ceiling.

The pre-rev0948 resumable overload remains source-compatible and retains its
aggregate-byte-only behavior by setting the delivered-file allowance to the
whole traversal entry limit. The shipping folder owner deliberately selects the
new explicit bound.

## Runtime proof: zero-byte 2 + 2 + 1 continuation

A focused owner fixture creates five zero-byte files and configures a two-path
segment. Across reconstructed owners using the same catalog it proves:

1. the first pass delivers and publishes `a.txt` and `b.txt`, records two journal
   INSERT statements and one progress-head UPDATE, and persists cursor `b.txt`;
2. the second pass resumes at the exact suffix, publishes `c.txt` and `d.txt`,
   and persists cursor `d.txt`;
3. the third pass publishes `e.txt`, completes and resets the epoch, retains five
   catalog and operation records, and deduplicates the five empty files to one
   content-addressed payload.

The observer test independently proves the same `2 + 2 + 1` path sequence,
exact skipped-prefix counts, and no duplicate delivery. A callback then replaces
an opened directory at the count cutpoint; the traversal rejects completion
because the directory identity no longer matches. This binds the new scheduler
frontier to the existing rooted re-attestation boundary rather than treating a
count as authority by itself.

## Refactor: idle set equality without a second whole-tree path vector

The unchanged-folder fast path previously copied every observed regular path
into a second vector, sorted it, copied every cataloged file path into another
vector, sorted that, and compared the vectors. That duplicated path storage on
exactly the large idle trees for which the fast path exists.

Rev0948 removes those copies. Every delivered regular path must already resolve
to one unique `File` catalog entry and pass exact operation, payload, and file
observation checks. After a complete traversal, equality between the observed
regular-file count and the number of `File` catalog entries proves that no file
mapping was omitted. Tombstone paths remain explicitly inspected, so a regular
file or unsupported object at a tombstoned pathname cannot be mistaken for
absence.

This refactor removes one O(number-of-files) path-copy-and-sort phase. It does
not make the idle pass metadata-free: the pass still walks the namespace,
observes exact local files, and uses the existing payload and replica cutpoints.

## Exact authority sequence

The count frontier changes scheduling only. Durable authority remains ordered as
follows:

1. Validate the whole-walk observation limits and the delivered-file segment
   limits before work.
2. Open an independent retained-root descriptor and capture its mount identity.
3. Classify the deterministic prefix at or before the durable cursor without
   redelivery.
4. Before the next eligible callback, stop if the delivered-file frontier is
   already full; otherwise apply the existing byte checks.
5. Let the visitor perform one exact, idempotent path effect.
6. Advance only the in-memory segment cursor and stage that path only after the
   effect succeeds.
7. Rebind every opened directory while unwinding and verify the retained root.
8. Release/re-prove payload authority and publish the staged journal paths plus
   progress head in one immediate transaction.
9. Permit absence inference only after the complete authenticated epoch proof
   introduced by rev0947.

A crash before step 8 loses scheduling progress, not path effects. Restart
replays those effects idempotently. A traversal identity failure before step 7
cannot publish the cursor. The new frontier therefore cannot outrun the rooted
proof boundary.

## Exact nonclaims and remaining scale risks

The 4,096-path default bounds delivered callbacks, one acknowledgement vector,
and one journal publication. It does **not** bound all scan memory or metadata
work:

- each directory is still completely read into a basename vector and sorted
  before its children are processed;
- every resumed segment starts at the retained root, re-enumerates directories,
  and `lstat`s the skipped prefix;
- `maximum_entries` still counts directories, symbolic links, special files,
  and internal artifacts, not only synchronized regular files;
- the ordinary path-local fallback still reloads and re-attests large durable
  state around individual effects, so a bounded segment can remain expensive;
- the asynchronous epoch is not a point-in-time filesystem snapshot;
- a count frontier is a scheduling bound, not target-workload latency,
  throughput, memory, or lock-horizon qualification.

The next scale owner should still be a crash-consistent exact metadata/subtree
index that can resume near the cursor rather than replaying the root prefix. The
current descriptor-rooted complete scanner should remain the rebuild and
rotating-scrub oracle. A durable payload metadata index, retention/GC, changed-
block transfer, identity-preserving rename, directory and metadata semantics,
recovery UX, multi-share device ownership, and public Tor/I2P qualification also
remain product work.

## Research notes

The design deliberately avoids claiming that SQLite cannot handle a large WAL
transaction. SQLite documents that the old pre-3.11 large-WAL limitation no
longer applies. It also documents that `BEGIN IMMEDIATE` starts a write
transaction immediately and can fail with `SQLITE_BUSY` if another writer is
active. The application therefore benefits from bounding the amount of staged
work and the writer interval even though SQLite correctness does not require an
arbitrary 4,096-row ceiling.

Syncthing's current documentation similarly treats filesystem notifications as
an accelerator that avoids unnecessary I/O while retaining periodic scanning,
and notes that scans of large folders can create resource spikes. AnonSync keeps
the watcher/complete-scan division but does not claim equivalent maturity or
performance.

Sources:

- https://www.sqlite.org/wal.html
- https://sqlite.org/lang_transaction.html
- https://sqlite.org/isolation.html
- https://docs.syncthing.net/users/tuning.html
- https://docs.syncthing.net/users/faq.html

## Validation

The frozen rev0948 source passed:

- all configured GCC 14.2 Debug targets built successfully from the exact source after retained incremental completion;
- 254/254 registered GCC tests passed in 34.05 seconds;
- 35/35 GCC product tests passed in 16.83 seconds;
- 64/64 focused observer checks;
- 232 focused folder-scan-owner checks;
- the real folder/service process tests exercising continuation and restart;
- the 55/55 payload/folder structural audit;
- the Clang 17 ASan/UBSan product target completed from the exact source after the clean build reached 169/222 steps and the retained build completed its 54-step resume;
- 35/35 Clang product tests passed in five fresh bounded CTest shards (89.72 cumulative real test seconds) with leak detection and no sanitizer diagnostic.

The lexical audit is hygiene evidence only. Filesystem, transaction, crash,
identity, and restart claims are carried by compiled runtime tests, source
review, and the explicit authority audit.
