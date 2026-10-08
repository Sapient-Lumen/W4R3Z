# Rev0698 — scheduler action plan

Rev0698 is code-bearing. Rev0697 made persisted resume-transfer workorders observable through a read-only queue selector, but the next daemon seam still required callers to translate queue facts into action classes themselves. That was too easy to get subtly wrong: a future worker could treat a terminal row as runnable, ignore retry-at cooldown, or prioritize an unsafe reclaim ahead of an owned live claim.

Rev0698 adds a bounded scheduler-pass action planner for resume-transfer workorders.

```text
sync_session_resume_transfer_workorders rows
  + rev0697 queue selector
  + scheduler_now_epoch
  + optional worker/lease identity
  + optional max_scheduler_actions
  → deterministic scheduler action classes
  → still no byte transfer, no row mutation, no terminal reset
```

## New scheduler action API

The new API is:

- `plan_sync_session_checkpoint_resume_transfer_workorder_scheduler_pass(...)`

The new public surfaces are:

- `SyncSessionCheckpointResumeTransferWorkorderSchedulerPassOptions`
- `SyncSessionCheckpointResumeTransferWorkorderSchedulerPassAction`
- `SyncSessionCheckpointResumeTransferWorkorderSchedulerPassResult`
- `SyncSessionCheckpointResumeTransferWorkorderSchedulerActionKind`

This API deliberately consumes the rev0697 selector instead of reimplementing SQLite policy. It produces a bounded, deterministic action plan over returned queue facts. It does not execute chunks, claim rows, reclaim rows, abandon rows, reset terminal rows, materialize files, clean staging artifacts, or mutate the checkpoint database.

## Action classes

Rev0698 maps queue facts to scheduler actions:

- `OwnedClaimReady` → `ExecuteOwnedClaim`.
- `ExpiredReclaimReady` → `ClaimOrReclaimExpired`.
- `ExpiredAbandonReady` → `AbandonExpired`.
- `LiveClaimedByOther` → `ObserveLiveClaimedByOther`.
- `ExpiredCoolingDown` → `WaitRetryBackoff`.
- `AbandonedReview` → `ReviewAbandoned`.
- `QuarantinedReview` → `ReviewQuarantined`.
- `CompletedIgnored` → `IgnoreCompleted` when completed rows are explicitly included for audit.

Each action carries the source queue kind, path, chunk offset/length/hash, worker/lease evidence, peer/session evidence, idempotency keys, lease/retry timing, attempt count, terminal-review marker, mutating-action marker, and scheduler priority. `max_scheduler_actions` can cap the returned batch without changing the underlying database.

## Audit/refactor performed

The audit target was the policy seam between queue selection and daemon mutation. Rev0697 centralized the read model, but a caller still had to decide what a queue fact meant. Rev0698 refactors that mapping into a public scheduler pass planner so future mutating daemon code can consume a single action vocabulary instead of scattering priority and safety rules.

The important safety choice is negative: terminal rows are never mapped to automatic reset, completed rows are ignored unless explicitly requested, cooldown rows are mapped to wait actions, and rows held by another live worker are observational only. Mutating action classes are limited to execute-owned, claim-or-reclaim-expired, and abandon-expired-at-cap decisions.

## Selftest proof

The active sync-domain selftest now proves:

- owned queue facts become bounded `ExecuteOwnedClaim` actions;
- `max_scheduler_actions` caps returned work without mutating rows;
- expired cooldown rows become non-mutating `WaitRetryBackoff` actions;
- retry-open expired rows become `ClaimOrReclaimExpired` actions;
- retry-open rows at the attempt cap become `AbandonExpired` actions;
- quarantined rows become review actions while other owned rows remain runnable;
- release CTest, packaged selftest, and ASAN/UBSAN selftest still pass.

Recorded validation for this revision:

- Release CTest: `100% tests passed, 0 tests failed out of 27`.
- Packaged sync-domain selftest: `anonsync_core sync domain model selftest passed=276 failed=0`.
- ASAN/UBSAN sync-domain selftest: `anonsync_core sync domain model selftest passed=276 failed=0` with leak detection disabled.

## What is still missing

Rev0698 adds a bounded scheduler action plan, not the mutating daemon worker loop. The next P0 is the first mutating scheduler pass that consumes these actions and invokes the existing narrow mutators safely: execute owned work, reclaim retry-open work, abandon at-cap work, and leave terminal rows for operator review. Real peer transport, authenticated peer response acceptance, overwrite/tombstone/conflict replay, encrypted transport, discovery, invite/share-key authority, and terminal-review product workflow remain out of scope.

Filename structure to preserve for linked revisions: `Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip`.
