# Bounded scan-segment frontier audit — rev0948

## Question

After rev0947 made a local scan epoch durable and fair, can one segment still
perform effectively whole-tree callback and journal work when file bytes are
small, and can that work be bounded without allowing a persisted cursor to
outrun descriptor-rooted namespace re-attestation?

The audited shipping path is:

- `src/sync_replica_folder_observer.{hpp,cpp}`;
- `src/sync_replica_folder_scan_owner.{hpp,cpp}`;
- `src/sync_replica_folder_process.cpp`;
- the corresponding observer, owner, process, and source-audit tests.

The watcher is an accelerator only. It does not participate in the scan cursor
or deletion proof.

## Original composition failure

Rev0947's resumable observer had two relevant bounds:

- a whole-walk entry limit, currently at most 100,000;
- an aggregate classified-file-byte frontier for one resumable segment.

The first protects namespace admission. The second decided when a productive
segment stopped. A zero-byte file spends no byte budget. Therefore a valid tree
of 100,000 zero-byte regular files could satisfy the byte frontier while causing
100,000 visitor effects and 100,000 path acknowledgements to be staged for one
journal publication.

The journal was already transactionally correct: each path effect committed
first, the walker re-proved the namespace, and the segment journal then advanced
the durable head once. The defect was that “bounded segment” did not compose
across distinct resource dimensions. Byte-bounded did not imply path-count-
bounded, memory-bounded, statement-count-bounded, or short writer ownership.

## Selected boundary

`SyncReplicaFolderTraversalSegmentLimits::maximum_regular_files` bounds the
number of eligible regular paths delivered to the visitor in one explicit
resumable traversal. Production defaults to 4,096.

The count is intentionally separate from `SyncReplicaFolderObservationLimits`:

- `maximum_entries` remains a hard whole-walk safety boundary and includes every
  directory entry, ignored object, and cursor-skipped prefix entry;
- `maximum_total_file_bytes` remains the productive byte frontier;
- `maximum_regular_files` is an internal scheduling frontier for visitor and
  journal work.

The field is retained inside `SyncReplicaFolderConvergencePassLimits`, not
exposed through service configuration. It is not yet an operator contract or a
performance tuning promise.

## Cutpoint analysis

### Cursor-skipped prefix

A regular path at or before `resume_after_path` increments only
`skipped_regular_file_count`. It does not increment the delivered regular-file
count and does not spend the segment byte budget. This preserves rev0947's
semantic continuation: the durable prefix may cost metadata work, but it cannot
consume the productive suffix allowance.

### Before the next callback

For the next eligible path, the walker checks:

```text
already delivered >= maximum_regular_files
```

before classifying that path's size and before invoking the visitor. If full, it
returns `StoppedAtSegmentFrontier`. The undelivered path remains after the
current cursor and is reconsidered by the following segment.

A byte frontier remains independently checked. A file that cannot fit an empty
byte segment still fails instead of producing a zero-progress loop. A count
frontier cannot be zero because validation rejects it before the root is opened.

### Successful visitor

Only after the visitor returns successfully does the walker:

- charge the classified bytes;
- increment the delivered regular-file count;
- mark that the segment made progress;
- set `resume_after_path` to that canonical path.

A visitor exception therefore cannot advance even the in-memory cursor.

### Rooted unwind

A stop disposition propagates through the same recursive walker as ordinary
completion. Every opened child directory is reopened by name beneath its parent
and compared by directory identity. The retained root authority is verified
after the recursive walk returns. The traversal result is not returned to the
folder owner before these checks finish.

The substitution regression mutates `nested` inside the first callback while a
one-path count frontier is active. The next path causes a stop, but unwinding
finds that `nested` was replaced and throws. This proves that the count frontier
is not itself a publication cutpoint.

### Durable publication

The folder owner performs each path effect through the established idempotent
owner. Only after that effect returns does it append the canonical path to
`segment_seen_paths`. The vector reserves at most the effective minimum of the
whole entry allowance and the local delivered-path frontier.

After traversal returns, the owner releases any payload mutation batch,
re-proves the retained payload cutpoint when present, and calls the scan-progress
journal owner once. That transaction inserts the staged paths and compare-and-
swap updates the progress head. A crash before journal publication replays
already committed effects; it never treats an unproved cursor as durable.

## Compatibility boundary

The pre-existing resumable API remains available. It delegates to the explicit
overload with a delivered-file allowance equal to `maximum_entries`. Since a
walk cannot deliver more regular files than all admitted entries, this preserves
the old aggregate-byte-only behavior. The production folder owner opts into the
new explicit default.

