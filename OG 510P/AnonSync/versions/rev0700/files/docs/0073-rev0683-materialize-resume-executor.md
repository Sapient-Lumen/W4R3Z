# Rev0683 — materialize resume executor

## Scope of this linked revision

Rev0683 is code-bearing. It promotes a new active C++ executable:

- `bin/rev0683/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3`

Rev0682 turned checkpoint restart evidence into a read-only per-path action plan. Rev0683 executes exactly one branch of that plan: `MaterializeStagedFile`. It adds `execute_sync_session_checkpoint_resume_materializations`, a narrow recovery executor that consumes the action plan, rechecks staged bytes and receipt sidecars, atomically materializes verified staged files, and updates SQLite materialization evidence.

## Mission fit

AnonSync’s mission is evidence-bound peer-to-peer folder convergence. A restart path is only useful when it can move from inspection to safe mutation without trusting stale caller state. Rev0683 is the first such move after the action router: it does not resume transfer, cleanup, tombstone, or conflict work. It only turns a complete staged file plus complete receipt proof into a materialized destination file and a durable checkpoint transition.

The revised local proof path is now:

`source scan → destination scan → manifest diff → local apply plan → staged inspection → chunk request → peer schedule → peer-bound response batch → peer transfer round continuation → receipt-gated materialization → committed staging cleanup → destination rescan → content convergence → SQLite session checkpoint → manifest chunk-row persistence → read-only checkpoint verification → exact chunk receipt coverage guard → source filesystem probe → destination filesystem probe → staging cleanup probe → DB-bound terminal staging repair sweeper → read-only resume action plan router → MaterializeStagedFile resume executor`

## Public C++ surface

Rev0683 adds:

- `SyncSessionCheckpointMaterializeResumeOptions`
- `SyncSessionCheckpointMaterializeResumeFileResult`
- `SyncSessionCheckpointMaterializeResumeResult`
- `execute_sync_session_checkpoint_resume_materializations`

The executor deliberately uses the rev0682 action plan as its gate. It refuses unsafe `QuarantineStaging` or `RejectDrift` plans by default, skips non-materialization paths, and mutates only files already classified as `MaterializeStagedFile`.

## Audit/refactor performed

The audit finding was that rev0682 made restart actions explicit but still left `MaterializeStagedFile` as a recommendation. That meant a caller had to hand-roll the hardest part: revalidating receipts, moving the staged file, and updating SQLite evidence without accidentally materializing drifted or tampered content.

Rev0683 closes that slice by adding a recovery executor that:

1. loads `plan_sync_session_checkpoint_resume_actions` with durable checkpoint integrity and source filesystem proof;
2. opens the checkpoint database read/write only after reusing the same root and identity safety checks;
3. rechecks the staged file as a regular file with the checkpointed size and content hash;
4. rehashes every receipt sidecar against the persisted `sync-chunk-receipt:v1:` row before filesystem mutation;
5. rejects wrong-kind, tampered, missing, or unexpected staging evidence through the action-plan gate;
6. atomically renames the staged file into the destination when the target is absent;
7. idempotently finalizes SQLite materialization evidence when the destination target is already present with the expected content;
8. writes/refreshes the `sync_session_materialization_checkpoints` row with the same `sync-materialize:v1:` key shape used by normal materialization;
9. updates `sync_session_file_results` and aggregate checkpoint materialization counters; and
10. verifies the post-state has transitioned into `CleanupCommittedStaging`, leaving receipt cleanup to the existing cleanup/repair boundary.

The refactor also exposes a real schema ceiling: checkpoint apply intents do not yet persist local overwrite preflight size/hash/kind evidence. Therefore rev0683 supports the remote-only fetch materialization branch and fail-closes on overwrite replay until that evidence is durable.

## Selftest coverage added

`--selftest-sync-domain-model` now proves that the executor:

- starts from a DB-mutated `MaterializeStagedFile` action;
- still materializes when the destination target is absent but the staged file and all receipts are complete;
- performs an atomic rename from staging into the destination;
- writes exactly one file-result materialization update and one materialization checkpoint;
- leaves receipt cleanup pending instead of silently deleting sidecars; and
- transitions the path from `MaterializeStagedFile` to `CleanupCommittedStaging` after the executor commits.

Recorded result: `anonsync_core sync domain model selftest passed=226 failed=0`.

## Validation

The release CTest suite reports `100% tests passed, 0 tests failed out of 27`.

The focused sanitizer selftest reports `anonsync_core sync domain model selftest passed=226 failed=0`.

The package validator is:

```bash
python3 tools/validate_rev0683_materialize_resume_executor.py
```

## Remaining ceiling

Rev0683 is not a general restart engine. It does not resume transfer rounds, does not execute cleanup after materialization, does not reclaim worker ownership, and does not replay overwrite materializations because local preflight evidence is not yet fully persisted.

The next best move is either the `CleanupCommittedStaging` executor branch or a checkpoint schema extension that persists enough local preflight evidence to safely replay remote-file overwrites after restart.
