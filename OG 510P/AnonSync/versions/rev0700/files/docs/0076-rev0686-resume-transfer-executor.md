# Rev0686 — resume transfer fake-peer executor

## Scope of this linked revision

Rev0686 is code-bearing. It promotes a new active C++ executable:

- `bin/rev0686/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3`

Rev0685 converted `ResumeTransfer` / `RetryTransfer` restart state into deterministic peer-bound work orders. Rev0686 addresses the next restart boundary: a work order should be executable in the fake-peer/local-source harness without bypassing checkpoint evidence. The new `execute_sync_session_checkpoint_resume_transfer_workorders` function consumes the rev0685 planner, writes missing staged chunks from the verified source tree, records accepted receipt rows, and proves the file now routes to `MaterializeStagedFile`.

## Mission fit

AnonSync’s mission is evidence-bound peer-to-peer folder convergence. A restarted process should not only know that chunks are missing; it should have a safe path to rebuild staged receipt evidence and then hand off to the existing materialization executor. Rev0686 closes that local proof path for the fake-peer branch while still refusing to claim production transport, worker ownership, or daemon behavior.

The revised local proof path is now:

`source scan → destination scan → manifest diff → local apply plan → staged inspection → chunk request → peer schedule → peer-bound response batch → peer transfer round continuation → receipt-gated materialization → committed staging cleanup → destination rescan → content convergence → SQLite session checkpoint → manifest chunk-row persistence → read-only checkpoint verification → exact chunk receipt coverage guard → source filesystem probe → destination filesystem probe → staging cleanup probe → DB-bound terminal staging repair sweeper → read-only resume action plan router → MaterializeStagedFile resume executor → CleanupCommittedStaging resume executor → ResumeTransfer work-order planner → fake-peer ResumeTransfer executor`

## Public C++ surface

Rev0686 adds:

- `SyncSessionCheckpointResumeTransferExecutionOptions`
- `SyncSessionCheckpointResumeTransferFileExecutionResult`
- `SyncSessionCheckpointResumeTransferExecutionResult`
- `execute_sync_session_checkpoint_resume_transfer_workorders`

The executor is intentionally scoped to planned fake-peer transfer work. It does not invent missing chunks itself; it calls `plan_sync_session_checkpoint_resume_transfers` and only executes peer-assigned chunks from that proof.

## Audit/refactor performed

The audit finding was that rev0685 made transfer continuation explicit but inert. A caller could receive `sync-resume-transfer-request:v1:`, `sync-resume-peer-request:v1:`, and `sync-resume-peer-schedule:v1:` keys, but there was no typed function that consumed those keys and moved checkpoint state forward.

Rev0686 closes that slice by adding an executor that:

1. loads the rev0685 transfer plan and inherits its durable checkpoint/source-filesystem gates;
2. opens SQLite read/write only after DB path and root safety validation;
3. reloads source manifest rows and apply intent rows for each planned path;
4. verifies the persisted staging path matches the transfer plan;
5. verifies peer-assigned chunks are an ordered unique subset of source manifest chunks and requested work-order chunks;
6. reads exact byte ranges from the verified source file;
7. writes or reuses staged chunk bytes and `sync-chunk-receipt:v1:` sidecars under the verified staging root;
8. upserts `sync_session_chunk_receipts` rows as `accepted`;
9. updates transfer-round/chunk/receipt counters on `sync_session_file_results` and `sync_session_checkpoints`; and
10. re-runs the restart action planner to prove completed staged evidence now routes to `MaterializeStagedFile`.

This is still not a live network executor. It is the fake-peer restart mutation bridge that later real transport must match.

## Selftest coverage added

`--selftest-sync-domain-model` now proves that the executor:

- starts from a checkpoint row marked `materialized=0` / `staging_artifacts_cleaned=0` with missing staged sidecars;
- uses the transfer planner to select all missing chunks for one pending path;
- writes staged bytes equal to the source manifest size;
- emits a `sync-resume-transfer-execute:v1:` key;
- verifies source chunk rows before mutation;
- upserts accepted receipt rows for every manifest chunk;
- updates database transfer counters;
- verifies the completed staged file content hash after execution; and
- promotes the path from `ResumeTransfer` to `MaterializeStagedFile` in the post-execution action plan.

Recorded result: `anonsync_core sync domain model selftest passed=236 failed=0`.

## Validation

The release CTest suite reports `100% tests passed, 0 tests failed out of 27`.

The focused sanitizer selftest reports `anonsync_core sync domain model selftest passed=236 failed=0`.

The package validator is:

```bash
python3 tools/validate_rev0686_resume_transfer_executor.py
```

## Remaining ceiling

Rev0686 does not persist transfer work orders as scheduler-owned rows, claim or reclaim workers, send or receive real peer messages, attach cryptographic peer/session transport, handle overwrite replay evidence, execute tombstone/conflict branches, or define folder membership/trust policy. The next best move is to persist executable transfer work and model worker ownership/reclaim, then bind real peer response acceptance to the same staged receipt/checkpoint transition proven here.
