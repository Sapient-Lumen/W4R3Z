# Rev0688 — durable resume transfer workorder lease

Rev0688 is code-bearing. It addresses the highest-risk seam left by rev0687: the restart-cycle executor could drain transfer/materialization/cleanup branches, but the transfer branch still recomputed work orders at execution time. That made the fake-peer resume executor useful, but not yet scheduler-shaped.

The new slice adds a SQLite-backed transfer workorder/lease boundary to the fake-peer resume executor. `execute_sync_session_checkpoint_resume_transfer_workorders` now claims each assigned source-manifest chunk into `sync_session_resume_transfer_workorders` before the chunk write path, records worker identity and a deterministic lease id, then marks the row completed after staged bytes and receipt rows are written and verified.

## Active binary

- `bin/rev0688/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3`

## Mission thread

`source scan → destination scan → manifest diff → local apply plan → staged inspection → chunk request → peer schedule → peer-bound response batch → peer transfer round continuation → receipt-gated materialization → committed staging cleanup → destination rescan → content convergence → SQLite session checkpoint → manifest chunk-row persistence → read-only checkpoint verification → exact chunk receipt coverage guard → source filesystem probe → destination filesystem probe → staging cleanup probe → DB-bound terminal staging repair sweeper → read-only resume action plan router → MaterializeStagedFile resume executor → CleanupCommittedStaging resume executor → ResumeTransfer work-order planner → fake-peer ResumeTransfer executor → bounded resume-cycle drain executor → durable worker-owned resume transfer workorder rows`

## Public/API changes

Rev0688 extends the existing transfer executor option/result structs rather than adding a parallel scheduler API:

- `SyncSessionCheckpointResumeTransferExecutionOptions::worker_id`
- `SyncSessionCheckpointResumeTransferExecutionOptions::worker_lease_epoch`
- `SyncSessionCheckpointResumeTransferExecutionOptions::persist_workorder_claims`
- `SyncSessionCheckpointResumeTransferExecutionResult::worker_id`
- `SyncSessionCheckpointResumeTransferExecutionResult::worker_lease_id`
- `SyncSessionCheckpointResumeTransferExecutionResult::workorder_rows_claimed`
- `SyncSessionCheckpointResumeTransferExecutionResult::workorder_rows_completed`
- per-file worker/lease/claim/completion counters in `SyncSessionCheckpointResumeTransferFileExecutionResult`
- cycle-level `transfer_workorder_rows_claimed` and `transfer_workorder_rows_completed`

## Durable schema change

Checkpoint schema metadata advances to `rev0688-sync-session-checkpoint-v3` and adds:

- `sync_session_resume_transfer_workorders`

Each row is keyed by `(session_id, path, chunk_offset)`, foreign-keyed to source manifest chunk evidence and apply intent evidence, and stores:

- source role/path/chunk offset/length/hash
- source action: `resume-transfer` or `retry-transfer`
- request, peer request, schedule, and execution idempotency keys
- peer id and peer session id
- worker id, worker lease id, and lease epoch
- work state: `claimed` or `completed`
- absolute staging path evidence

This remains deliberately local. It does not yet implement multi-process lock expiration, clock-based lease TTL, or remote transport. It creates the durable row shape needed for those policies without relaxing any existing filesystem or checkpoint guards.

## Audit/refactor note

The refactor keeps transfer execution delegated through the existing action planner and fake-peer executor. The new worker lease is deterministic and evidence-bound: if `worker_id` is omitted, the executor uses `<session_id>-worker`; otherwise the supplied id must be a portable lowercase sync id. The lease id is derived from session id, worker id, peer id, peer session id, and `worker_lease_epoch`.

The executor only marks a workorder completed after:

1. assigned chunks are proven to be source-manifest rows;
2. source file bytes are read and hash-checked against the manifest chunk;
3. staged bytes are written or existing matching receipts are reused;
4. receipt rows are upserted; and
5. the corresponding claimed workorder row is updated from `claimed` to `completed`.

## Validation

Recorded rev0688 validation:

```bash
python3 tools/validate_rev0688_resume_workorder_lease.py
```

- `audit/logs/rev0688-release-ctest.log` records `100% tests passed, 0 tests failed out of 27`.
- `audit/logs/rev0688-resume-workorder-lease-selftest.log` records `anonsync_core sync domain model selftest passed=238 failed=0`.
- `audit/logs/rev0688-asan-ubsan-sync-domain-selftest.log` records `anonsync_core sync domain model selftest passed=238 failed=0` under an AddressSanitizer/UndefinedBehaviorSanitizer debug build with leak detection disabled.
- `audit/logs/rev0688-binary-sha256.txt` binds the promoted active executable.

## Remaining ceiling

Rev0688 persists worker-owned completed workorder rows, but it still executes those rows immediately in the deterministic fake-peer branch. The next best move is to split workorder claiming from execution, add reclaim/abandon/quarantine semantics for rows left in `claimed`, and then bind production peer response acceptance to those claimed rows without using source-root shortcuts.
