# Rev0677 — manifest chunk coverage guard

## Scope of this linked revision

Rev0677 is code-bearing. It promotes a new active C++ executable:

- `bin/rev0677/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3`

Rev0676 made completed checkpoint resume views prove durable cross-table integrity, but the chunk proof still had an aggregate-only weak point: the reader compared source manifest chunk counts to committed receipt counts without proving that every receipt matched a specific source-manifest chunk by path, offset, length, and hash. Rev0677 closes that gap.

## Mission fit

The heart of AnonSync is evidence-bound peer-to-peer folder convergence. A restart reader should not treat “the right number of receipts exists” as equivalent to “the right chunks were received.” Restart evidence has to bind received chunks back to the exact source manifest that justified the transfer.

The revised local proof path is now:

`source scan → destination scan → manifest diff → local apply plan → staged inspection → chunk request → peer schedule → peer-bound response batch → peer transfer round continuation → receipt-gated materialization → committed staging cleanup → destination rescan → content convergence → SQLite session checkpoint → manifest chunk-row persistence → read-only checkpoint verification → exact chunk receipt coverage guard → read-only resume view`

## Public C++ surface

Rev0677 extends:

- `SyncSessionCheckpointResult`
- `SyncSessionCheckpointResumeViewResult`
- `persist_sync_fake_peer_session_checkpoint`
- `load_sync_session_checkpoint_resume_view`

New checkpoint result evidence includes:

- `source_manifest_chunks_written`
- `destination_before_manifest_chunks_written`
- `destination_after_manifest_chunks_written`

New resume view evidence includes:

- `manifest_chunk_rows_verified`
- `chunk_receipt_coverage_verified`
- `destination_before_manifest_chunks_recorded`
- `destination_after_manifest_chunks_recorded`
- `source_manifest_chunk_rows_recorded`
- `destination_before_manifest_chunk_rows_recorded`
- `destination_after_manifest_chunk_rows_recorded`
- `source_manifest_chunks_without_receipts`
- `chunk_receipts_without_source_manifest_chunks`

The SQLite checkpoint schema now writes `rev0677-sync-session-checkpoint-v2` and adds `sync_session_manifest_chunks`. The reader still recognizes the older v1 schema as a known historical schema, but durable integrity defaults to false for aggregate-only v1 checkpoints because exact manifest chunk coverage cannot be proven without persisted chunk rows.

## Audit/refactor performed

The audit finding was that rev0676 was directionally correct but still accepted a receipt table by count. A corrupted checkpoint could keep the same total number of receipt rows while altering a receipt path, offset, length, or hash. That would be invisible to a count-only guard.

Rev0677 changes that by:

1. adding the `sync_session_manifest_chunks` table with one row per manifest chunk;
2. persisting chunk rows for source, destination-before, and destination-after manifests;
3. promoting the checkpoint schema marker to `rev0677-sync-session-checkpoint-v2`;
4. exposing manifest chunk-row counts in checkpoint and resume results;
5. verifying each manifest role's declared chunk count against actual chunk rows;
6. proving every source manifest chunk has a matching committed receipt row by path, offset, length, and hash;
7. proving every committed receipt row maps back to a source manifest chunk; and
8. folding exact chunk coverage into `durable_integrity_verified`.

This is a restart-safety refactor. It narrows what can be trusted after a crash before building executable resume/retry behavior on top of the checkpoint database.

## Selftest coverage added

`--selftest-sync-domain-model` now requires the two-file fake peer session resume view to prove:

- schema marker `rev0677-sync-session-checkpoint-v2`;
- manifest digest row consistency;
- manifest entry-count row consistency;
- manifest chunk-row count consistency;
- file-result aggregate consistency;
- chunk receipt total consistency;
- exact chunk receipt coverage by path, offset, length, and hash;
- zero source chunks without receipts;
- zero receipts without source manifest chunks; and
- `durable_integrity_verified` before terminal completion is trusted.

The selftest mutates one persisted receipt hash and verifies that `load_sync_session_checkpoint_resume_view` rejects the checkpoint. It then rewrites the checkpoint and repeats the rev0676 manifest entry-count corruption test.

Recorded result: `anonsync_core sync domain model selftest passed=205 failed=0`.

## Validation

The release CTest suite reports `100% tests passed, 0 tests failed out of 27`.

The focused sanitizer selftest reports `anonsync_core sync domain model selftest passed=205 failed=0`.

The package validator is:

```bash
python3 tools/validate_rev0677_manifest_chunk_coverage_guard.py
```

## Remaining ceiling

Rev0677 still does not execute recovery from checkpoint rows. It makes completed checkpoint evidence harder to spoof, but it does not persist request-plan rows, peer schedule rows, accepted response batches, retry ownership, cleanup transitions before and after filesystem mutation, tombstone/conflict branches inside the fake session, peer/folder trust material, authenticated transport, resource governance, or metadata/privacy policy.

The next best move is actionable non-terminal restart: persist request/schedule/batch rows before each transfer round, reconstruct pending staged transfers by combining SQLite rows with filesystem inspection, and then apply deterministic retry and cleanup policy.
