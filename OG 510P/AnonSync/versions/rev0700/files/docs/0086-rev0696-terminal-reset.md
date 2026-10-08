# Rev0696 — terminal workorder reset

Rev0696 is code-bearing. Rev0695 made abandoned and quarantined resume-transfer workorders durable terminal safety facts, but it left them as one-way stops. That was safe, but incomplete for a long-running sync daemon: a trusted operator or recovery worker needs a way to reopen terminal work after inspecting the condition, without deleting the abandon/quarantine history that made the stop visible.

Rev0696 adds the first evidence-preserving terminal reset slice for resume-transfer workorders.

```text
abandoned/quarantined row + explicit reset permission + current transfer-plan evidence
  → sync_session_resume_transfer_workorder_reset_events row
  → work_state='claimed' under a fresh worker lease
  → claim_attempts reset to 1
  → prior abandon/quarantine/reclaim event history remains queryable
```

This is not silent reclaim. Ordinary workers still fail closed against terminal rows. A terminal row only reopens through `reset_sync_session_checkpoint_resume_transfer_terminal_workorders`, with explicit permission for the terminal state being reset.

## New durable evidence

Rev0696 adds:

- `sync_session_resume_transfer_workorder_reset_events`
- `reset_reason='operator-terminal-reset'`
- previous terminal state, previous chunk/source-action/idempotency/peer/session/staging/lease/retry/attempt evidence
- new current-plan chunk/source-action/idempotency/peer/session/staging evidence
- new worker, lease, claimed-at, lease-expiry, and `retry_at_epoch` evidence

The reset event insert and row reopen happen in the same transaction. A reset without a reset event remains impossible in the active path.

## API/result surface

The new API is:

- `reset_sync_session_checkpoint_resume_transfer_terminal_workorders(...)`

The new option/result structs expose:

- `reset_abandoned_workorders`
- `reset_quarantined_workorders`
- `workorder_reset_now_epoch`
- `workorder_retry_backoff_seconds`
- `terminal_rows_found`
- `workorder_rows_reset`
- `abandoned_rows_reset`
- `quarantined_rows_reset`
- `reset_events_written`

The reset API reloads the same transfer plan used by claim/execution, verifies durable checkpoint/source evidence through the planner, writes the reset audit row, and then reopens only the selected terminal rows as fresh `claimed` rows under the reset worker lease.

## Audit/refactor performed

The audit target was the rev0695 terminal boundary. The key finding was that terminal rows were correctly non-stealable and non-reclaimable, but there was no explicit path to convert a reviewed terminal fact back into claimed work. That forced an operator either to leave safe work stuck forever or to mutate SQLite state outside the product API.

Rev0696 keeps the existing claim/probe/reclaim/abandon/quarantine helper intact and adds a separate reset API instead of weakening terminal rejection. The reset path deliberately does not delete workorder rows or cascade away existing reclaim/abandon/quarantine events. It updates the terminal row in place after writing reset evidence, preserving history through the same primary workorder identity.

## Selftest proof

The active sync-domain selftest now proves:

- terminal reset requires explicit terminal-state permission;
- a quarantined row can be reopened only through a durable reset event preserving prior quarantine evidence;
- an abandoned row set can be reopened only through durable reset events preserving previous abandoned/reclaim history;
- after reset, the normal claim path treats the reopened rows as ordinary owned `claimed` work;
- terminal-row silent reclaim remains fail-closed before the reset;
- retry-at backoff, expired reclaim, attempt-cap abandon, durable quarantine, reclaimed-owner execution, materialization, cleanup, and convergence still pass.

Recorded validation for this revision:

- Release CTest: `100% tests passed, 0 tests failed out of 27`.
- Packaged sync-domain selftest: `anonsync_core sync domain model selftest passed=261 failed=0`.
- ASAN/UBSAN sync-domain selftest: `anonsync_core sync domain model selftest passed=261 failed=0` with leak detection disabled.

## What is still missing

Rev0696 adds an evidence-preserving terminal reset API, but it is still not a production operator UI, persisted daemon queue selector, authenticated peer response acceptance path, tombstone replay, conflict replay, encrypted transport, discovery, invite/share-key authority, or trust/privacy product surface.

The next scheduler step should consume `retry_at_epoch` and terminal/reset states from a persisted daemon loop rather than relying on direct API calls from selftests.

Filename structure to preserve for linked revisions: `Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip`.
