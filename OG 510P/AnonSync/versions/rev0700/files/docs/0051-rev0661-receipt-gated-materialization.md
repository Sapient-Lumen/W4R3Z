# rev0661 — C++ receipt-gated materialization

## Mission fit

AnonSync is a C++ peer-to-peer file synchronization product. Rev0661 tightens the handoff between resumable chunk transfer and local filesystem mutation: a staged remote file can now be required to prove that every manifest chunk was durably received through AnonSync's chunk receipt boundary before the file is renamed into the synchronized folder.

This keeps the Resilio-style local sync path honest. Rev0660 introduced receipt-backed staged chunk writes, but the final materialization function could still accept a complete `.part` file that appeared in staging without consulting those receipts. That was useful for trusted bulk test fixtures, but it left no C++ switch for callers that want a chunk-transfer-only commit gate. Rev0661 adds that switch and covers both normal remote-file materialization and file/file conflict preservation.

## C++ changes

Rev0661 extends `cpp/anonsync_core/include/anonsync_core.hpp` and `cpp/anonsync_core/src/sync_domain.cpp`:

- `SyncStagedFileMaterializationOptions` gains `require_chunk_receipts`.
- `SyncStagedFileMaterializationResult` gains `chunk_receipts_checked`.
- `SyncConflictPreservationOptions` gains `require_chunk_receipts`.
- `SyncConflictPreservationResult` gains `chunk_receipts_checked`.
- `materialize_staged_sync_file` now uses `verify_staged_file_complete_with_receipts_or_throw` when receipt gating is required; otherwise it preserves the older trusted complete-file verification path.
- `apply_sync_conflict_preservation` applies the same receipt-gated verification before promoting a remote file version over a preserved local conflict copy.
- The sync-domain selftest now rejects complete staged bytes that lack chunk receipts when receipt gating is enabled, then proves that out-of-order receipt-backed chunks can be materialized and that conflict preservation can require receipts before promotion.

## Audit/refactor finding

The audit finding for this turn is that rev0660 had two adjacent notions of “complete”:

1. `write_sync_staged_chunk` could declare a staged file complete only after every chunk receipt and staged byte verified.
2. `materialize_staged_sync_file` and remote-file conflict preservation could still accept any complete staged file whose bytes matched the manifest.

Matching bytes are still necessary, but for a resumable peer transfer they are not the whole evidence story. A chunk scheduler needs to know that the staged file came through the planned chunk receipt path, not through an untracked side write. Rev0661 fixes that by making receipt evidence a selectable precondition at the final rename/promotion boundary.

## Safety properties added

- Receipt-gated materialization fails if any manifest chunk receipt is missing or mismatched.
- Receipt-gated materialization still verifies the whole staged file against chunk hashes and content SHA-256 before rename.
- The receipt gate reuses the remote entry digest, publisher-neutral version digest, apply intent key, path, staging path, offset, length, and chunk SHA-256 material from rev0660 receipts.
- A complete but unreceipted staged file remains in staging and is not committed when the gate is enabled.
- Conflict preservation can now require receipts before replacing the local target with the remote conflict version after the local conflict copy is preserved.
- The older complete-file path remains available for trusted bulk staging/test flows by leaving `require_chunk_receipts` false.

## Validation

Release-O0 CTest passed for the active C++ binary:

```text
100% tests passed, 0 tests failed out of 27
```

The sync-domain selftest now reports:

```text
anonsync_core sync domain model selftest passed=134 failed=0
```

A narrow ASAN/UBSAN sync-domain binary also passed the same selftest:

```text
anonsync_core sync domain model selftest passed=134 failed=0
```

The package validator is `tools/validate_rev0661_receipt_gated_materialization.py`.

## What this still does not prove

Rev0661 does not persist transfer state across daemon restart, schedule peer chunk requests, clean up orphan `.part` or `.chunks` directories after successful materialization, delete receipt sidecars after commit, exchange manifests with peers, authenticate a real transport, execute local-tombstone conflict semantics, or run as a full sync daemon.

The next code-bearing seam should add transfer cleanup/garbage collection, persisted transfer state, or a fake authenticated peer-session harness that drives manifest exchange, chunk receipt writes, receipt-gated materialization, tombstone application, and conflict preservation end-to-end.
