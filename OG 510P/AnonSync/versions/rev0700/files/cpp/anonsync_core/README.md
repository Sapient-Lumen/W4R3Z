# anonsync_core rev0700

This C++ core is the active product surface for AnonSync's peer-to-peer folder convergence work.

Rev0700 extends the sync-domain module introduced in rev0651 and the transfer/session/checkpoint pipeline developed through rev0699 with the first bounded mutating scheduler executor for persisted resume-transfer workorders:

- `SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionOptions`
- `SyncSessionCheckpointResumeTransferWorkorderSchedulerExecutionResult`
- `execute_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(...)`
- `allowed_execution_idempotency_keys` on claim/execution mutators
- complete-group consumption for `ExecuteOwnedClaim`, `ClaimOrReclaimExpired`, and `AbandonExpired`
- non-mutating observation for `ObserveLiveClaimedByOther`, `WaitRetryBackoff`, `ReviewAbandoned`, `ReviewQuarantined`, and `IgnoreCompleted`

The active lifecycle now has five distinct paths: evidence-bound mutators, read-only selectors, scheduler action planning, scheduler group-boundary planning, and a bounded scheduler executor. Claim, reclaim, abandon, quarantine, reset, execution, materialization, and cleanup remain evidence-bound mutators. The queue selector remains a non-mutating SQLite read model. The scheduler pass planner consumes that selector and translates durable facts into a daemon action vocabulary without changing rows. Rev0700 adds the executor bridge that consumes complete returned groups and delegates mutation through existing mutator APIs using `execution_idempotency_key` filters.

The rev0700 selftest proves clean terminal `AlreadyConverged`, complete transfer/materialize/cleanup restart, claim-only workorders, live-steal rejection, expired reclaim, retry-at cooldown, attempt-cap abandon, quarantine, terminal reset, queue selection, scheduler action planning, scheduler group-boundary deferral/return behavior, and mutating scheduler execution over returned complete groups.

Validation evidence for this package:

```text
anonsync_core sync domain model selftest passed=285 failed=0
100% tests passed, 0 tests failed out of 27
```

The next code-bearing seam should be a persisted daemon loop around the scheduler executor: stable worker identity, bounded repeated passes, backpressure, and stop conditions for terminal review, instead of a single caller-driven scheduler pass.
