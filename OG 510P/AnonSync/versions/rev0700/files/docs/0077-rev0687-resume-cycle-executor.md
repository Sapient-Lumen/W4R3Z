# Rev0687 — resume cycle drain executor

## Scope of this linked revision

Rev0687 is code-bearing. It promotes a new active C++ executable:

- `bin/rev0687/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3`

Rev0686 made fake-peer `ResumeTransfer` work orders executable. Rev0687 addresses the next operational risk: a caller should not have to hand-wire the restart sequence from transfer continuation to staged-file materialization to committed-staging cleanup. The new `execute_sync_session_checkpoint_resume_cycle` function drains the already-proven restart branches in order and then re-runs the action router as a final proof.

## Mission fit

AnonSync's mission is evidence-bound peer-to-peer folder convergence. A restart path should be resumable by shape, not by tribal knowledge. Rev0687 makes the local restart loop explicit:

`action plan → fake-peer transfer executor → action plan → materialization executor → action plan → cleanup executor → strict final action plan`

The final action plan is configured to require live destination filesystem evidence and clean staging artifacts before the cycle reports convergence. That keeps the mission centered on actual folder truth rather than merely successful function calls.

The revised local proof path is now:

`source scan → destination scan → manifest diff → local apply plan → staged inspection → chunk request → peer schedule → peer-bound response batch → peer transfer round continuation → receipt-gated materialization → committed staging cleanup → destination rescan → content convergence → SQLite session checkpoint → manifest chunk-row persistence → read-only checkpoint verification → exact chunk receipt coverage guard → source filesystem probe → destination filesystem probe → staging cleanup probe → DB-bound terminal staging repair sweeper → read-only resume action plan router → MaterializeStagedFile resume executor → CleanupCommittedStaging resume executor → ResumeTransfer work-order planner → fake-peer ResumeTransfer executor → bounded resume-cycle drain executor`

## Public C++ surface

Rev0687 adds:

- `SyncSessionCheckpointResumeCycleOptions`
- `SyncSessionCheckpointResumeCycleResult`
- `execute_sync_session_checkpoint_resume_cycle`

The cycle executor is intentionally an orchestrator, not a new low-level mutation engine. Each mutating phase delegates to the existing branch executor and each boundary is re-planned through `plan_sync_session_checkpoint_resume_actions`.

## Audit/refactor performed

The audit finding was that rev0686 proved the fake-peer transfer branch but left a recoverable restart as several public calls that had to be invoked in exactly the right order. That is a product risk because the correct sequence is part of the sync engine, not caller policy.

Rev0687 closes that slice by adding a typed cycle executor that:

1. loads the initial restart action plan with durable integrity and source-filesystem gates;
2. refuses `QuarantineStaging`, `RejectDrift`, and `RepairCommittedStaging` instead of sweeping unsafe artifacts;
3. runs fake-peer transfer work when `ResumeTransfer` / enabled `RetryTransfer` actions exist;
4. re-plans before materialization and fails if transfer limits leave pending transfer work while final convergence is required;
5. runs `MaterializeStagedFile` work through the existing materialization executor;
6. re-plans before cleanup;
7. runs `CleanupCommittedStaging` work through the existing cleanup executor;
8. runs a final action plan with destination filesystem and staging-clean requirements enabled; and
9. reports final convergence only when every file is `AlreadyConverged` with no remaining restart actions.

A small selftest refactor also removed a duplicated transfer-executor assertion while adding the new cycle test.

## Selftest coverage added

`--selftest-sync-domain-model` now proves that the cycle executor:

- starts from a terminal checkpoint that is deliberately rewound for one file to `materialized=0` / `staging_artifacts_cleaned=0`;
- removes the destination file and staged sidecars to simulate an interrupted restart;
- classifies the file as recoverable transfer work through existing checkpoint evidence;
- runs the fake-peer transfer executor and writes all source manifest chunks into staging;
- runs materialization and restores the missing destination target;
- runs cleanup and marks receipt rows committed-cleaned;
- proves the final action plan has all files `AlreadyConverged`; and
- proves staging is empty and the live destination bytes match the source fixture.

Recorded result: `anonsync_core sync domain model selftest passed=237 failed=0`.

## Validation

The release CTest suite reports `100% tests passed, 0 tests failed out of 27`.

Package validator:

```bash
python3 tools/validate_rev0687_resume_cycle_executor.py
```

No sanitizer result is claimed for rev0687; the sanitizer rebuild was attempted but exceeded the available tool window.

## Remaining ceiling

Rev0687 still recomputes transfer work instead of persisting scheduler-owned rows before chunk writes. It does not define worker claims, leases, reclaims, or production peer transport. The next best move is to persist resume work-order rows and add worker ownership/reclaim semantics, so the cycle executor drains durable claimed work rather than recomputed local plans.
