# Rev0693 — attempt-cap abandon policy

Rev0693 is code-bearing. Rev0692 made expired resume-transfer claim takeover auditable by preserving previous-owner reclaim events, but repeated expiry could still churn forever: `claimed → expired → reclaimed → expired → reclaimed` had no deterministic stop condition. That was a scheduler safety gap, because a daemon must sometimes decide that a row should no longer be handed to another worker.

Rev0693 adds the first narrow abandon-policy slice for durable resume-transfer workorders. Claim and executor options now carry `max_workorder_claim_attempts`. When a row is still `claimed`, its lease has expired, and its persisted `claim_attempts` is already at the configured cap, the claim helper transitions the row to terminal `work_state='abandoned'` instead of reclaiming it again.

## New durable evidence

The workorder state machine now allows:

- `claimed`
- `completed`
- `abandoned`

A new companion table records the policy decision:

- `sync_session_resume_transfer_workorder_abandon_events`

Each abandon event records the session, path, chunk evidence, source action, abandon attempt, previous worker and lease window, decision worker and lease epoch, deterministic abandon time, max-attempt cap, and `abandon_reason='max-claim-attempts-exhausted'`.

The abandon event is inserted in the same SQLite transaction as the row state update. If event insertion fails, the abandon transition fails. There is no terminal abandon without a durable reason row.

## API/result surface

The claim and execution option structs now expose:

- `max_workorder_claim_attempts`

The result structs now expose top-level and per-file counters for:

- `workorder_rows_abandoned`
- `workorder_abandon_events_written`

The claim result also exposes `files_abandoned`, so claim-only daemon passes can distinguish rows that were newly owned from rows that became terminal under policy.

## Audit/refactor performed

The audit target was the shared claim/probe/reclaim helper. Rev0692 centralized row ownership decisions, which made it the right place to add policy. Rev0693 keeps that centralized shape and extends the helper from a two-way expired branch into a policy branch:

1. Insert or reload the row.
2. Reject mismatched live ownership.
3. If expired and under the cap, reclaim and write reclaim-event history.
4. If expired and at/over the cap, abandon and write abandon-event history.
5. Reject future claim attempts against terminal abandoned rows.

A small SQLite backup helper was added only for selftest isolation: the attempt-cap abandonment proof runs on a copied checkpoint database so the main resume-transfer path can still complete through fake-peer execution, materialization, and cleanup.

## Selftest proof

The active sync-domain selftest now proves:

- initial claim-only rows write no reclaim or abandon events;
- live steal still fails;
- expired reclaim still writes previous-owner reclaim events;
- a copied expired/reclaimed checkpoint with `claim_attempts=2` and `max_workorder_claim_attempts=2` becomes `abandoned` at the deterministic cap;
- abandon rows preserve earlier reclaim history;
- no staged bytes or receipts are written by abandon policy;
- a later worker cannot reclaim an abandoned row;
- the original non-abandoned checkpoint still executes, materializes, cleans up, and converges.

Recorded validation for this revision:

- Release CTest: `100% tests passed, 0 tests failed out of 27`.
- Packaged sync-domain selftest: `anonsync_core sync domain model selftest passed=248 failed=0`.
- ASAN/UBSAN sync-domain selftest: `anonsync_core sync domain model selftest passed=248 failed=0` with leak detection disabled.

## What is still missing

Rev0693 adds terminal abandon for retry-cap exhaustion, but it does not yet implement quarantine transitions for suspicious evidence drift, retry-at/backoff scheduling windows, daemon wake timing, production peer response acceptance, tombstone replay, conflict replay, or a UI-facing repair workflow for abandoned rows.

Rev0694 should extend the same policy surface with quarantine reasons and deterministic retry-at scheduling instead of adding network transport.

Filename structure to preserve for linked revisions: `Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip`.
