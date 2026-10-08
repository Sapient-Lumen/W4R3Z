# Rev0700 — scheduler executor boundary

Rev0700 is the first code-bearing revision where the persisted resume-transfer scheduler does more than plan. It executes a bounded pass, but only through complete returned scheduler groups and only by delegating to the existing evidence-bound mutators.

## Why this matters

Rev0698 introduced a read-only action vocabulary over workorder queue facts. Rev0699 made bounded passes safe by refusing to split rows that share an `execution_idempotency_key`. The remaining danger was the bridge into mutation: the scheduler returns a bounded action set, but the claim and execution mutators derive their authority from the full transfer plan. Without a lower filter, a daemon could ask for one group and accidentally mutate every currently plan-visible row.

Rev0700 closes that seam with `allowed_execution_idempotency_keys`.

## New boundary

`execute_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(...)` does this:

1. Loads a bounded scheduler pass with `plan_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(...)`.
2. Validates that returned mutating actions carry complete group metadata and namespaced `sync-resume-transfer-execute:v1:` evidence.
3. Splits returned mutating groups into owned-execute keys and claim/reclaim/abandon keys.
4. Calls `claim_sync_session_checkpoint_resume_transfer_workorders(...)` only when returned groups require `ClaimOrReclaimExpired` or `AbandonExpired`.
5. Calls `execute_sync_session_checkpoint_resume_transfer_workorders(...)` only when returned groups require `ExecuteOwnedClaim`.
6. Verifies that the mutator consumed exactly the selected scheduler actions.
7. Treats deferred groups, live claims held by other workers, retry cooldown rows, terminal review rows, and completed audit rows as observation-only facts.

The scheduler executor does not perform direct `UPDATE sync_session_resume_transfer_workorders` shortcuts. It reuses the existing mutators so checkpoint integrity, source filesystem evidence, apply-intent evidence, workorder evidence, lease ownership, retry windows, terminal states, and staging paths are checked in the same place as before.

## Public surface added

- `SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionOptions`
- `SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionResult`
- `execute_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(...)`
- `SyncSessionCheckpointResumeTransferClaimOptions.allowed_execution_idempotency_keys`
- `SyncSessionCheckpointResumeTransferExecutionOptions.allowed_execution_idempotency_keys`

## Selftest coverage added

The active sync-domain selftest now proves:

- `max_scheduler_actions` too small for a complete group returns deferral counters and leaves claimed rows untouched.
- Retry-cooling rows are observed without reclaim or execution.
- A returned retry-open expired group is reclaimed through the claim mutator and writes reclaim events.
- A returned attempt-cap expired group is abandoned through the claim mutator and writes abandon events.
- A returned owned live group is executed through the execution mutator and completes the selected workorder rows.
- Completed workorders reappear only as completed audit facts when explicitly requested.

Validation summary:

```text
anonsync_core sync domain model selftest passed=285 failed=0
100% tests passed, 0 tests failed out of 27
```

## Audit/refactor note

The selftest now freezes an owned-executor checkpoint seed before later retry/reclaim checks and runs owned execution after those checks. That avoids using a transfer write to mutate the shared staging fixture before cooldown/reclaim tests have finished. The production code change is the lower execution-key filter; the fixture refactor keeps the proof honest.

## Remaining gap

Rev0700 is a bounded scheduler executor, not yet a daemon. The next revision should wrap it in a persisted loop that uses stable worker identity, repeats bounded passes, respects backpressure, stops on terminal review, and never spins on cooldown or live-other rows.

Filename structure to preserve for linked revisions: `Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip`.
