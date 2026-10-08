# Rev0675 — sync session checkpoint resume view

## Scope of this linked revision

Rev0675 is code-bearing. It promotes a new active C++ executable:

- `bin/rev0675/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3`

The revision closes a concrete restart-read gap left by rev0674. Rev0674 persisted completed fake-session evidence into SQLite, but the rows were still mostly write-time evidence: the C++ API could commit and reload-verify counts, yet there was no typed surface for a restarted process to ask, “what terminal work is complete, what work is pending, and does this database belong to the folder/device/peer context I am about to operate?”

Rev0675 adds that read-only seam.

## Mission fit

The heart of AnonSync is folder convergence under evidence-bound local truth. Durable evidence is not enough unless it can be consumed after restart without trusting caller-authored claims. Rev0675 makes the completed checkpoint inspectable as restart input while staying mutation-free.

The revised local proof path is now:

`source scan → destination scan → manifest diff → local apply plan → staged inspection → chunk request → peer schedule → peer-bound response batch → peer transfer round continuation → receipt-gated materialization → committed staging cleanup → destination rescan → content convergence → SQLite session checkpoint → read-only checkpoint verification → read-only resume view`

## Public C++ surface

Rev0675 adds:

- `SyncSessionCheckpointResumeViewOptions`
- `SyncSessionCheckpointResumeViewResult`
- `load_sync_session_checkpoint_resume_view`

The new API opens the checkpoint database read-only, loads the requested `session_id`, validates optional expected identities, and returns terminal/pending state for materialization, cleanup, and chunk receipts.

Key result fields include:

- `materialization_terminal_complete`
- `cleanup_terminal_complete`
- `all_chunk_receipts_committed_cleaned`
- `terminal_session_complete`
- `files_pending_materialization`
- `files_pending_cleanup`
- `chunk_receipts_pending_cleanup`
- `pending_materialization_paths`
- `pending_cleanup_paths`

## Audit/refactor performed

The audit finding was that rev0674 had a durable write seam but no restart-read seam. A real sync process needs to inspect the local database after process restart before touching the destination or staging roots. Without a typed reader, later resume logic would either duplicate ad-hoc SQL or trust the caller’s memory of the last completed run.

Rev0675 changes that by:

1. introducing a read-only checkpoint resume view;
2. requiring lowercase portable `session_id` identity;
3. optionally binding the loaded row to expected folder, source device, destination device, and peer IDs;
4. refusing database paths inside source, destination, or staging roots before SQLite open;
5. reporting terminal versus pending work without mutating filesystem state;
6. refactoring the checkpoint schema DDL into `ensure_sync_session_checkpoint_schema_or_throw`; and
7. replacing checkpoint reload verification SQL string concatenation with bound session-id queries.

This is intentionally a restart-read seam, not a scheduler. It should be the input to the next recovery step.

## Selftest coverage added

`--selftest-sync-domain-model` now requires the two-file fake peer session to persist a checkpoint and then load a resume view from it. The selftest requires:

- terminal resume-view loading from the checkpoint database;
- materialization terminal completion;
- cleanup terminal completion;
- every receipt row marked `committed-cleaned`;
- zero pending materialization paths;
- zero pending cleanup paths;
- row counts matching the fake session’s apply/file/chunk evidence;
- rejection of a mismatched expected destination device identity; and
- rejection of a resume-view database path inside the destination sync root before opening SQLite.

Recorded result: `anonsync_core sync domain model selftest passed=202 failed=0`.

## Validation

The release CTest suite reports `100% tests passed, 0 tests failed out of 27`.

The focused sanitizer selftest reports `anonsync_core sync domain model selftest passed=202 failed=0`.

The package validator is:

```bash
python3 tools/validate_rev0675_sync_session_resume_view.py
```

## Remaining ceiling

Rev0675 can read checkpoint rows as restart input, but it still does not claim production sync or recovery execution. Missing pieces include persisted in-flight request plans, peer assignments, accepted response batches, retry ownership, crash cleanup of abandoned staged files, tombstone/conflict branches in the fake session, peer/folder trust material, invite/share-key authority, authenticated transport, resource governance, and metadata/privacy policy.

The next best move is an actionable resume plan: combine the checkpoint resume view with `inspect_sync_staged_transfer` to reconstruct pending work, persist transfer-round state before every scheduled peer batch, and record cleanup transitions before and after filesystem mutation.
