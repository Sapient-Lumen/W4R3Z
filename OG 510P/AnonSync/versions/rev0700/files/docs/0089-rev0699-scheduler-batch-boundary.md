# Rev0699 — scheduler batch boundary

## Summary

Rev0699 is a code-bearing scheduler safety slice. Rev0698 produced row-shaped scheduler actions from persisted resume-transfer workorder queue facts. That was useful for observation, but it was unsafe to wire directly to mutation because transfer execution evidence is batch-shaped: rows for the same planned peer assignment share the same `execution_idempotency_key`.

Rev0699 hardens that boundary by grouping scheduler actions by `execution_idempotency_key`. A bounded scheduler pass now returns a complete execution group or defers the entire group. It never returns a partial mutating group just because `max_scheduler_actions` was too small.

## Why this matters

The next product goal is a mutating persisted scheduler pass. Before adding it, the cube needed to prove that an action cap cannot create hidden out-of-band mutation pressure.

The rev0698 planner could return one chunk row from a larger owned claim when `max_scheduler_actions=1`. Existing execution idempotency evidence for that row was computed over the whole assigned chunk batch. A future executor faced two bad choices:

1. execute the whole batch and silently mutate rows outside the returned scheduler action list, or
2. execute only one chunk and recompute a different execution key, causing a legitimate claimed row to look suspicious.

Rev0699 rejects that shape. The scheduler planner now exposes execution-group metadata and defers groups that would be split.

## Public API additions

`SyncSessionCheckpointResumeTransferWorkorderSchedulerPassAction` now includes:

- `scheduler_group_priority`
- `scheduler_group_size`

`SyncSessionCheckpointResumeTransferWorkorderSchedulerPassResult` now includes:

- `scheduler_action_groups_considered`
- `scheduler_action_groups_returned`
- `scheduler_action_groups_deferred_by_limit`
- `scheduler_actions_deferred_by_limit`

The action kinds remain unchanged:

- `ExecuteOwnedClaim`
- `ClaimOrReclaimExpired`
- `AbandonExpired`
- `ObserveLiveClaimedByOther`
- `WaitRetryBackoff`
- `ReviewAbandoned`
- `ReviewQuarantined`
- `IgnoreCompleted`

## Behavioral contract

`plan_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(...)` remains read-only. It still consumes `select_sync_session_checkpoint_resume_transfer_workorder_queue(...)` and does not update SQLite or filesystem state.

The new scheduler batching contract is:

1. Build action drafts from queue facts.
2. Group drafts by `execution_idempotency_key`.
3. For observational rows without an execution key, use a unique observational group key.
4. Apply `max_scheduler_actions` only at group boundaries.
5. If a group would exceed the cap, defer the group and increment deferred counters.
6. Assign `scheduler_priority` only to returned actions.
7. Assign `scheduler_group_priority` and `scheduler_group_size` to every returned action.

## Selftest evidence

The active sync-domain selftest now proves both sides of the boundary:

- A live owned workorder batch with multiple chunks and `max_scheduler_actions=1` returns zero actions, one deferred group, and deferred action count equal to the chunk count.
- The same batch with a cap equal to the complete group size returns the full group as `ExecuteOwnedClaim` actions with shared group metadata.

The active selftest now records:

```text
anonsync_core sync domain model selftest passed=277 failed=0
```

Release CTest remains:

```text
100% tests passed, 0 tests failed out of 27
```

## What this enables next

The next code-bearing revision can add the first mutating scheduler pass with a safer rule: consume complete scheduler action groups only. That executor should call the existing claim/execution/abandon paths and prove it never mutates deferred groups, cooldown rows, live-other rows, terminal review rows, or completed audit rows.

Filename structure to preserve for linked revisions: `Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip`.
