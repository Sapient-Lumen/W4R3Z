# Revision notes — rev0983

## Offline database replacement

- Added `anonsync_sync database-recovery-replace --manifest ABSOLUTE_JSON --snapshot ABSOLUTE_SQLITE --rollback ABSOLUTE_SQLITE --expected-current v1:INCARNATION:EPOCH:CUTPOINT`.
- Added a separate `SyncReplicaDatabaseReplacementOwner`; the immutable backup
  creator remains non-restoring.
- Validates and retains the detached candidate before any mutation.
- Requires an exact current active-database expectation.
- Preserves the displaced logical primary replica database as a private,
  sidecar-free, create-new rollback artifact.
- Replaces the active logical database through SQLite's own destination write
  transaction under the existing descriptor-rooted operational VFS.
- Re-proves the restored candidate, advances recovery epoch and state generation,
  closes the writer, and independently reopens the deployment before success.
- Does not touch payload bytes, the folder catalog, membership, effects, anchors,
  synchronized files, or networking.

## Audit/refactor

- Corrected artifact namespace authority from main-name comparison to the
  complete deterministic SQLite family: main, `-journal`, `-wal`, and `-shm`.
- Requires candidate and rollback families to be disjoint and excludes every
  family member from the deployment manifest, every active SQLite family,
  payload storage, and synchronized roots.
- Preflights the complete create-new output family before expensive resident
  capture and repeats that proof at the last non-mutating cutpoint before main
  publication. This denies deterministic sidecar conflicts without claiming an
  atomic four-name reservation against a concurrent hostile writer.
- Generalized the single bounded SQLite live-copy implementation to support an
  existing named writable destination without adding another raw backup loop.
- Added exact page-size preflight for WAL replacement destinations.
- Added rollback-on-injected-interruption, successful named replacement,
  read-only, private-destination, and page-size-mismatch focused regressions.
- Removed the terminal `SQLITE_DONE` step from the throwable observer surface.
  SQLite has already completed the named-destination transaction at that
  cutpoint; hooks now run only between nonterminal copy effects, and a one-step
  named-replacement regression proves that callback failure cannot be reported
  after committed mutation.
- Centralized backup/replacement artifact path validation, detached attestation,
  compact cutpoint projection, and seal policy in one internal helper.
- Expanded the real process recovery oracle from 265 to 381 checks, including
  complete artifact-family/root exclusion, deterministic output-sidecar
  denial before main publication, stale-current rejection with no rollback
  publication, exact displaced-state preservation, active replacement, mandatory
  epoch advancement, and detached rollback inspection.

## Boundary

The rollback artifact is a canonical logical SQLite snapshot, not raw main/WAL/
SHM inode identity. A crash after logical replacement but before epoch advance
still requires the existing offline inspection/advance ceremony; rev0983 does
not claim a durable external action receipt. This remains a primary-replica
recovery slice, not a whole-share backup or restore.

## Validation

Exact rev0983 active source passed the fresh GCC 14.2 Debug graph (535/535 configured build edges), all 262/262 registered tests in an indexed final-source replay, and an independent 41/41 product replay. Focused GCC proofs passed 334 SQLite-owner checks, 38 deployment-binding checks, 102 snapshot-seal checks, 53 SQLite live-backup/replacement checks, and the 381-check real database backup, recovery, and replacement process oracle. Source audits passed 28/28 database-backup checks, 28/28 database-replacement checks, 26/26 SQLite live-backup checks, and 402/402 structural authority checks. The fresh Clang 17 Debug product dependency graph completed 246/246 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 41/41 product tests passed in bounded exact-source shards with leak detection and halt-on-error, and focused sanitized proofs passed the same 334, 38, 102, and 53 checks. Aggregate retained-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0982 parent SHA-256 matched 41ce680f8a8b2cfc0cbf53e9be7379bab5460424da1fb0b20a721445222e48b2 and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 15/15 changed active files and the complete 581-file projection byte-for-byte and by mode. The final active implementation projection contains 581 files / 27,002,934 bytes with SHA-256 819d8a6650843ecb0e3fe795e37eb69bc23449e308111f5c0f604954bdb62d3b. Validation excluded the divergent integrated branch, orphaned validators, vanished build trees, interrupted nonterminal runs, and every result not bound to the reconstructed exact source. The final wrapper directory and ZIP remain publication-gated on the release manifest, package verification, CRC integrity, canonical paths, absence of symlinks, and clean-extraction path/byte/type/mode equality.

## Intended archive

AnonSync-rev0983-2026.08.03.06.40-logicalreplace-familyfence-rollbackproof-andalusite.zip
