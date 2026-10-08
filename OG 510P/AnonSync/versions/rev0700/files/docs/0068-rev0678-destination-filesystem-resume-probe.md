# Rev0678 — destination filesystem resume probe

## Scope of this linked revision

Rev0678 is code-bearing. It promotes a new active C++ executable:

- `bin/rev0678/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3`

Rev0677 made the checkpoint resume view verify exact manifest chunk coverage in SQLite. The next restart-safety gap was outside SQLite: a completed checkpoint could remain internally consistent while the destination folder changed after checkpoint commit. Rev0678 closes that local-truth gap by making the resume reader inspect the current destination filesystem against the persisted `destination_after` manifest before treating a session as terminal.

## Mission fit

The heart of AnonSync is evidence-bound peer-to-peer folder convergence. Restart evidence should not mean “the database once said convergence happened.” It should mean “the database is internally coherent and the destination tree still matches the committed destination-after manifest.”

The revised local proof path is now:

`source scan → destination scan → manifest diff → local apply plan → staged inspection → chunk request → peer schedule → peer-bound response batch → peer transfer round continuation → receipt-gated materialization → committed staging cleanup → destination rescan → content convergence → SQLite session checkpoint → manifest chunk-row persistence → read-only checkpoint verification → exact chunk receipt coverage guard → destination filesystem probe → read-only resume view`

## Public C++ surface

Rev0678 extends:

- `SyncSessionCheckpointResumeViewOptions`
- `SyncSessionCheckpointResumeViewResult`
- `load_sync_session_checkpoint_resume_view`

New option:

- `require_destination_filesystem_match`, enabled by default.

New resume view evidence:

- `destination_filesystem_verified`
- `destination_filesystem_entries_checked`
- `destination_filesystem_file_entries_checked`
- `destination_filesystem_tombstone_entries_checked`
- `destination_filesystem_missing_paths`
- `destination_filesystem_kind_mismatches`
- `destination_filesystem_content_mismatches`
- `destination_filesystem_drift_paths`

The SQLite checkpoint schema remains `rev0677-sync-session-checkpoint-v2`; rev0678 changes read-time restart semantics, not the durable row format.

## Audit/refactor performed

The audit finding was that rev0677 had strong durable integrity but an incomplete restart boundary. `load_sync_session_checkpoint_resume_view` could prove the checkpoint rows, chunk rows, and receipt rows were mutually consistent, yet it did not verify that files currently under `destination_root_path` still matched the persisted `destination_after` manifest.

Rev0678 adds a read-only filesystem probe that:

1. resolves every persisted `destination_after` path under the configured destination root;
2. rejects symlink ancestors and non-regular file substitutions for file entries;
3. hashes each destination file and compares size plus SHA-256 to the persisted manifest entry;
4. treats tombstone entries as absent-path expectations;
5. records bounded drift paths for missing, wrong-kind, or content-mismatched entries; and
6. folds `destination_filesystem_verified` into `terminal_session_complete` when `require_destination_filesystem_match` is enabled.

This is a restart-safety refactor. It keeps durable integrity separate from current-filesystem truth, while requiring both before a completed session is trusted by default.

## Selftest coverage added

`--selftest-sync-domain-model` now requires the two-file fake peer session resume view to prove:

- durable schema/manifest/chunk/receipt integrity from rev0677;
- `destination_filesystem_verified` for the `destination_after` manifest;
- zero missing destination paths;
- zero wrong-kind destination paths;
- zero destination content mismatches; and
- zero destination drift paths before terminal completion is trusted.

The selftest then mutates one materialized destination file after checkpoint commit and verifies that `load_sync_session_checkpoint_resume_view` rejects the terminal checkpoint by default. It also verifies the advisory mode: with `require_destination_filesystem_match=false`, the call succeeds while exposing one content mismatch and the drift path `docs/session-report.txt`.

Recorded result: `anonsync_core sync domain model selftest passed=207 failed=0`.

## Validation

The release CTest suite reports `100% tests passed, 0 tests failed out of 27`.

The focused sanitizer selftest reports `anonsync_core sync domain model selftest passed=207 failed=0`.

The package validator is:

```bash
python3 tools/validate_rev0678_destination_filesystem_resume_probe.py
```

## Remaining ceiling

Rev0678 still does not execute recovery from checkpoint rows. It can now reject drifted terminal checkpoints, but it does not persist request-plan rows, peer schedule rows, accepted response batches, retry ownership, cleanup transitions before and after filesystem mutation, tombstone/conflict branches inside the fake session, peer/folder trust material, authenticated transport, resource governance, or metadata/privacy policy.

The next best move is actionable non-terminal restart: persist request/schedule/batch rows before each transfer round, reconstruct pending staged transfers by combining SQLite rows with filesystem inspection, and then apply deterministic retry and cleanup policy.
