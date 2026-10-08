# Revision notes — rev0964

The shipping resumable folder walk now bounds each sorted immediate-directory
basename batch instead of materializing a flat directory's complete component
vector.

## Mission move

Rev0947 made local repair scans restartably fair and rev0948 bounded one
productive segment to 4,096 delivered regular paths. The observer nevertheless
copied and sorted every immediate basename before it could deliver the first
path. A flat directory near the namespace ceiling therefore remained a repeated
memory cliff on every segment. Rev0964 removes that cliff from the production
resumable path without adding a second scan owner or weakening deletion fences.

## C++ implementation

- Added the fixed internal
  `kSyncReplicaFolderTraversalMaximumBufferedDirectoryComponentsPerBatch =
  4096` boundary.
- Added an exact bounded max-heap selector for the next lexicographically
  smallest immediate components after an in-directory boundary.
- Uses one reserved `std::vector<std::string>` as both the heap and the sorted
  output, then moves it into the batch; no `priority_queue` container plus
  copy-out vector coexist.
- Compares unselected `dirent` names through `std::string_view`, allocating only
  names admitted to the bounded heap.
- Sorts each selected batch in place in the same bytewise `std::string` order as
  the old complete vector.
- Refactored regular-file classification, callbacks, recursive descent, and
  post-walk directory rebinding into one shared `walk_component_batch_or_throw`
  implementation.
- Retains the first pass's eligible-component count as a decreasing visit
  budget, preventing later rescans from chasing a concurrently appended suffix.
- Returns the non-complete `directory_census_frontier` outcome when a later
  enumeration sees eligible names beyond that budget, preserving the last
  delivered cursor while withholding completed-epoch absence authority.
- Rescans the same open directory only while first-census work remains and the
  current traversal segment can still perform useful delivered-file work.
- Charges every non-dot entry in the first complete directory census exactly
  once; selection rescans do not consume the namespace ceiling again.
- Preserves classification of cursor-skipped regular files so continuation
  cannot bypass the independent whole-folder regular-file capacity.
- Leaves the non-resumable complete observer on the former whole-directory
  vector path and records that boundary explicitly.

## Diagnostics and regression

`SyncReplicaFolderTraversalSegment` now exposes non-authoritative directory
enumeration-pass count and largest individual component-batch count. The new
4,113-file regression proves exact sorted delivery with no duplicate, two count
frontiers followed by namespace completion, a 4,096-name largest batch, exact
one-versus-two enumeration-pass behavior, and no double charging of the 4,113
namespace entries. A second regression inserts one interleaved name that
displaces the last original census member from the final bounded batch, plus
sixteen suffix names. It proves the first segment returns
`directory_census_frontier` rather than false completion and that its persisted
cursor reaches the displaced original plus every inserted name exactly once.
Existing rooted race and folder-owner convergence suites continue to prove
post-walk directory identity, durable cursor/journal ordering, and completed-
epoch absence.

## Audit/refactor

The first draft described 4,096 as a process-wide simultaneous-basename ceiling.
That was false because recursive descent can retain one unprocessed parent batch
per active directory. The final API and documentation say **per batch** and
retain the configured depth limit as part of aggregate memory truth.

The audit also corrected two concurrency defects in the first draft. Bounded
heap storage did not by itself stop later rescans from chasing newly created
names outside the already-charged census. The decreasing first-census budget
makes one visit finite. A second review found that count fencing alone could
let an interleaved new name consume the final slot, displace an original census
member, and still return `EndOfNamespace`. The final stop reason denies
completion whenever a later pass observes work beyond the first census; the
durable cursor then resumes at the displaced member without granting deletion
authority to the moving namespace.

The audit rejects a performance overclaim. The bounded selector rescans a
large immediate directory for later batches, and every service segment still
replays and `lstat`s its skipped path prefix. Rev0964 trades an unbounded flat-
directory allocation for bounded per-batch memory; it does not claim a durable
subtree index, point-in-time snapshot isolation, or huge-tree qualification.

See `BOUNDED_RESUMABLE_DIRECTORY_COMPONENT_BATCH_AUDIT_rev0964.md`.

## Validation

- Fresh GCC 14.2 debug graph: **527/527 configured build edges**, followed by exact-source no-work bundled-SQLite re-attestation.
- Complete GCC registry: **258/258 tests** on the final source and documentation, with the final structural source audit closing test 123.
- Independent GCC product lane: **39/39 tests** in bounded serial shards.
- Focused GCC checks: **84** resumable SHA-256, **19** scrub-state, **26** verification-index, **576** payload-store, **30/30** rooted POSIX resolution, **92** network-model checks with **41** generated operations, **296** SQLite-owner, **360** folder-owner, **110** sync-once, **2,043** TLS, **17** integrity-evidence, **92** local-control, **77/77** folder-observer, and **6/6** observer-race checks.
- Structural payload-store/folder-traversal authority audit: **205/205 checks**.
- Fresh Clang 17 ASan/UBSan product dependency graph: **238/238 build edges**, followed by exact-source no-work re-attestation.
- Clang ASan/UBSan product set: **39/39 tests** with leak detection; the allocation-heavy folder-owner executable passed **360 checks** outside CTest's fixed timeout, and the new observer suites passed **77/77** and **6/6** without sanitizer diagnostics.
- Exact rev0963 parent SHA-256 matched and the wrapper-aware parent verifier passed **41/41 checks**.
- Source patch reconstruction covers **5/5 changed active files** byte-for-byte and by mode.
- Active implementation projection: **567 files / 25687923 bytes**, SHA-256 `feb5974b52c3d85635a0019cb9a58f90748834a22ccf8782f5e5f5dcb0492a04`.
- Publication remains contingent on the exact manifest, wrapper-directory and ZIP verifiers, ZIP CRC/path/no-symlink policy, and clean-extraction path/byte/type/mode equality.

## Nonclaims

The entry count remains the first-pass asynchronous census for a directory
visit; namespace mutation during a sweep is repaired conservatively by later
epochs and watcher notifications. Recursive traversal can retain one bounded
batch per active depth. The full non-resumable observer still buffers a complete
immediate directory. No target-scale RSS/latency claim, durable metadata index,
skipped-prefix elimination, user version history, retention policy, restore,
or garbage collector is added.
