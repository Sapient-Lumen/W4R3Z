# Revision notes — rev0989

## Summary

Rev0989 removes the remaining per-effect O(history) multiplier from
metadata-only selective-sync dematerialization. Planning, pre-unlink, and
post-unlink reproof no longer take complete replica snapshots or reconstruct the
complete causal model. Each boundary uses one transactionally pinned exact path
and operation cutpoint.

## C++ implementation

- Implemented `SyncReplicaSqliteOwner::targeted_path_cutpoint_or_throw()`.
- Reads the typed metadata row, at most two exact visible rows, the sole visible
  operation when present, and at most one distinct retained operation.
- Rejects conflicts rather than materializing a complete conflict projection.
- Verifies canonical operation bytes, IDs, redundant charges, sole-visible
  active state, folder/path binding, and visible flags.
- Reuses a sole-visible operation as the requested retained operation without a
  second potentially large envelope copy.
- Centralized complete and targeted operation decoding in
  `load_stored_operation_row_or_throw()`.
- Replaced three complete replica snapshots/model restores per successful
  metadata-only effect with three targeted replica cutpoints.
- Added `remote_targeted_replica_path_cutpoint_count` and shipping JSON field
  `remote_targeted_replica_path_cutpoints`.

## Adjacent audit/refactor

The first implementation exported stored global generation and digest fields
from a path-local read that did not recompute those aggregate facts. The
retained result now exposes only the exact operations it independently proves.
Each cutpoint also re-attests the exact trigger-free schema and foreign-key mode
inside the same pinned transaction; that fixed schema work is independent of
retained history and preserves current durable authority.

The production composition previously admitted 12,288 complete replica
snapshots/model restores in one 4,096-effect pass. At the 10,000-operation
model frontier, that could decode 122,880,000 retained operation rows before
causal-map reconstruction. The new per-effect path is independent of total
retained history, though complete snapshots remain intentionally global
planning and settlement authority.

## Runtime proof

The SQLite-owner test traces statements for sole-visible, conflict, absent,
cross-path, and unrelated-history cases. It proves one exact visible-path query,
one or two exact operation reads, zero complete visible or complete operation
projections, and exactly one schema-catalog plus one foreign-key-PRAGMA proof.
The folder-owner eight-file
regression proves 24 exact path and operation reads while complete projections
remain pass-bounded and all causal/catalog/private-payload semantics remain
intact.

## Authority boundary

The cutpoint is path-local. It does not recompute global digests, prove
unrelated evidence, replace complete snapshots, hold a writer transaction
across filesystem work, or qualify multi-terabyte RSS. Rooted observation,
private payload retention, causal supersession, atomic removal, and final
absence proof remain unchanged.

See
`TARGETED_REPLICA_PATH_OPERATION_CUTPOINT_AND_HISTORY_SCALE_AUDIT_rev0989.md`.

## Validation and archive

Exact rev0989 source passed the GCC 14.2 Debug complete graph in its 540-edge configured dependency state, followed by a no-work bundled-SQLite re-attestation, all 269/269 registered tests, and an independent 43/43 product replay. Focused GCC proofs passed 356 SQLite-owner checks and 536 folder-owner checks. Source audits passed 52/52 selective-sync checks, 24/24 targeted catalog-cutpoint checks, 30/30 targeted replica path-cutpoint checks, and 433/433 structural authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 251/251 edges; all 43/43 product tests passed with leak detection and halt-on-error, including direct 356-check SQLite-owner and 536-check folder-owner proofs. The sanitized folder-owner proof peaked at 1,664,276 KiB RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0988 parent SHA-256 matched 067de76a76061db941ebccde03821c84134428152784954a51feba153505d23d and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 13/13 changed active files and the complete 593-file projection byte-for-byte and by mode. The final active implementation projection contains 593 files / 27,588,416 bytes with SHA-256 195b1897e39b44b6f32d2838ee6eff35dc65849de7a3e2e70c6bb0882d43ea4a. The final wrapper directory and ZIP passed release-package verification, CRC integrity, canonical-path and no-symlink checks, and clean-extraction path/byte/type/mode equality.

`AnonSync-rev0989-2026.08.04.07.53-targetedreplica-historybounded-pathreproof-larimar.zip`
