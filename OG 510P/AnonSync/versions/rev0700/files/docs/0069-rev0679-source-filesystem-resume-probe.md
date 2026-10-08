# Rev0679 — source filesystem resume probe

## Scope of this linked revision

Rev0679 is code-bearing. It promotes a new active C++ executable:

- `bin/rev0679/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3`

Rev0678 made the completed checkpoint resume view verify that the current destination tree still matches the persisted `destination_after` manifest. The next restart-safety gap was asymmetric live truth: the same reader still trusted the persisted `source` manifest without checking that the current source root still provides the bytes and tombstone state that the checkpoint says the peer session used. Rev0679 closes that gap and refactors the destination-specific checker into one reusable manifest-filesystem probe.

## Mission fit

AnonSync’s mission is evidence-bound peer-to-peer folder convergence. Resume evidence should bind three layers before a terminal checkpoint is trusted by default:

1. durable SQLite rows are internally coherent;
2. every committed receipt still matches a persisted source manifest chunk; and
3. the live source and destination roots still match the persisted source and destination-after manifests.

The revised local proof path is now:

`source scan → destination scan → manifest diff → local apply plan → staged inspection → chunk request → peer schedule → peer-bound response batch → peer transfer round continuation → receipt-gated materialization → committed staging cleanup → destination rescan → content convergence → SQLite session checkpoint → manifest chunk-row persistence → read-only checkpoint verification → exact chunk receipt coverage guard → source filesystem probe → destination filesystem probe → read-only resume view`

## Public C++ surface

Rev0679 extends:

- `SyncSessionCheckpointResumeViewOptions`
- `SyncSessionCheckpointResumeViewResult`
- `load_sync_session_checkpoint_resume_view`

New option:

- `require_source_filesystem_match`, enabled by default.

New resume view evidence:

- `source_filesystem_verified`
- `source_filesystem_entries_checked`
- `source_filesystem_file_entries_checked`
- `source_filesystem_tombstone_entries_checked`
- `source_filesystem_missing_paths`
- `source_filesystem_kind_mismatches`
- `source_filesystem_content_mismatches`
- `source_filesystem_drift_paths`

The destination fields from rev0678 remain, but the implementation now uses the shared `SyncManifestFilesystemProbe` and `verify_manifest_filesystem_or_throw` for both the `source` role and the `destination_after` role. The durable SQLite checkpoint schema remains `rev0677-sync-session-checkpoint-v2`; rev0679 changes read-time restart semantics, not the row layout.

## Audit/refactor performed

The audit finding was that rev0678’s restart reader had two different trust levels for the two trees involved in a transfer. The destination tree was checked against persisted post-session evidence, while the source tree was assumed to remain true once its manifest rows and chunk receipts were coherent. That was acceptable for a historical terminal proof, but too weak for a restart boundary that future non-terminal recovery will use as live input.

Rev0679 refactors the read-time filesystem check into a role-bound helper that:

1. selects persisted manifest rows by `session_id` and role;
2. resolves every path under the caller-provided root;
3. rejects symlink ancestors and non-regular substitutions for file rows;
4. hashes current file bytes and compares size plus SHA-256 to the manifest row;
5. treats tombstones as absent-path expectations;
6. records bounded drift paths for missing, wrong-kind, or content-mismatched entries; and
7. folds source and destination probe booleans into `terminal_session_complete` when their strict options are enabled.

This keeps durable database integrity, receipt coverage, source live truth, and destination live truth as separate evidence planes while requiring all of them by default.

## Selftest coverage added

`--selftest-sync-domain-model` now requires the two-file fake peer session resume view to prove:

- durable schema/manifest/chunk/receipt integrity from rev0677;
- `source_filesystem_verified` for the persisted source manifest;
- `destination_filesystem_verified` for the persisted destination-after manifest;
- zero source and destination missing paths;
- zero source and destination wrong-kind paths;
- zero source and destination content mismatches; and
- zero source and destination drift paths before terminal completion is trusted.

The selftest mutates one materialized destination file after checkpoint commit and verifies that strict resume loading rejects it. It then restores the destination file, mutates one source file after checkpoint commit, and verifies that strict resume loading rejects the source drift. Advisory mode is tested for both probes: disabling the relevant strict option permits the view to load while reporting one content mismatch and the drift path `docs/session-report.txt`.

Recorded result: `anonsync_core sync domain model selftest passed=209 failed=0`.

## Validation

The release CTest suite reports `100% tests passed, 0 tests failed out of 27`.

The focused sanitizer selftest reports `anonsync_core sync domain model selftest passed=209 failed=0`.

The package validator is:

```bash
python3 tools/validate_rev0679_source_filesystem_resume_probe.py
```

## Remaining ceiling

Rev0679 still does not execute restart recovery. It can now reject or report source/destination drift for terminal checkpoint views, but it does not persist request-plan rows, peer schedule rows, accepted response batches, retry ownership, cleanup transition rows before and after filesystem mutation, tombstone/conflict branches inside the fake session, peer/folder trust material, authenticated transport, resource governance, or metadata/privacy policy.

The next best move remains actionable non-terminal restart: persist request/schedule/batch rows before each transfer round, reconstruct pending staged transfers by combining SQLite rows with source/destination/staging filesystem inspection, and then apply deterministic retry and cleanup policy.
