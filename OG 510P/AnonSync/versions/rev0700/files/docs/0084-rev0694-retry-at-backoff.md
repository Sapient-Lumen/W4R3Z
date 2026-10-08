# Rev0694 — retry-at backoff scheduling

Rev0694 is code-bearing. Rev0693 gave expired resume-transfer workorders a deterministic terminal stop policy through `max_workorder_claim_attempts` and `work_state='abandoned'`, but expiry alone could still wake the daemon into immediate retry churn whenever the cap had not yet been reached.

Rev0694 adds the smallest scheduling-policy slice: every claimed resume-transfer workorder now carries `retry_at_epoch`, derived deterministically from the lease expiration, claim attempt number, and `workorder_retry_backoff_seconds`. Expiry remains part of the safety rule, but takeover is now gated by the retry window:

```text
reclaim/abandon may run only when
lease_expires_at_epoch <= workorder_claim_now_epoch
and
retry_at_epoch <= workorder_claim_now_epoch
```

## New durable evidence

The `sync_session_resume_transfer_workorders` row now stores:

- `retry_at_epoch`

For attempt `n`, the retry time is:

```text
retry_at_epoch = lease_expires_at_epoch + (workorder_retry_backoff_seconds * n)
```

With `workorder_retry_backoff_seconds=0`, rev0694 preserves rev0693 behavior: `retry_at_epoch == lease_expires_at_epoch`.

Reclaim and abandon event tables now preserve scheduling context:

- `sync_session_resume_transfer_workorder_reclaim_events.previous_retry_at_epoch`
- `sync_session_resume_transfer_workorder_reclaim_events.new_retry_at_epoch`
- `sync_session_resume_transfer_workorder_abandon_events.previous_retry_at_epoch`

The event row is written in the same transaction as the workorder transition. A retry-at transition without matching event evidence remains impossible.

## API/result surface

Claim and execution options now expose:

- `workorder_retry_backoff_seconds`

Claim and execution results now expose:

- top-level `workorder_retry_backoff_seconds`
- top-level `retry_at_epoch`
- per-file `retry_at_epoch`

The per-file value reflects the actual claimed/reclaimed row schedule. The top-level value is the maximum retry-at epoch observed across the file outcomes in the operation.

## Audit/refactor performed

The audit target was the rev0693 row-lifecycle helper and event schema. The finding was that lease expiry and retry readiness were still collapsed into one concept. Rev0694 separates them while keeping the decision centralized:

1. Insert or reload the row.
2. Reject mismatched live ownership.
3. Detect expired rows.
4. Reject expired rows whose `retry_at_epoch` has not opened.
5. If the retry window is open and the cap is reached, abandon with scheduling evidence.
6. If the retry window is open and the cap is not reached, reclaim with previous/new scheduling evidence.
7. Reject terminal abandoned rows.

This is intentionally a local scheduler primitive, not network transport.

## Selftest proof

The active sync-domain selftest now proves:

- initial claim-only rows can store deterministic retry-at backoff evidence;
- an expired row at lease expiration is rejected while its retry window is still closed;
- the same row is reclaimable once `retry_at_epoch` opens;
- reclaim events persist both previous and new retry-at epochs;
- existing zero-backoff reclaim/abandon behavior remains compatible;
- attempt-cap abandon, preserved reclaim history, fail-closed abandoned-row reclaim, reclaimed-owner execution, materialization, cleanup, and convergence still pass.

Recorded validation for this revision:

- Release CTest: `100% tests passed, 0 tests failed out of 27`.
- Packaged sync-domain selftest: `anonsync_core sync domain model selftest passed=252 failed=0`.
- ASAN/UBSAN sync-domain selftest: `anonsync_core sync domain model selftest passed=252 failed=0` with leak detection disabled.

## What is still missing

Rev0694 adds retry-at/backoff scheduling evidence, but it does not yet implement quarantine transitions for suspicious evidence drift, production peer response acceptance, tombstone replay, conflict replay, persisted daemon wake loops, or a repair/reset workflow for abandoned/quarantined rows.

Rev0695 should use this scheduling evidence to add the first durable quarantine state and quarantine event table, keeping suspicious drift separate from ordinary retry exhaustion.

Filename structure to preserve for linked revisions: `Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip`.
