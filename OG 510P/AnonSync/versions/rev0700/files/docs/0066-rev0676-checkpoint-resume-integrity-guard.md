# Rev0676 — checkpoint resume integrity guard

## Scope of this linked revision

Rev0676 is code-bearing. It promotes a new active C++ executable:

- `bin/rev0676/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3`

Rev0675 could reopen a completed sync-session checkpoint as restart input, but its read path was still too trusting: a resumed process could see terminal-looking aggregate rows without proving that the manifest rows, manifest-entry rows, file-result aggregates, cleanup rows, and chunk receipt totals were mutually consistent. Rev0676 tightens that boundary.

## Mission fit

The heart of AnonSync is still evidence-bound peer-to-peer folder convergence. A restart reader must not merely report that a checkpoint says “done”; it must prove that the durable evidence tables agree before that state can be used as restart input.

The revised local proof path is now:

`source scan → destination scan → manifest diff → local apply plan → staged inspection → chunk request → peer schedule → peer-bound response batch → peer transfer round continuation → receipt-gated materialization → committed staging cleanup → destination rescan → content convergence → SQLite session checkpoint → read-only checkpoint verification → read-only resume view → durable cross-table integrity guard`

## Public C++ surface

Rev0676 extends:

- `SyncSessionCheckpointResumeViewOptions`
- `SyncSessionCheckpointResumeViewResult`
- `load_sync_session_checkpoint_resume_view`

New option:

- `require_durable_integrity` defaults to `true`.

New result evidence includes:

- `schema_version`
- `schema_version_supported`
- `manifest_digest_rows_verified`
- `manifest_entry_rows_verified`
- `file_result_aggregates_verified`
- `chunk_receipt_totals_verified`
- `durable_integrity_verified`
- actual manifest-entry row counts for source/destination-before/destination-after
- source manifest chunk-count evidence used to cross-check chunk receipt rows

## Audit/refactor performed

The audit finding was that rev0675 created a typed resume reader, but the reader did not yet defend enough against internally inconsistent durable state. The checkpoint writer stores multiple related tables; the resume reader therefore needs to validate the relationship between those tables before returning terminal restart evidence.

Rev0676 changes that by:

1. reading and validating checkpoint schema metadata;
2. verifying that source, destination-before, and destination-after manifest digest rows match the checkpoint row digests;
3. comparing manifest `entry_count` declarations with actual manifest-entry rows;
4. summing file-result transfer rounds, chunks, reused receipts, and materialized bytes back to the checkpoint totals;
5. summing cleanup checkpoint receipts/directories back to the checkpoint totals;
6. comparing source manifest chunk-count evidence with recorded chunk receipt rows;
7. folding those checks into `durable_integrity_verified`; and
8. requiring durable integrity, by default, before `terminal_session_complete` can be true.

This is a restart-safety refactor, not a transport or scheduler expansion. It makes the existing checkpoint/resume seam more trustworthy before building executable recovery on top of it.

## Selftest coverage added

`--selftest-sync-domain-model` now requires the two-file fake peer session resume view to prove:

- supported checkpoint schema metadata;
- manifest digest row consistency;
- manifest entry-count row consistency;
- file-result aggregate consistency;
- chunk receipt total consistency;
- `durable_integrity_verified`; and
- terminal completion only after the durable integrity guard passes.

The selftest also mutates the persisted source manifest `entry_count` in SQLite and verifies that the resume integrity guard rejects the checkpoint.

Recorded result: `anonsync_core sync domain model selftest passed=203 failed=0`.

## Validation

The release CTest suite reports `100% tests passed, 0 tests failed out of 27`.

The focused sanitizer selftest reports `anonsync_core sync domain model selftest passed=203 failed=0`.

The package validator is:

```bash
python3 tools/validate_rev0676_checkpoint_resume_integrity_guard.py
```

## Remaining ceiling

Rev0676 still does not execute recovery from checkpoint rows. It verifies that terminal restart input is internally coherent, but it does not persist in-flight request plans, peer schedules, accepted response batches, retry ownership, abandoned-transfer cleanup policy, tombstone/conflict branches inside the fake session, peer/folder trust material, authenticated transport, resource governance, or metadata/privacy policy.

The next best move is to make the resume view actionable for non-terminal state: persist request/schedule/batch rows before every transfer round, reconstruct pending staged transfers by combining SQLite rows with filesystem inspection, and then apply deterministic retry/cleanup policy.
