# Rev0682 — resume action plan restart router

## Scope of this linked revision

Rev0682 is code-bearing. It promotes a new active C++ executable:

- `bin/rev0682/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3`

Rev0681 could safely repair one terminal staging failure mode after restart. Rev0682 adds the first read-only restart action router: `plan_sync_session_checkpoint_resume_actions`. It turns durable checkpoint rows plus live source, destination, staging, and receipt evidence into explicit per-path actions instead of asking a caller to infer recovery behavior from counters.

## Mission fit

AnonSync’s mission is evidence-bound peer-to-peer folder convergence. A restarted process must not ask, “is the old checkpoint terminal?” only. It also needs to ask, “what is the next safe action for each path?” Rev0682 keeps this boundary read-only: it classifies paths but does not mutate SQLite or the filesystem.

The revised local proof path is now:

`source scan → destination scan → manifest diff → local apply plan → staged inspection → chunk request → peer schedule → peer-bound response batch → peer transfer round continuation → receipt-gated materialization → committed staging cleanup → destination rescan → content convergence → SQLite session checkpoint → manifest chunk-row persistence → read-only checkpoint verification → exact chunk receipt coverage guard → source filesystem probe → destination filesystem probe → staging cleanup probe → DB-bound terminal staging repair sweeper → read-only resume action plan router`

## Public C++ surface

Rev0682 adds:

- `SyncSessionCheckpointResumeActionKind`
- `SyncSessionCheckpointResumeActionPlanOptions`
- `SyncSessionCheckpointResumeActionFilePlan`
- `SyncSessionCheckpointResumeActionPlanResult`
- `plan_sync_session_checkpoint_resume_actions`

The action kinds are:

- `AlreadyConverged`
- `RepairCommittedStaging`
- `CleanupCommittedStaging`
- `MaterializeStagedFile`
- `ResumeTransfer`
- `RetryTransfer`
- `QuarantineStaging`
- `RejectDrift`

## Audit/refactor performed

The audit finding was that rev0681’s repair executor was safe but still narrow. It could remove stale committed terminal artifacts, but a restart caller still lacked a single typed view for non-terminal or partially restored paths.

Rev0682 adds a read-only planning/refactor boundary that:

1. loads `load_sync_session_checkpoint_resume_view` with durable/source proof by default, while allowing destination/staging cleanliness to be advisory for planning;
2. opens the checkpoint database read-only and requires the database path to remain outside source, destination, and staging roots;
3. joins file results, apply intents, source manifest entries, source manifest chunks, and chunk receipt rows;
4. verifies that stored absolute target/staging paths still match the caller’s configured roots;
5. checks current destination target bytes against checkpointed remote content evidence;
6. inspects staged `.part` files without treating partial files as corruption;
7. verifies receipt sidecars by hashing each receipt file back to the persisted `sync-chunk-receipt:v1:` key;
8. detects missing, wrong-kind, tampered, and unexpected receipt-directory artifacts;
9. returns missing chunks for partial transfer continuation; and
10. classifies each path into a concrete next action while leaving all mutation to later executors.

This is not a live transfer resume engine. It is a restart router that prevents the next executor from guessing.

## Selftest coverage added

`--selftest-sync-domain-model` now proves that the action router:

- classifies a terminal clean checkpoint as `AlreadyConverged` for both files;
- classifies a DB-mutated, complete staged file with accepted receipt rows as `MaterializeStagedFile`;
- classifies reappeared committed `.part` and `.part.chunks` artifacts as `RepairCommittedStaging` before the rev0681 repair executor runs; and
- classifies a tampered stale terminal staged file as `QuarantineStaging`, not as repairable.

Recorded result: `anonsync_core sync domain model selftest passed=223 failed=0`.

## Validation

The release CTest suite reports `100% tests passed, 0 tests failed out of 27`.

The focused sanitizer selftest reports `anonsync_core sync domain model selftest passed=223 failed=0`.

The package validator is:

```bash
python3 tools/validate_rev0682_resume_action_plan.py
```

## Remaining ceiling

Rev0682 still does not execute non-terminal recovery. It does not persist request-plan, peer-schedule, response-batch, or transfer-round rows before each round; it does not reclaim worker ownership; it does not write cleanup state transitions; and it does not implement tombstone/conflict branches in the fake session.

The next best move is a tiny executor for one `plan_sync_session_checkpoint_resume_actions` branch, most likely `MaterializeStagedFile`: materialize only when the action plan says the staged file is complete, every receipt is verified, source evidence still matches, and the destination target preflight is safe.
