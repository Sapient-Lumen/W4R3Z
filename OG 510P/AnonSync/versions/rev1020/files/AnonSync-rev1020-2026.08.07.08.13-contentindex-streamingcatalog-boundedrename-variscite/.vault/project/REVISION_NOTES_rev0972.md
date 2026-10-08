# Revision notes — rev0972

## Product move

Rev0972 combines sealed rev0971's byte-bounded causal-history status with exact
share-level retained-payload reachability. Existing exact `versions` output now
classifies current visible, superseded active, inactive retained evidence,
deduplicated retained-union, missing, and unreferenced payload facts without a
second command or collector.

## C++ implementation

- Added fixed-schema reachability classes keyed by exact `(SHA-256, size)`
  identity.
- Reused exact history's complete payload snapshot and grouped active
  projection; no second payload observation is performed.
- Included every inactive retained file operation through one linear borrowed
  evidence visitor.
- Added exact entry, byte, and operation-reference partition checks before
  output.
- Added evidence-bound `v3:exact:<operations>:<evidence>:<payload>` source
  cutpoints with typed before/during evidence-drift stages.
- Retained compatible v1 exact decoding and unchanged v2 metadata tokens.
- Kept metadata browsing payload-cold with null evidence and reachability.
- Advanced service status to `anonsync.peer-service.status.v17` and the local
  history response to `anonsync.local-historical-versions.response.v5`.

## Adjacent audit/refactor

The merge exposed an incompatible sibling-schema collision: two branches had
independently assigned different payloads to service schema v16. Rev0972 resolves that collision with v17 rather than silently
reusing a versioned contract.

The initial merge also retained a second inline reachability serializer beside
rev0971's canonical counted history encoder. Rev0972 removes that drift and
capacity seam. Evidence and reachability fields now pass through the same stream
for exact 256 KiB counting and live/terminal emission. The expanded maximum-page
regression proves the combined v3/reachability object remains bounded and the
completed inventory still exists only once in stable status.

The status contract says `reclaimable_authority:false` and
`class_totals_overlap:true`. It measures reachability; it does not account for
catalogs, in-flight work, user pins, policy, grace, writer fencing, or a
crash-safe collector.

## Compatibility

- Existing `versions` request forms remain accepted.
- Exact callers may continue a legacy v1 token; successful output upgrades to
  evidence-bound v3.
- Metadata v2 tokens remain byte-for-byte unchanged.
- Default CLI behavior remains exact.
- No reconciliation wire-protocol generation changes.
- Consumers must opt into service status v17 because v16 had two incompatible
  sibling definitions before this merge.

## Validation

Exact rev0972 source passed the fresh GCC 14.2 Debug graph (528/528 configured build edges), all 258/258 registered tests, and an independent 39/39 product replay. Focused GCC suites passed 84 resumable-SHA-256, 19 scrub-state, 26 verification-index, 576 payload-store, 30/30 rooted-POSIX, 98 network-model plus 41 generated-operation, 296 SQLite-owner, 421 folder-owner, 110 sync-once, 2,043 TLS, 17 integrity-evidence, 132 local-control, 87/87 observer, and 6/6 observer-race checks. The structural authority audit passed 279/279 checks. A clean Clang 17 Debug product dependency graph completed 239/239 edges with ASan and UBSan; all 39/39 product tests passed with leak detection and halt-on-error. Focused sanitizer proof passed the 421-check folder-owner suite in 33.17 seconds at 1,376,128 KiB peak RSS and the 132-check local-control suite in 0.57 seconds at 91,608 KiB peak RSS. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0971 parent SHA-256 matched 7212288343824982bfc5c505cf32c39c9ec920d84850103daeafdbd8187f8c33 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 14/14 changed active files and the complete 570-file projection byte-for-byte and by mode. The final active implementation projection contains 570 files / 26,108,596 bytes with SHA-256 e226a95f2c0bf343ad4ff41353415686ea78bde24bcf3ea12c615eaac745d912. Validation also removed multiple orphaned divergent rev0972 build and prototype trees so only the sealed reachability/frontier source and its isolated build directories contributed release authority.

## Nonclaims

Rev0972 does not add garbage collection, quotas, retention expiry, durable pins,
Archive UI, chronological ordering, conflict browsing, batch restore, directory
restore, or remote transfer semantics for deliberately collected history.
