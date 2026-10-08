# Rev0680 — staging cleanup resume probe

## Scope of this linked revision

Rev0680 is code-bearing. It promotes a new active C++ executable:

- `bin/rev0680/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3`

Rev0679 made the checkpoint resume view verify that the live source and destination roots still match the persisted source and destination-after manifests. The next restart-safety gap was the staging root: a terminal checkpoint could prove SQLite cleanup rows while stale `.part` files or `.part.chunks` receipt directories had reappeared on disk. Rev0680 closes that local-truth gap with a read-only staging cleanup probe.

## Mission fit

AnonSync’s mission is evidence-bound peer-to-peer folder convergence. Resume evidence should bind four local planes before a terminal checkpoint is trusted by default:

1. durable SQLite rows are internally coherent;
2. every committed receipt still matches a persisted source manifest chunk;
3. the live source and destination roots still match the persisted source and destination-after manifests; and
4. the live staging root no longer contains committed transfer artifacts that SQLite says were cleaned.

The revised local proof path is now:

`source scan → destination scan → manifest diff → local apply plan → staged inspection → chunk request → peer schedule → peer-bound response batch → peer transfer round continuation → receipt-gated materialization → committed staging cleanup → destination rescan → content convergence → SQLite session checkpoint → manifest chunk-row persistence → read-only checkpoint verification → exact chunk receipt coverage guard → source filesystem probe → destination filesystem probe → staging cleanup probe → read-only resume view`

## Public C++ surface

Rev0680 extends:

- `SyncSessionCheckpointResumeViewOptions`
- `SyncSessionCheckpointResumeViewResult`
- `load_sync_session_checkpoint_resume_view`

New option:

- `require_staging_artifacts_cleaned`, enabled by default.

New resume view evidence:

- `staging_artifacts_verified`
- `staging_artifact_paths_checked`
- `staging_files_present`
- `staging_receipt_directories_present`
- `staging_artifact_kind_mismatches`
- `staging_artifact_paths`

The durable SQLite checkpoint schema remains `rev0677-sync-session-checkpoint-v2`; rev0680 changes read-time restart semantics, not the row layout.

## Audit/refactor performed

The audit finding was that rev0679’s terminal resume proof still treated staging cleanup as historical database evidence. That was too weak for restart intake: a process could see `staging_artifacts_cleaned=1` and committed-cleaned receipt rows while a stale receipt directory remained under the staging root.

Rev0680 adds `SyncStagingArtifactsProbe` and `verify_committed_staging_artifacts_absent_or_throw`, which:

1. selects cleaned file-result rows for the session;
2. joins each row to its apply intent and persisted source manifest entry;
3. requires the apply intent remote digest to match the source manifest entry digest;
4. reconstructs the expected staging path from the source path and remote entry digest;
5. requires the persisted absolute staging path to match the reconstructed staging path;
6. verifies that the expected `.part` file is absent;
7. verifies that the expected `.part.chunks` receipt directory is absent;
8. records bounded stale artifact paths for advisory mode; and
9. folds `staging_artifacts_verified` into `terminal_session_complete` when `require_staging_artifacts_cleaned` is enabled.

This is a restart-safety refactor. It keeps durable cleanup rows, current source truth, current destination truth, and current staging cleanup truth as separate evidence planes while requiring all of them by default.

## Selftest coverage added

`--selftest-sync-domain-model` now requires the two-file fake peer session resume view to prove:

- durable schema/manifest/chunk/receipt integrity from rev0677;
- source and destination filesystem verification from rev0679;
- `staging_artifacts_verified` for all cleaned materialized files;
- zero present staging files;
- zero present receipt directories;
- zero staging artifact kind mismatches; and
- zero staging artifact paths before terminal completion is trusted.

The selftest then recreates the receipt directory for `docs/session-report.txt` after checkpoint commit and verifies that `load_sync_session_checkpoint_resume_view` rejects the terminal checkpoint by default. Advisory mode is also tested: with `require_staging_artifacts_cleaned=false`, the call succeeds while reporting one stale receipt directory and its bounded relative artifact path.

Recorded result: `anonsync_core sync domain model selftest passed=212 failed=0`.

## Validation

The release CTest suite reports `100% tests passed, 0 tests failed out of 27`.

The focused sanitizer selftest reports `anonsync_core sync domain model selftest passed=212 failed=0`.

The package validator is:

```bash
python3 tools/validate_rev0680_staging_cleanup_resume_probe.py
```

## Remaining ceiling

Rev0680 still does not execute restart recovery. It can reject or report stale committed staging artifacts for terminal checkpoint views, but it does not persist request-plan rows, peer schedule rows, accepted response batches, retry ownership, cleanup transition rows before and after filesystem mutation, tombstone/conflict branches inside the fake session, peer/folder trust material, authenticated transport, resource governance, or metadata/privacy policy.

The next best move is executable restart planning: build a read-only pending-transfer reconstruction view that combines SQLite rows, source/destination probes, staging inspection, and receipt sidecars to decide whether each path should resume chunk transfer, retry, materialize, clean, quarantine, or be rejected as drifted.
