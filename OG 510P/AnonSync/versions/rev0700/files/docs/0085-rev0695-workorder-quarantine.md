# Rev0695 — workorder quarantine

Rev0695 is code-bearing. Rev0694 gave expired resume-transfer workorders deterministic retry-at backoff scheduling, but suspicious evidence drift still failed only by rolling back the current operation. That was safe, but not durable enough for a daemon: after the failed claim ended, there was no row-state fact saying that a claimed workorder had become unsafe to touch.

Rev0695 adds the first durable quarantine slice. An existing claimed resume-transfer workorder now becomes terminal `work_state='quarantined'` when its stored evidence no longer matches the current transfer plan.

```text
claimed row + current plan mismatch
  → work_state='quarantined'
  → sync_session_resume_transfer_workorder_quarantine_events row
  → no byte writes
  → future claim/execute attempts fail closed
```

This is intentionally separate from abandon. Abandon means ordinary retry-cap exhaustion. Quarantine means suspicious evidence mismatch.

## New durable evidence

The `sync_session_resume_transfer_workorders.work_state` set now includes:

- `quarantined`

The new companion table is:

- `sync_session_resume_transfer_workorder_quarantine_events`

Each quarantine event records:

- `quarantined_at_epoch`
- previous chunk/source-action/idempotency/peer/session/staging/lease/retry/attempt evidence from the stored row
- expected chunk/source-action/idempotency/peer/session/staging evidence from the current plan
- decision worker, lease, and lease epoch
- `quarantine_reason='plan-evidence-mismatch'`

The row-state transition and event insert happen in the same transaction. A quarantine without event evidence remains impossible in the active path.

## API/result surface

Claim and execution results now expose:

- per-file `workorder_rows_quarantined`
- per-file `workorder_quarantine_events_written`
- top-level `workorder_rows_quarantined`
- top-level `workorder_quarantine_events_written`
- claim-level `files_quarantined`

The executor skips byte writes when any selected chunk for a file is quarantined or abandoned during claim/probe. Completion still requires owned `claimed` rows.

## Audit/refactor performed

The audit target was the shared row-lifecycle helper. The finding was that the helper already centralized the right decision point, but the suspicious-evidence branch was represented as a generic throw. Rev0695 refactors that branch into an explicit terminal transition while preserving the existing ordering:

1. Insert or reload the row.
2. Reject terminal `abandoned` or `quarantined` rows.
3. If claimed-row evidence mismatches the current plan, quarantine and write an event.
4. Reject mismatched live ownership.
5. Reject expired rows before `retry_at_epoch` opens.
6. If retry-open and at cap, abandon with evidence.
7. If retry-open and under cap, reclaim with evidence.
8. Complete only owned claimed rows after receipts and staged bytes are verified.

## Selftest proof

The active sync-domain selftest now proves:

- an initially claimed fixture has no quarantined rows;
- mutating a claimed row's stored schedule idempotency key causes a durable quarantine, not a rollback-only failure;
- the quarantine event preserves previous mismatched schedule evidence and expected current-plan schedule evidence;
- future claim attempts against a terminal quarantined row fail closed;
- retry-at backoff, expired reclaim, attempt-cap abandon, preserved reclaim history, fail-closed abandoned-row reclaim, reclaimed-owner execution, materialization, cleanup, and convergence still pass.

Recorded validation for this revision:

- Release CTest: `100% tests passed, 0 tests failed out of 27`.
- Packaged sync-domain selftest: `anonsync_core sync domain model selftest passed=256 failed=0`.
- ASAN/UBSAN sync-domain selftest: `anonsync_core sync domain model selftest passed=256 failed=0` with leak detection disabled.

## What is still missing

Rev0695 adds durable quarantine, but it does not yet implement terminal repair/reset, production peer response acceptance, tombstone replay, conflict replay, persisted daemon wake loops, or a UI/operator workflow for abandoned/quarantined rows.

Rev0696 should add the first evidence-preserving repair/reset path for terminal abandoned/quarantined workorders.

Filename structure to preserve for linked revisions: `Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip`.
