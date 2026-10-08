# Revision notes — rev0991

## Parent and lineage

Rev0991 is based directly on the exact sealed rev0989 release. No rev0990
archive is part of release lineage: the previously displayed rev0990 link was
not retained or uploaded and is therefore not used as source, validation, or
package authority.

## Summary

Rev0991 removes the complete-replica rebuild from the normal prepared local-file
publication path. Replica SQLite schema v8 adds a canonical operation-path index,
fixed-width counted commutative witnesses for active operations, complete
evidence, and visible paths, plus an exact visible-path cardinality. Preparation
and commit now operate on target-path history and the active causal frontier,
allowing unrelated progress while rejecting same-path drift.

## C++ implementation

- Added `sync_replica_digest_accumulator.{hpp,cpp}` with canonical 256-bit
  addition and subtraction modulo 2^256.
- Added domain-separated element witnesses and complete-model recomputation for
  active operations, retained evidence, and visible-path projections.
- Raised the durable replica schema from v7 to v8.
- Added `sync_replica_operation_paths` and its canonical path index.
- Added `visible_path_count_be` and incrementally maintained counted witnesses.
- Preserved complete reconstruction and migration from every released schema
  v1 through v7.
- Refactored local operation construction so the public model and SQLite owner
  share the exact causal-head derivation.
- Added target-path history, active-head, local-chain, policy, and schema
  publication cutpoints.
- Added a complete-model fallback when an existing pending child references the
  future local operation ID.
- Rejects executable TEMP triggers before the targeted writer's first effect.

## Adjacent audit/refactor

The original idempotent retry shortcut could return `AlreadyPublished` for an
identical local operation after a same-dot fork had quarantined that operation
and compromised the local actor. The retained implementation now requires the
existing operation to remain active and the actor uncompromised. A no-effect
regression proves the exact retry fails closed after the fork.

The fixed-width accumulator test also now covers exact carry and borrow across
the modulo-2^256 boundary.

## Scale and authority boundary

A 4,096-file scan segment against a 10,000-operation frontier previously
admitted 8,192 complete model rebuilds and 81,920,000 prior operation-row
decodes. The normal path is now O(history-of-that-path + active causal heads),
not O(total retained history) for every local file.

The new additive witnesses are unkeyed structural evidence, not authentication
authority or a cryptographic set commitment. Complete database observation,
canonical operation validation, authenticated envelopes, and migration/restore
recomputation remain authoritative.

See
`TARGETED_LOCAL_PUBLICATION_AND_INCREMENTAL_REPLICA_WITNESS_AUDIT_rev0991.md`.

## Validation

Exact rev0991 source passed the GCC 14.2 Debug complete graph across its 470-edge exact-change dependency state, followed by a no-work bundled-SQLite re-attestation, all 270/270 registered tests, and an independent 43/43 product replay. Focused GCC proofs passed 1,291 hash-graph, 238 prepared-publication, 361 SQLite-owner, and 536 folder-owner checks. Source audits passed 43/43 SQLite-owner, 30/30 targeted local-publication, and 442/442 structural authority checks. A fresh Clang 17 Debug AddressSanitizer/UndefinedBehaviorSanitizer product graph completed 252/252 edges; all 43/43 product tests passed with leak detection and halt-on-error. Direct sanitizer proofs passed the same 1,291, 238, 361, and 536 checks; the folder-owner proof peaked at 1,688,812 KiB RSS. Aggregate authoritative-log inspection found no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0989 parent SHA-256 matched 9af82eab8ce067088e65bf1ca165eb099967b72e18fde3660767454374a9387e and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 14/14 changed active files and the complete 596-file projection byte-for-byte and by mode. The final active implementation projection contains 596 files / 27,719,683 bytes with SHA-256 25888965fb9c560846cb528617655c38586f80dd9e27f2c3538baecb83f696b3. The final wrapper directory and ZIP passed release-package verification, CRC integrity, canonical-path and no-symlink checks, and clean-extraction path/byte/type/mode equality.

## Archive

AnonSync-rev0991-2026.08.04.11.50-countedwitness-targetedpublication-quarantinefence-spessartine.zip
