# Rev0690 — resume transfer claim split

## Scope of this linked revision

Rev0690 is code-bearing. It promotes a new active C++ executable:

- `bin/rev0690/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3`

Rev0689 identified the next real scheduler boundary: a transfer workorder row must be able to remain `claimed` after a process stops, without pretending that bytes were written. Rev0690 implements that boundary for the fake-peer resume-transfer slice and audits the row ownership bug that made the old boundary too weak.

## Mission fit

AnonSync’s mission is folder convergence under evidence-bound local truth. Restart transfer work is only trustworthy if the daemon can separate four facts:

1. work was planned from durable checkpoint/source evidence;
2. work was claimed by a specific worker/lease;
3. bytes and receipts were actually accepted; and
4. the row was completed by the same worker/lease that owned the claim.

Rev0690 adds the missing distinction between item 2 and item 3. The local proof path now includes:

`ResumeTransfer work-order planner → claim-only durable workorder rows → owned fake-peer transfer execution → receipt-gated materialization → committed staging cleanup`

This is not production transport and not lease reclamation. It is the crash-visible row boundary that production transport and lease reclamation should later consume.

## Public C++ surface

Rev0690 adds:

- `SyncSessionCheckpointResumeTransferClaimOptions`
- `SyncSessionCheckpointResumeTransferFileClaimResult`
- `SyncSessionCheckpointResumeTransferClaimResult`
- `claim_sync_session_checkpoint_resume_transfer_workorders`

The claim function consumes the rev0685/rev0688 transfer plan, opens SQLite read/write, inserts `claimed` rows for peer-assigned chunks, reloads the rows, verifies ownership/evidence, commits, and returns. It does not write staged bytes, receipt sidecars, `sync_session_chunk_receipts` rows, `sync_session_file_results` counters, or checkpoint aggregate counters.

## Audit/refactor performed

The audit target was `sync_session_resume_transfer_workorders`. The key finding was that rev0688 persisted useful row evidence, but the executor used `INSERT OR REPLACE`. Because the primary key is `(session_id, path, chunk_offset)`, a second worker could replace a live `claimed` row with a new worker id, worker lease id, lease epoch, and execution key. That was the opposite of a daemon-safe claim boundary.

Rev0690 refactors claim handling into one helper shared by the claim-only API and the fake-peer executor. The helper:

1. uses `INSERT OR IGNORE`, not `INSERT OR REPLACE`;
2. reloads the row after the insert attempt;
3. requires `work_state='claimed'`;
4. requires the same worker id, worker lease id, and worker lease epoch;
5. requires the same peer id, peer session id, request idempotency key, peer request key, schedule key, execution key, source action, chunk length/hash, and staging path; and
6. fails closed if another worker or lease already owns the row.

This is a small refactor, but it changes the trust shape: the executor can now consume a row previously claimed by the same worker/lease, while a different worker cannot silently steal it.

## Selftest coverage added

`--selftest-sync-domain-model` now proves that the resume-transfer slice:

- claims all missing chunks for `docs/session-report.txt` into `sync_session_resume_transfer_workorders`;
- records worker `worker-charlie` and deterministic `sync-resume-transfer-lease:v1:` evidence;
- commits the claim-only transaction;
- leaves `work_state='claimed'` rows without writing staged bytes or receipt sidecars;
- leaves the restart action router at `ResumeTransfer`, not `MaterializeStagedFile`;
- rejects worker `worker-echo` attempting to execute the live claimed rows under a different lease; and
- allows the original owning worker/lease to execute, write receipt-backed staged chunks, and mark the same rows `completed`.

Recorded result: `anonsync_core sync domain model selftest passed=242 failed=0`.

## Validation

The release CTest suite reports `100% tests passed, 0 tests failed out of 27`.

The packaged active binary selftest reports `anonsync_core sync domain model selftest passed=242 failed=0`.

The focused sanitizer selftest reports `anonsync_core sync domain model selftest passed=242 failed=0` with leak detection disabled.

The package validator is:

```bash
python3 tools/validate_rev0690_resume_claim_split.py
```

## Remaining ceiling

Rev0690 does not yet implement claimed-at timestamps, lease-expiry timestamps, retry-at timestamps, attempt counters, reclaim, abandon, or quarantine transitions. It also does not accept production peer bytes. The executor still uses the deterministic fake-peer source-root byte path after claim ownership is verified.

The next best code-bearing move is:

**Rev0691 — resume transfer lease expiry and reclaim policy**

Acceptance target:

1. extend or companion-map workorders with claimed-at/lease-expiry/retry/attempt/quarantine evidence;
2. prove fresh live claims cannot be reclaimed;
3. prove expired claims can be reclaimed by a new worker without deleting old evidence;
4. prove mismatched execution still fails; and
5. keep claim-only rows crash-visible until owned execution, reclaim, abandon, or quarantine changes their state.

## Session operating rule

For this working session, each linked turn should preserve the filename shape:

`Project-Name-rev####-YYYY.MM.DD.HH.MM-foobarnamesummaryhighlightcodename.zip`

The linked artifact should have the full filename written out as the link text. One link per turn is enough.

## Honest ceiling after rev0690

AnonSync is still not a production peer discovery system, encrypted peer protocol, persisted multi-worker scheduler, file watcher, daemon, UI, invite/share-key authority, or deployable privacy-preserving distributed sync product. Rev0690 makes claimed transfer rows real and non-stealable by mismatched workers, but abandoned claims are not yet reclaimable, real peer network responses are not accepted, overwrite replay is not persisted, tombstone/conflict branches are not restart-drained, and trust/privacy policy is still prose rather than product machinery.