This separation keeps tests and diagnostic callers source-compatible while
making the shipping scheduler's stronger composition visible in source.

## Zero-byte restart proof

Five zero-byte files ordered `a.txt` through `e.txt` are scanned with a two-path
frontier.

| Pass | Delivered | Durable cursor | Seen count | Complete |
|---|---:|---|---:|---|
| 1 | `a.txt`, `b.txt` | `b.txt` | 2 | no |
| 2 | `c.txt`, `d.txt` | `d.txt` | 4 | no |
| 3 | `e.txt` | reset after epoch completion | 0 | yes |

The first pass is traced at SQLite statement level: two seen-path INSERTs and one
progress-head UPDATE. Owners are reconstructed between passes, proving that the
suffix comes from durable progress rather than process memory. Final state has
five catalog entries and operations but one empty content-addressed payload.

## Idle fast-path refactor proof

The prior idle proof retained an observed-path vector, built a second vector of
cataloged file paths, sorted both, and compared them. Rev0948 instead uses:

1. per-observed-path membership in a unique `File` catalog entry;
2. complete traversal;
3. equality of observed regular-file cardinality and catalog `File`
   cardinality;
4. explicit inspection of every non-File/tombstone catalog path.

Given the catalog's unique canonical-path invariant and a filesystem traversal
that cannot emit one pathname twice, membership plus equal cardinality proves
set equality. The tombstone loop is necessary: regular-file membership says
nothing about a cataloged tombstone pathname, and an unsupported object there
must fail visibly rather than count as absence.

The refactor removes duplicate whole-tree path storage and sorting. It does not
remove exact file observation, payload proof, replica proof, or catalog scans.

## SQLite interpretation

This correction is not based on the obsolete claim that WAL cannot support
large transactions. SQLite states that WAL's historical large-transaction
limitation was removed in version 3.11.0. The project's bundled SQLite 3.53.3 is
well beyond that point.

The relevant application facts are instead:

- the C++ owner must retain one string per pending acknowledgement;
- every pending path requires a prepared INSERT iteration and hash-chain update;
- `BEGIN IMMEDIATE` starts a write transaction at once and admits only one
  writer;
- bounded work reduces the maximum application-controlled staging and writer
  interval, while leaving correctness independent of the chosen default.

No latency, memory, or lock-duration number is claimed without target-scale
measurement.

## Residual risks

### Per-directory name retention

`read_sorted_components_or_throw` reads and stores every immediate basename in a
directory before processing any child. A flat directory near the entry ceiling
therefore still creates a large vector even though only 4,096 regular paths are
delivered. The count frontier does not solve this. A future iterator or indexed
subtree cursor must preserve deterministic order and directory identity proofs
without retaining the whole component set.

### Prefix replay

Every segment opens the root and classifies the cursor-skipped prefix. The
continuation prevents repeated path effects and payload work, not repeated
metadata work. Large deep prefixes can still dominate runtime.

### Path-local durable work

The conservative fallback performs substantial catalog, replica, and payload
attestation around individual path effects. A 4,096-path segment is a maximum
callback/journal unit, not evidence that 4,096 paths meet a desired latency.

### Namespace mutation

The epoch remains an asynchronous sweep. Already-seen changes wait for a later
epoch, cataloged physical presence behind a completed cursor can force restart,
and uncataloged creation behind the cursor is discovered by the next epoch. The
rev0947 absence fences remain necessary.

### Other product gaps

This revision does not add a durable payload index, payload/version garbage
collection, changed-block transfer, rename identity, empty-directory or broad
metadata semantics, recovery UX, multi-share device ownership, selective sync,
or public-overlay qualification.

## Recommended next scale slice

Build one durable, crash-consistent metadata/subtree index that can seek near a
persisted cursor and serve as an optimization only. Preserve the existing rooted
scanner as a complete rebuild oracle and use bounded rotating revalidation to
detect index drift. The index should distinguish ordinary file observation
metadata from deletion authority; no cache hit should manufacture absence.

Before fixing the internal default as a product contract, capture the first real
Resilio uninstall workload and measure path distribution, flat-directory width,
file sizes, churn, restart behavior, acceptable catch-up latency, and direct/Tor/
I2P routes.

## External references

- SQLite WAL: https://www.sqlite.org/wal.html
- SQLite transactions: https://sqlite.org/lang_transaction.html
- SQLite isolation: https://sqlite.org/isolation.html
- Syncthing tuning: https://docs.syncthing.net/users/tuning.html
- Syncthing FAQ: https://docs.syncthing.net/users/faq.html
