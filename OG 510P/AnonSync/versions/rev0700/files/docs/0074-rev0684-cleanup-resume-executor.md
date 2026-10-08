# Rev0684 — cleanup resume executor

## Scope of this linked revision

Rev0684 is code-bearing. It promotes a new active C++ executable:

- `bin/rev0684/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3`

Rev0683 executed the `MaterializeStagedFile` branch and deliberately left a materialized file in `CleanupCommittedStaging`. Rev0684 executes exactly that next branch. It adds `execute_sync_session_checkpoint_resume_cleanups`, a narrow recovery executor that consumes the action plan, rechecks destination content, removes only matching staged files and DB-bound receipt sidecars, updates SQLite cleanup evidence, and verifies the path returns to `AlreadyConverged`.

## Mission fit

AnonSync’s mission is evidence-bound peer-to-peer folder convergence. A restart executor must not merely make the destination bytes appear; it must also reconcile the staging evidence left behind so the next process sees one coherent terminal state. Rev0684 turns cleanup into an explicit, auditable recovery step instead of hiding it inside materialization or leaving it to ad hoc callers.

The revised local proof path is now:

`source scan → destination scan → manifest diff → local apply plan → staged inspection → chunk request → peer schedule → peer-bound response batch → peer transfer round continuation → receipt-gated materialization → committed staging cleanup → destination rescan → content convergence → SQLite session checkpoint → manifest chunk-row persistence → read-only checkpoint verification → exact chunk receipt coverage guard → source filesystem probe → destination filesystem probe → staging cleanup probe → DB-bound terminal staging repair sweeper → read-only resume action plan router → MaterializeStagedFile resume executor → CleanupCommittedStaging resume executor`

## Public C++ surface

Rev0684 adds:

- `SyncSessionCheckpointCleanupResumeOptions`
- `SyncSessionCheckpointCleanupResumeFileResult`
- `SyncSessionCheckpointCleanupResumeResult`
- `execute_sync_session_checkpoint_resume_cleanups`

The executor deliberately uses the rev0682 action plan as its gate. It refuses unsafe `QuarantineStaging` or `RejectDrift` plans by default, skips non-cleanup paths, and mutates only files already classified as `CleanupCommittedStaging`.

## Audit/refactor performed

The audit finding was that rev0683 correctly made materialization executable, but stopped at a half-terminal state: `materialized=1`, `staging_artifacts_cleaned=0`, and receipt rows still in `accepted` state. That was safe, but it meant a restarted caller still had to hand-roll receipt deletion and cleanup checkpoint updates.

Rev0684 closes that slice by adding a recovery executor that:

1. loads `plan_sync_session_checkpoint_resume_actions` with durable checkpoint integrity and source filesystem proof;
2. opens the checkpoint database read/write only after reusing the same root and identity safety checks;
3. rechecks the materialized destination target as a regular file with the checkpointed size and content hash;
4. verifies a leftover staged file before removing it, and only if it still matches checkpointed content;
5. rehashes every receipt sidecar against the persisted `sync-chunk-receipt:v1:` row before deletion;
6. refuses wrong-kind, tampered, missing-row, or unexpected receipt-directory artifacts;
7. reconstructs the same `sync-transfer-cleanup:v1:` key shape used by normal committed cleanup;
8. updates `sync_session_file_results`, `sync_session_cleanup_checkpoints`, and `sync_session_chunk_receipts` in one SQLite transaction;
9. refreshes aggregate checkpoint cleanup counters from cleanup checkpoint rows; and
10. verifies the post-state is `AlreadyConverged` and passes the strict terminal resume view.

The refactor also makes a clearer distinction between three cleanup states: pending cleanup after materialization, terminal cleanup repair for reappeared artifacts, and unsafe quarantine when artifact content no longer matches DB evidence.

## Selftest coverage added

`--selftest-sync-domain-model` now proves that the executor:

- starts from the `CleanupCommittedStaging` state produced by the materialization executor;
- can also remove a leftover staged file when the destination already contains matching terminal content;
- verifies and removes all DB-bound `sync-chunk-receipt:v1:` sidecars;
- updates receipt rows to `committed-cleaned`;
- writes/refreshes cleanup checkpoint rows with `sync-transfer-cleanup:v1:` keys;
- updates cleanup aggregate counters;
- returns all files to `AlreadyConverged`; and
- restores the strict terminal checkpoint resume view.

Recorded result: `anonsync_core sync domain model selftest passed=232 failed=0`.

## Validation

The release CTest suite reports `100% tests passed, 0 tests failed out of 27`.

The focused sanitizer selftest reports `anonsync_core sync domain model selftest passed=232 failed=0`.

The package validator is:

```bash
python3 tools/validate_rev0684_cleanup_resume_executor.py
```

## Remaining ceiling

Rev0684 is not a general restart engine. It does not resume partial transfers, persist in-flight request/schedule/batch rows, reclaim abandoned workers, or replay overwrite/tombstone/conflict branches.

The next best move is either an executable `ResumeTransfer` branch backed by durable request/schedule/batch state, or a checkpoint schema extension that persists enough local preflight evidence to safely replay remote-file overwrites after restart.
