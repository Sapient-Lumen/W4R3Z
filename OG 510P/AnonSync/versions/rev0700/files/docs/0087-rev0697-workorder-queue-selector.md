# Rev0697 — workorder queue selector

Rev0697 is code-bearing. Rev0696 gave abandoned/quarantined resume-transfer workorders an evidence-preserving reset path, but the cube still lacked a durable read model for a daemon. The scheduler facts existed in SQLite; no API could ask, without mutation, “what should a worker do next?”

Rev0697 adds the first persisted daemon queue selector slice for resume-transfer workorders.

```text
sync_session_resume_transfer_workorders rows
  + queue_now_epoch
  + optional current worker/lease identity
  + optional max_workorder_claim_attempts
  → read-only queue facts
  → no row mutation, no byte transfer, no filesystem write
```

## New read-only API

The new API is:

- `select_sync_session_checkpoint_resume_transfer_workorder_queue(...)`

The new public surfaces are:

- `SyncSessionCheckpointResumeTransferWorkorderQueueOptions`
- `SyncSessionCheckpointResumeTransferWorkorderQueueFact`
- `SyncSessionCheckpointResumeTransferWorkorderQueueResult`
- `SyncSessionCheckpointResumeTransferWorkorderQueueKind`

The selector opens the checkpoint read-only, reloads the resume view, preserves the durable/source verification gates, and scans `sync_session_resume_transfer_workorders` with deterministic ordering. It returns facts; it does not claim rows, reclaim rows, abandon rows, reset rows, transfer bytes, materialize files, or clean staging artifacts.

## Queue classifications

Rev0697 classifies workorders as:

- `OwnedClaimReady` — a live claimed row owned by the selector worker/lease and eligible for execution.
- `LiveClaimedByOther` — a live claimed row not owned by the selector worker/lease.
- `ExpiredCoolingDown` — an expired row whose `retry_at_epoch` has not opened.
- `ExpiredReclaimReady` — an expired row whose retry window is open and which is below the configured abandon cap.
- `ExpiredAbandonReady` — an expired retry-open row at `max_workorder_claim_attempts`.
- `AbandonedReview` — a terminal abandoned row that requires operator/recovery review.
- `QuarantinedReview` — a terminal quarantined row that requires safety review.
- `CompletedIgnored` — a completed row, hidden by default and exposed only when `include_completed_workorders` is true.

Each fact also carries the stored worker, lease, timing, claim-attempt, source-action, idempotency, peer/session, staging path, chunk evidence, and reclaim/abandon/quarantine/reset event counts. Reset rows are not a special mutable path; they appear as ordinary claimed rows with reset history present.

## Audit/refactor performed

The audit target was the gap between row lifecycle mutation and daemon readiness. Rev0696 could already store wake predicates (`retry_at_epoch`), stop predicates (`abandoned`, `quarantined`), repair predicates (reset events), and completion facts, but the only way to reason over them was direct SQL in tests or ad hoc code.

Rev0697 factors that reasoning into a public read-only queue selector. This keeps the mutator APIs narrow and makes scheduler policy inspectable. The selector deliberately requires `worker_id` and `worker_lease_id` together before marking a row as owned, so a daemon cannot accidentally treat “same worker name” as enough ownership evidence.

## Selftest proof

The active sync-domain selftest now proves:

- owned live claimed rows are selected as `OwnedClaimReady` without mutation;
- expired rows remain `ExpiredCoolingDown` until `retry_at_epoch` opens;
- retry-open expired rows are selected as `ExpiredReclaimReady`;
- retry-open rows at the configured attempt cap are selected as `ExpiredAbandonReady`;
- quarantined rows are selected only as terminal review facts;
- reset quarantined rows appear as fresh owned claimed work while older claims remain reclaimable;
- abandoned rows are selected only as terminal review facts;
- reset abandoned rows appear as fresh owned claimed work with reset history;
- completed rows are ignored by default and exposed as `CompletedIgnored` only for explicit audit;
- release CTest, packaged selftest, and ASAN/UBSAN selftest still pass.

Recorded validation for this revision:

- Release CTest: `100% tests passed, 0 tests failed out of 27`.
- Packaged sync-domain selftest: `anonsync_core sync domain model selftest passed=271 failed=0`.
- ASAN/UBSAN sync-domain selftest: `anonsync_core sync domain model selftest passed=271 failed=0` with leak detection disabled.

## What is still missing

Rev0697 adds a selector, not a daemon. The next P0 is a bounded scheduler pass that consumes these facts and calls existing mutators deterministically without inventing shortcuts. Real peer transport, authenticated peer response acceptance, persisted overwrite replay, tombstone replay, conflict replay, encrypted transport, discovery, invite/share-key authority, and trust/privacy product surfaces remain out of scope.

Filename structure to preserve for linked revisions: `Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip`.
