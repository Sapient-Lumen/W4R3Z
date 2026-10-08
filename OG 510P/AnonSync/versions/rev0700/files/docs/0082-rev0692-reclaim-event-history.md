# Rev0692 — reclaim event history

Rev0692 is code-bearing. Rev0691 made expired resume-transfer claims reclaimable, but the act of reclaiming still overwrote the live workorder row's owner fields. That was operationally useful but audit-thin: after takeover, the row could tell you the current owner and attempt count, but not who was displaced, which lease expired, or why the transition happened.

Rev0692 adds durable previous-owner transition evidence for expired transfer-claim takeover. The active mission remains **authorized folder convergence under evidence-bound local truth**: a restart daemon should be able to resume or reject work without trusting memory, logs, or a central service, and a reviewer should be able to reconstruct why ownership changed.

## Public surface

The resume-transfer claim and execution result structs now expose:

- `workorder_reclaim_events_written` at the top-level claim result.
- `workorder_reclaim_events_written` per claimed file.
- `workorder_reclaim_events_written` at the top-level execution result.
- `workorder_reclaim_events_written` per executed file.

These counters are intentionally narrow. They only report companion transition rows written during expired-claim takeover. A same-owner live execution that consumes an already reclaimed row reports zero new reclaim events, even though it may complete the reclaimed workorder rows.

## SQLite transition evidence

Rev0692 adds a companion table:

- `sync_session_resume_transfer_workorder_reclaim_events`

Each event row is keyed by `session_id`, `path`, `chunk_offset`, and `reclaim_attempt`. It records the immutable chunk/source-action evidence plus the full previous and new ownership windows:

- `previous_worker_id`
- `previous_worker_lease_id`
- `previous_worker_lease_epoch`
- `previous_claimed_at_epoch`
- `previous_lease_expires_at_epoch`
- `new_worker_id`
- `new_worker_lease_id`
- `new_worker_lease_epoch`
- `new_claimed_at_epoch`
- `new_lease_expires_at_epoch`
- `reclaim_reason='expired-lease'`

The event references the durable workorder row and is inserted in the same transaction as the expired-row ownership update. The current row still advances to the new owner; the companion event preserves the displaced owner and reason trail.

## Audit/refactor target

The audit target was the rev0691 reclaim helper. The important refactor was to keep the claim/probe/reclaim decision centralized while adding a second durable write at exactly one point: after the expired row is successfully updated and before the transaction commits. This avoids duplicating reclaim policy across claim-only and execution paths.

The helper now performs this sequence:

1. Insert-or-ignore a fresh claimed workorder row.
2. Reload and validate chunk, request, peer, execution, source-action, staging, state, and lease evidence.
3. Reject live foreign ownership.
4. If the row is expired and reclaim is allowed, update the owner/lease/timing fields and increment `claim_attempts`.
5. Insert one `sync_session_resume_transfer_workorder_reclaim_events` row carrying previous-owner and new-owner evidence with reason `expired-lease`.

Both claim-only reclaim and executor-side reclaim share this helper, so the audit event semantics stay identical.

## Selftest coverage added

The active sync-domain model selftest still proves the rev0691 worker sequence, and now also proves the event trail:

- Initial worker `worker-charlie` claim writes no reclaim events.
- Live steal attempt by `worker-echo` before lease expiry writes no reclaim events.
- Expired reclaim by `worker-delta` writes one reclaim event per assigned chunk.
- Each event records previous owner `worker-charlie`, previous claim window `1000 → 1010`, new owner `worker-delta`, new claim window `1010 → 1025`, `reclaim_attempt=2`, and `reclaim_reason='expired-lease'`.
- Later execution by `worker-delta` completes the workorder rows without writing duplicate reclaim events.
- Completed workorder rows still preserve the companion reclaim event history.

The recorded focused result is `anonsync_core sync domain model selftest passed=245 failed=0`.

## Validation evidence

- Release CTest: `100% tests passed, 0 tests failed out of 27`.
- Packaged active binary sync-domain selftest: `anonsync_core sync domain model selftest passed=245 failed=0`.
- ASAN/UBSAN sync-domain selftest: `anonsync_core sync domain model selftest passed=245 failed=0`.
- Package validator: `rev0692 reclaim event history package validator passed`.

## Remaining ceiling

Rev0692 closes the previous-owner audit hole for expired reclaims. It still does **not** implement retry-at scheduling, retry caps, explicit `abandoned` or `quarantined` workorder states, or a policy engine that decides when expiry should become reclaim versus abandon versus quarantine.

Rev0693 should turn reclaim history into policy: add explicit terminal/holding states or a companion policy table for abandoned and quarantined rows, then prove that suspicious or over-budget claims stop safely without deleting the original workorder or its transition history.

## Filename discipline

Linked revisions should continue using the filename structure requested for the session: `Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip`.
