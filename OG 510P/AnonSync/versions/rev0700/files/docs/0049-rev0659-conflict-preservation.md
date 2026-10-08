# rev0659 — C++ conflict-copy preservation

## Mission fit

AnonSync is a C++ peer-to-peer file synchronization product. Rev0659 keeps the mission concrete by executing the next planned local sync mutation after remote file materialization and remote tombstone application: conflict preservation.

A Resilio-style sync engine cannot treat concurrent edits as an overwrite race. When local and remote version lineages are concurrent, or when equal lineage carries divergent content, the local apply plan emits `PreserveConflictCopy`. Before rev0659 that was only a path-bearing intent. Rev0659 turns the regular-local-file case into a guarded C++ mutation: preserve the current local bytes at a deterministic conflict path, then apply the remote file or remote tombstone only after the local target still matches the manifest evidence.

## C++ changes

Rev0659 extends `cpp/anonsync_core/include/anonsync_core.hpp` and `cpp/anonsync_core/src/sync_domain.cpp`:

- `SyncConflictPreservationOptions` carries the local synchronized root and staging root.
- `SyncConflictPreservationResult` records the normalized path, target/staging/conflict-copy paths, `sync-conflict:v1:` idempotency evidence, target-preflight status, conflict-copy status, remote file/tombstone outcome, and verified remote file digest/chunk evidence.
- `apply_sync_conflict_preservation` validates a remote file or tombstone entry, requires a `RecordConflict`/`PreserveConflictCopy` apply entry, rechecks remote entry and publisher-neutral version digests, requires planned local regular-file evidence, verifies target and conflict-copy path binding, rejects symlink ancestors, preflights the current target, preserves the local file as a conflict copy, preflights the target again, and then applies the remote file or tombstone.
- `conflict_preservation_idempotency_key` binds remote entry digest, remote version digest, local apply intent key, path, target path, staging path, conflict-copy path, local entry digest, and local version digest.
- `preflight_conflict_target_state` and `ensure_conflict_copy_absent_or_matching` make conflict preservation fail closed before overwriting or deleting anything unexpected.
- `validate_local_apply_plan_shape` now treats `PreserveConflictCopy` entries as staging remote content only when the remote side is a file. This fixes file/delete conflicts, whose remote side is a tombstone and therefore carries no staging path.

## Audit/refactor finding

The audit finding for this turn is that rev0655 already planned conflict-copy paths, but no C++ function executed them. During implementation, a second issue surfaced: the local apply-plan shape validator treated every conflict as if it needed staged remote bytes. That was correct for file/file conflicts, but wrong for file/delete conflicts where the remote side is a tombstone.

Rev0659 fixes both:

- file/file conflicts now copy the planned local regular file to a deterministic conflict path, verify the staged remote file against manifest chunks/content, recheck the local target, and promote the remote file;
- file/delete conflicts now copy the planned local regular file to a deterministic conflict path, recheck the local target, and remove the original target to reflect the remote tombstone;
- file/delete conflict apply plans no longer fail shape validation for lacking a remote staging path.

## Safety properties added

- Conflict preservation is tied to a `RecordConflict`/`PreserveConflictCopy` plan, not raw caller-provided paths.
- The remote entry digest and publisher-neutral version digest are rechecked at the mutation boundary.
- The planned local target must still be a regular file whose current size and SHA-256 match the planned local evidence.
- The target is checked once before copying and again before applying the remote side.
- The conflict-copy path stays under the local root, must not cross symlink ancestors, and must differ from the target path.
- Existing conflict copies are reused only when their bytes already match the planned local file evidence.
- Staged remote files are verified against chunk and content hashes before promotion.
- Remote tombstone conflicts remove the original target only after local conflict-copy preservation succeeds.
- Conflict commit evidence receives a dedicated `sync-conflict:v1:` namespace.

## Validation

Release validation was rerun after the conflict preservation changes:

```text
100% tests passed, 0 tests failed out of 27
```

The sync-domain selftest now reports:

```text
anonsync_core sync domain model selftest passed=103 failed=0
```

A narrow AddressSanitizer/UndefinedBehaviorSanitizer build of `sync_domain.cpp` plus the sync-domain harness also passed with the same selftest summary. Full CMake sanitizer coverage remains heavy because older non-sync translation units are large; rev0659 records the narrow sanitizer scope explicitly.

The package validator is `tools/validate_rev0659_conflict_preservation.py`.

## What this still does not prove

Rev0659 does not implement peer chunk receipt, partial-file transfer resume, crash cleanup of orphan `.part` files, persisted conflict metadata, local-tombstone vs remote-file conflict execution, authenticated manifest exchange, LAN/WAN discovery, NAT traversal, or a long-running daemon.

The next code-bearing seam should add chunk receipt/write accounting and transfer resume, or persist the manifest/index state that these local mutations need for restart recovery.
