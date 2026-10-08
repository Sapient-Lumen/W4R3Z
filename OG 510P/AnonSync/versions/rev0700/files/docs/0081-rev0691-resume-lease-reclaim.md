# Rev0691 — resume transfer lease reclaim

Rev0691 is a code-bearing scheduler/restart hardening revision. Rev0690 split transfer workorder claim from execution and made live claims non-stealable. Rev0691 adds the missing deterministic time boundary: a `claimed` row now says when it was claimed, when its worker lease expires, and how many claim attempts have touched the row.

This keeps the mission pointed at **authorized folder convergence under evidence-bound local truth**. A restart daemon should not have to guess whether a worker was live, stale, or silently overwritten. The row itself now carries enough local evidence to reject live steals and reclaim only after expiry.

## Public surface

`SyncSessionCheckpointResumeTransferClaimOptions` and `SyncSessionCheckpointResumeTransferExecutionOptions` now expose:

- `workorder_claim_now_epoch`
- `worker_lease_seconds`
- `allow_expired_workorder_reclaim`

Their result structs now report top-level and per-file lease evidence:

- `claimed_at_epoch`
- `lease_expires_at_epoch`
- `workorder_rows_reclaimed`

The new fields are deliberately scoped to resume-transfer claim/execution. During audit, an accidental lease-field bleed into `SyncSessionCheckpointMaterializeResumeResult` was removed. Materialization remains about receipts, staged bytes, and checkpoint rows; it does not own transfer worker leases.

## SQLite workorder evidence

`sync_session_resume_transfer_workorders` now persists:

- `claimed_at_epoch INTEGER NOT NULL CHECK(claimed_at_epoch > 0)`
- `lease_expires_at_epoch INTEGER NOT NULL CHECK(lease_expires_at_epoch > claimed_at_epoch)`
- `claim_attempts INTEGER NOT NULL CHECK(claim_attempts > 0)`

Fresh claims are inserted with `claim_attempts=1`. Expired reclaims update the owner/lease/timing fields and advance `claim_attempts=claim_attempts+1`; they do not write staged bytes and do not alter chunk/request/peer/execution/staging evidence.

## Refactor/audit target

The refactor target was the rev0690 shared transfer workorder helper. It now performs one complete row lifecycle probe:

1. `INSERT OR IGNORE` a fresh `claimed` row with deterministic timing.
2. Reload the row by `session_id`, `path`, and `chunk_offset`.
3. Validate chunk length/hash, source action, request key, peer request key, schedule key, execution key, peer id, peer session id, staging path, work state, and lease timing.
4. Accept the row when the same worker/lease still owns a live claim.
5. Reject another worker while `lease_expires_at_epoch > workorder_claim_now_epoch`.
6. Reclaim only when the row is still `claimed` and `lease_expires_at_epoch <= workorder_claim_now_epoch`.

This makes the scheduler boundary deterministic without adding wall-clock behavior to tests. Tests pass explicit epochs, so a future daemon can plug in a real monotonic wall-clock source without changing the row semantics.

## Selftest coverage added

The active sync-domain model selftest now proves the following transfer-workorder sequence:

- worker `worker-charlie` claims rows at epoch `1000` with a `10`-second lease, producing `lease_expires_at_epoch=1010` and `claim_attempts=1`.
- worker `worker-echo` attempts execution at epoch `1005` and is rejected because the claim is still live.
- worker `worker-delta` reclaims at epoch `1010` with a new lease, producing `lease_expires_at_epoch=1025`, `claim_attempts=2`, and no staged bytes.
- stale owner `worker-charlie` is rejected after reclaim.
- reclaimed owner `worker-delta` executes the fake-peer transfer and completes the same durable rows.

The recorded focused result is `anonsync_core sync domain model selftest passed=245 failed=0`.

## Validation evidence

- Release CTest: `100% tests passed, 0 tests failed out of 27`.
- Packaged active binary sync-domain selftest: `anonsync_core sync domain model selftest passed=245 failed=0`.
- ASAN/UBSAN sync-domain selftest: `anonsync_core sync domain model selftest passed=245 failed=0`.
- Package validator: `rev0691 resume lease reclaim package validator passed`.

## Remaining ceiling

Rev0691 makes `claimed → expired → reclaimed` real enough for a deterministic restart worker. It still does **not** preserve previous-owner history. The row records current owner and attempt count, but it loses the old worker id, old lease id, old lease epoch, old claim window, and reason for takeover.

Rev0692 should add previous-owner transition evidence or an equivalent companion table, then prove explicit row-state decisions: `expired → reclaimed`, `expired → abandoned`, and `expired → quarantined`. That must happen before production peer response acceptance, because real networked peers need a reason trail for every stale or suspicious lease transition.

## Filename discipline

Linked revisions should continue using the filename structure requested for the session: `Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip`.
