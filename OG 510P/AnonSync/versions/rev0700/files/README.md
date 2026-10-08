# AnonSync slim C++ working cube — rev0700

AnonSync is a **C++ peer-to-peer file synchronization system**. The product target is Resilio Sync-style local folder replication across authorized devices: discover or address peers, compare authenticated file manifests, transfer missing content-addressed chunks, apply creates/updates/deletes exactly once, preserve conflicts honestly, and resume after interruption without a central service being the ordinary source of truth.

Rev0700 is **code-bearing**. It promotes a new active executable:

- `bin/rev0700/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3`

Rev0699 made bounded scheduler passes return complete `execution_idempotency_key` groups or explicit deferral evidence. Rev0700 turns that boundary into the first bounded **mutating persisted scheduler executor**: the scheduler pass is loaded, mutating groups are filtered by returned execution keys, and existing claim/reclaim/abandon/execution mutators are invoked only through those filters. There are no direct scheduler SQL shortcuts for workorder mutation.

## Active sync mission

The heart of the mission remains folder convergence under evidence-bound local truth:

> Make authorized devices converge on the same intended folder tree without treating a central service as the ordinary source of truth, while preserving enough evidence to recover safely, reject stale or forged work, and expose conflicts honestly.

The product noun is **folder convergence**. The durability noun is **evidence-bound local truth**. Rev0700 keeps the restart scheduler on that line by letting a future daemon perform exactly the bounded persisted work it was told to perform, while still reloading checkpoint, manifest, apply-intent, filesystem, lease, retry, and workorder evidence below the scheduler layer before mutation.

## Rev0700 changes

- Adds `allowed_execution_idempotency_keys` filters to `SyncSessionCheckpointResumeTransferClaimOptions` and `SyncSessionCheckpointResumeTransferExecutionOptions`.
- Adds `SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionOptions` and `SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionResult`.
- Adds `execute_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(...)` as the first persisted scheduler executor boundary.
- The scheduler executor calls `plan_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(...)`, accepts only complete returned groups, builds execution-key filters, and then delegates mutation to the existing claim/reclaim/abandon and owned-claim execution APIs.
- The claim/execution mutators now reject execution-key filters in the wrong namespace and skip transfer-plan files outside the selected execution keys.
- The scheduler executor observes deferred groups, retry cooldown rows, live-other rows, terminal review rows, and completed audit rows without mutation.
- Adds selftests proving: too-small action caps do not mutate; retry-cooling rows stay untouched; expired returned groups are reclaimed only through the claim mutator; at-cap expired groups are abandoned only through the claim mutator; owned returned groups complete only through the execution mutator; completed rows reappear only as audit facts when requested.
- Extends the active sync-domain selftest from `passed=277` to `passed=285`.
- Adds `docs/0090-rev0700-scheduler-executor-boundary.md`, `audit/rev0700-scheduler-executor-boundary-audit.json`, `audit/rev0700-scheduler-executor-boundary-source.patch`, `schema/rev0700/slim-cube-manifest.json`, and `tools/validate_rev0700_scheduler_executor_boundary.py`.

## Audit/refactor performed

The audit target was the first mutating scheduler bridge. The dangerous seam was that scheduler actions are returned as a bounded action list while the existing mutators derive authority from the full transfer plan. Wiring them together naively would let a daemon ask for one returned group but accidentally mutate every plan-visible row.

Rev0700 resolves that by adding an explicit `execution_idempotency_key` filter one layer below the scheduler. The scheduler executor never updates workorder rows directly. It turns returned complete groups into a small set of allowed execution keys and calls the existing evidence-bound mutators with those filters. The mutators recheck the current transfer plan, row evidence, lease ownership, retry window, terminal state, and staging evidence before touching SQLite rows or filesystem bytes.

A second audit issue surfaced in the selftest fixture: executing the owned group mutates the shared staging filesystem. The test now freezes the owned-executor checkpoint seed before later retry/reclaim tests and runs owned execution after those tests, so reclaim/backoff assertions are not weakened by fixture side effects.

## What is missing now

The scheduler can now run a bounded persisted mutating pass, but it is still a single-pass local boundary, not a production daemon. The next P0 gap is a persisted daemon loop that wraps it, persists worker identity, repeats bounded passes safely, and stops on terminal review or backpressure without spinning.

Other ceilings remain real: no production peer discovery, encrypted peer protocol, real peer response acceptance bound to owned claims, persisted multi-worker daemon, file watcher, UI, invite/share-key authority, trust/privacy policy, overwrite replay, tombstone replay, conflict replay, or productized operator repair UI.

## Validate

Current rev0700 package validation:

```bash
python3 tools/validate_rev0700_scheduler_executor_boundary.py
```

Recorded validation for this revision:

- `audit/logs/rev0700-release-ctest.log` records `100% tests passed, 0 tests failed out of 27`.
- `audit/logs/rev0700-packaged-sync-domain-selftest.log` records `anonsync_core sync domain model selftest passed=285 failed=0`.
- `audit/logs/rev0700-asan-ubsan-sync-domain-selftest.log` records `anonsync_core sync domain model selftest passed=285 failed=0` with leak detection disabled.
- `audit/logs/rev0700-scheduler-executor-boundary-package-validator.log` records `rev0700 scheduler executor boundary package validator passed`.
- The active binary SHA-256 is `c1f2f5fd3ca452e536434644c76bfd2775f84c4d553406d0e121cbfd1301ecbe`.

## Read first

- `docs/0090-rev0700-scheduler-executor-boundary.md` — this turn's mutating scheduler executor boundary.
- `docs/0089-rev0699-scheduler-batch-boundary.md` — complete execution-idempotency group planning.
- `docs/0088-rev0698-scheduler-action-plan.md` — bounded scheduler action planner over queue facts.
- `docs/0003-next-risk-register.md` — current risk register after the scheduler executor slice.
- `docs/0001-cpp-core-gameplan.md` — current C++ core plan and next daemon loop seam.

Filename structure to preserve for linked revisions: `Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip`.
