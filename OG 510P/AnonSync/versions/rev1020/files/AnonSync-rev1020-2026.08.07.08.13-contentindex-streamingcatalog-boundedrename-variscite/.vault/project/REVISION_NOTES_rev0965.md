# Revision notes — rev0965

The shipping resumable folder walk now releases a selected parent basename
batch before recursive descent and resumes the same open parent from the exact
processed component boundary.

## Mission move

Rev0964 bounded each immediate selected-name batch to 4,096, but recursive
descent could retain one full batch per active directory depth. Rev0965 turns
that per-frame limit into a traversal-wide selected-basename limit without
adding another scanner or changing durable scan ownership.

## C++ implementation

- Split the shared component walker into a classifier that stops at the first
  directory, descriptor-owning pending descent state, and one rooted descent /
  post-walk rebinding helper.
- Copies the selected child component and canonical path before opening the
  child, then owns the opened descriptor through `ScopedFd` so exceptions cannot
  leak it.
- Destroys the selected parent vector, including reserved capacity, before
  entering the child.
- Re-enumerates the same open parent strictly after the processed component,
  preserving component-wise bytewise preorder.
- Keeps the non-resumable complete observer on its existing whole-directory
  vector while sharing classification and directory-rebinding logic.
- Added exact live-batch accounting and
  `peak_simultaneously_buffered_directory_component_count`; the resumable loop
  requires zero live selected names before reserving another selector vector,
  the RAII owner rejects overlap again, and the public boundary proves the live
  count returns to zero.
- Preserves callback-before-cursor publication, rooted mount/path checks,
  directory identity reproof, namespace entry charging, and regular-file
  capacity semantics.

## Census-drift audit/refactor

The first charged directory census is now an exact suffix-cardinality fence on
every required later rescan. Before processing a rescan, its eligible component
count must match the unconsumed first-census count. Detected growth, shrinkage,
or a rename across the processed component boundary returns
`directory_census_frontier` and that inconsistent pass cannot grant completed-
epoch absence authority.

This tightened the older growth regression. An inconsistent rescan no longer
publishes an interleaved post-census name merely because one bounded slot is
available. The next segment starts at the last coherent cursor and discovers the
interleaved name, displaced original, and all appended suffixes exactly once.

## Mechanical regression

- A two-level fixture places a leading child plus 4,095 regular siblings at both
  levels and one deepest leaf: 8,191 regular files and 8,193 total entries.
- Exact preorder completes in five directory enumeration passes.
- Largest individual selected batch is 4,096.
- Largest simultaneous selected-name count is 4,096 rather than 8,192,
  proving ancestor batches do not multiply the bound by depth.
- A cross-boundary parent rename during child traversal returns the non-complete
  census frontier; a fresh epoch sees the moved path and child leaf in order.
- Focused observer checks increase from 77 in sealed rev0964 to 87.

## Adjacent contamination audit

An adjacent clean rebuild found an unrelated retained-version prototype in the
folder-owner header, implementation, test, and low-level replica CLI. All four
contaminated files were restored exactly from the verified rev0964 parent before
any authoritative validation. Only the intended observer files differed at the
implementation cutpoint.

A second cloudtainer audit removed an obsolete discarded-branch cleanup loop
whose broad pathname match terminated current rev0965 Ninja, CTest, and test
processes. The interrupted product invocations and one missing-object link are
excluded; the link and every affected test shard were rerun after process
quiescence.

## Validation

- Fresh GCC 14.2 Debug complete graph: **527/527 configured build edges**, followed by an exact-final-source **35/35-edge** delta rebuild and no-work bundled-SQLite profile re-attestation.
- Complete GCC registry: **258/258 tests** in bounded terminal shards, with the final documentation-sensitive structural audit rerun as registered test 123.
- Independent GCC product lane: **39/39 tests** in bounded serial shards.
- Focused GCC checks: **84** resumable SHA-256, **19** scrub-state, **26** verification-index, **576** payload-store, **30/30** rooted POSIX resolution, **92** network-model checks with **41** generated operations, **296** SQLite-owner, **360** folder-owner, **110** sync-once, **2,043** TLS, **17** integrity-evidence, **92** local-control, **87/87** folder-observer, and **6/6** observer-race checks.
- Structural payload-store/folder-traversal authority audit: **210/210 checks**.
- Fresh Clang 17 ASan/UBSan product dependency graph: **238/238 build edges**, followed by an exact-final-source **35/35-edge** delta rebuild and no-work re-attestation.
- Clang ASan/UBSan product set: **39/39 tests** with leak detection and UBSan halt-on-error. The allocation-heavy folder-owner executable passed **360 checks** outside CTest's fixed timeout at **1,311,404 KiB peak RSS**, and the focused observer suites passed **87/87** and **6/6**.
- Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic.
- Exact rev0964 parent SHA-256 matched and the wrapper-aware parent verifier passed **41/41 checks**.
- Source patch reconstruction covers **5/5 changed active files** byte-for-byte and by mode.
- Active implementation projection: **567 files / 25712778 bytes**, SHA-256 `c1fda16a5a848ed3da1ff8548f08cddb30fcde711da8b8e027afd1f12bfca35d`.
- Publication remains contingent on the exact manifest, wrapper-directory and ZIP verifiers, ZIP CRC/path/no-symlink policy, and clean-extraction path/byte/type/mode equality.

## Nonclaims

Selected basename storage is one bounded batch, but recursive traversal still
retains a depth-indexed set of descriptors and pending component/path records;
aggregate canonical-path bytes also depend on path lengths and are not a strict
O(depth)-byte claim. Releasing before child descent can add full parent
enumeration passes. The
non-resumable observer still materializes complete immediate directories.
Rev0965 does not add snapshot isolation, a durable subtree index, rename
identity, empty-directory synchronization, user-restorable history, garbage
collection, or huge-tree qualification.

See `GLOBAL_RESUMABLE_DIRECTORY_BATCH_LIFETIME_AUDIT_rev0965.md`.
