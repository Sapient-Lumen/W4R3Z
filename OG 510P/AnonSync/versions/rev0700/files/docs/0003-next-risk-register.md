# Next risk register after rev0700

Rev0700 fixed the first mutating scheduler bridge: a bounded scheduler executor now consumes complete returned `execution_idempotency_key` groups and delegates to existing claim/reclaim/abandon/execution mutators through execution-key filters. It does not directly update workorder rows.

## Current P0 risks

1. **No persisted daemon loop yet.** The cube can claim, execute, abandon, quarantine, reset, select queue facts, plan scheduler actions, group those actions safely, and run one bounded mutating scheduler pass. It still does not run a persistent worker loop with stable identity, repeated passes, and stop conditions.
2. **Real peer transport is still not bound to owned claims.** The fake-peer/source-root shortcut proves row lifecycle and byte writes, but production response acceptance must be tied to a claimed workorder row and authenticated peer response evidence.
3. **Scheduler execution must not grow SQL shortcuts.** Rev0700 intentionally delegates mutation to existing evidence-bound mutators. Future loop work should preserve that invariant rather than adding direct scheduler-row updates.
4. **Terminal review has no product workflow.** Abandoned and quarantined rows are visible and resettable under explicit permission, but there is no operator UI/policy boundary for inspecting and approving repair.
5. **Tombstone/conflict replay remains below the workorder standard.** Delete and conflict-copy resume branches still need the same durable scheduler discipline as file fetch.

## Current P1 risks

1. **Backpressure policy is local and manual.** `max_scheduler_actions` bounds one pass; a daemon loop needs policy for repeated passes, cooldown-only waits, and live-other rows without spin.
2. **Worker identity needs product semantics.** The executor accepts worker IDs/lease epochs; a daemon needs stable persisted worker identity, not caller-invented strings.
3. **Audit manifests are useful but not stateful enough.** Validators still rely heavily on phrases/logs/hashes. They should grow SQLite transition probes for the daemon loop and workorder tables.
4. **`sync_domain.cpp` remains too large.** The scheduler/workorder region should eventually split away from manifest/diff/filesystem/application code.
5. **Quarantine reasons are still narrow.** Evidence mismatch is covered; suspicious event-history, retry schedule drift, and unexpected terminal transitions should become explicit reasons.

## Next safest move

Add a daemon-loop wrapper around `execute_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(...)`. It should:

- persist or receive a stable worker identity and monotonically advancing lease epoch,
- call the scheduler executor in bounded passes,
- stop cleanly on no returned mutating work, cooldown-only work, live-other-only work, terminal-review work, or configured pass limits,
- report per-pass and aggregate counters,
- prove that repeated passes cannot spin or mutate terminal rows,
- continue delegating all mutation to the existing claim/execution/abandon paths.

## Validation floor

Every future restart/scheduler revision should preserve the rev0700 validation floor: `anonsync_core sync domain model selftest passed=285 failed=0`, `100% tests passed, 0 tests failed out of 27`, active-binary hash binding, package-local manifest, and explicit audit. New scheduler revisions should also prove row-state transitions such as `planned → claimed`, `claimed → completed`, `claimed → expired/retry-closed`, `expired/retry-open → reclaimed`, `expired/retry-open/at-cap → abandoned`, suspicious drift → `quarantined`, explicit terminal reset → `claimed`, daemon queue selection, scheduler action planning, complete scheduler group batching, bounded mutating scheduler execution, and future daemon-loop repetition without silently deleting or overwriting evidence.

This register explicitly treats the scheduler executor as a bridge, not as a privileged SQL mutator.
