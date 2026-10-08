# Rev0685 — resume transfer work-order planner

## Scope of this linked revision

Rev0685 is code-bearing. It promotes a new active C++ executable:

- `bin/rev0685/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3`

Rev0684 executed the `CleanupCommittedStaging` branch. Rev0685 addresses the next restart boundary: the action router can classify partial or missing staged transfer evidence as `ResumeTransfer`, but callers still had to hand-roll missing-chunk request and peer-schedule work. Rev0685 adds `plan_sync_session_checkpoint_resume_transfers`, a read-only bridge from restart classification to peer-bound transfer work orders.

## Mission fit

AnonSync’s mission is evidence-bound peer-to-peer folder convergence. A restarted process should not merely learn that a file needs transfer continuation; it should receive a bounded, deterministic, peer-bound work order that names exactly which manifest chunks may be requested next. Rev0685 keeps that boundary read-only so transfer execution and durable worker ownership can be added without weakening the existing materialization/cleanup proof path.

The revised local proof path is now:

`source scan → destination scan → manifest diff → local apply plan → staged inspection → chunk request → peer schedule → peer-bound response batch → peer transfer round continuation → receipt-gated materialization → committed staging cleanup → destination rescan → content convergence → SQLite session checkpoint → manifest chunk-row persistence → read-only checkpoint verification → exact chunk receipt coverage guard → source filesystem probe → destination filesystem probe → staging cleanup probe → DB-bound terminal staging repair sweeper → read-only resume action plan router → MaterializeStagedFile resume executor → CleanupCommittedStaging resume executor → ResumeTransfer work-order planner`

## Public C++ surface

Rev0685 adds:

- `SyncSessionCheckpointResumeTransferPlanOptions`
- `SyncSessionCheckpointResumeTransferFilePlan`
- `SyncSessionCheckpointResumeTransferPlanResult`
- `plan_sync_session_checkpoint_resume_transfers`

The planner consumes `plan_sync_session_checkpoint_resume_actions`, selects `ResumeTransfer` / optional `RetryTransfer` paths, and emits peer-bound missing-chunk work. It does not mutate SQLite, write staged files, remove artifacts, fetch bytes, or send network messages.

## Audit/refactor performed

The audit finding was that rev0684 made restart cleanup executable, but the transfer branch remained an under-specified label. `SyncSessionCheckpointResumeActionFilePlan::chunks_to_request` contained useful evidence, but the next caller still had to invent request IDs, schedule IDs, peer IDs, and budget behavior.

Rev0685 closes that slice by adding a recovery planner that:

1. loads `plan_sync_session_checkpoint_resume_actions` with durable checkpoint integrity and source filesystem proof;
2. rejects quarantine/reject action plans by default;
3. opens the checkpoint database read-only only after root and DB-path safety checks;
4. reloads apply intent evidence for `fetch_remote_file` / `stage_remote_file` paths;
5. verifies the persisted apply staging path still matches the action-plan staging path;
6. selects missing chunks with `max_chunks_per_request` and `max_bytes_per_request` limits;
7. assigns one peer work slice with `max_chunks_per_peer_round` and `max_bytes_per_peer_round` limits;
8. emits deferred chunks when either request or peer-round budgets leave remaining work;
9. binds request work to `sync-resume-transfer-request:v1:` keys; and
10. binds peer work to `sync-resume-peer-request:v1:` and `sync-resume-peer-schedule:v1:` keys.

This is not a live transfer executor. It is the restart work-order seam that a future durable scheduler and byte-acceptance executor should consume.

## Selftest coverage added

`--selftest-sync-domain-model` now proves that the planner:

- can start from a checkpoint row marked `materialized=0` / `staging_artifacts_cleaned=0` with missing receipt sidecars;
- classifies durable DB receipt rows without live sidecars as `ResumeTransfer`;
- emits exactly one transfer file plan for the pending path;
- respects a one-chunk request budget and a one-chunk peer-round budget;
- reports deferred chunks for later transfer rounds;
- binds work to the expected peer and peer session; and
- emits `sync-resume-transfer-request:v1:`, `sync-resume-peer-request:v1:`, and `sync-resume-peer-schedule:v1:` keys.

Recorded result: `anonsync_core sync domain model selftest passed=234 failed=0`.

## Validation

The release CTest suite reports `100% tests passed, 0 tests failed out of 27`.

The focused sanitizer selftest reports `anonsync_core sync domain model selftest passed=234 failed=0`.

The package validator is:

```bash
python3 tools/validate_rev0685_resume_transfer_planner.py
```

## Remaining ceiling

Rev0685 is not a general restart engine. It does not persist transfer work-order rows, claim or reclaim workers, fetch peer bytes, write missing staged chunks, update receipt rows, or advance into materialization. The next best move is a durable transfer-work schema or a narrow fake-peer `ResumeTransfer` executor that consumes the rev0685 work order and transitions complete staged evidence to the existing rev0683/rev0684 executors.
