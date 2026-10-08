# Rev0681 — staging repair resume sweeper

## Scope of this linked revision

Rev0681 is code-bearing. It promotes a new active C++ executable:

- `bin/rev0681/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3`

Rev0680 made the checkpoint resume view fail closed when committed staging artifacts were present on disk. Rev0681 adds the first explicit recovery executor for that specific terminal case: `repair_sync_session_checkpoint_staging_artifacts`.

## Mission fit

AnonSync’s mission is evidence-bound peer-to-peer folder convergence. A restart path must not merely notice stale local sidecars; it must know when it is safe to repair them. Rev0681 keeps the proof planes separate:

1. durable SQLite checkpoint rows and chunk coverage must verify;
2. source and destination live files must still match persisted manifests;
3. staging artifacts must be derived from committed apply/manifest/chunk evidence;
4. receipt files must hash back to persisted `sync-chunk-receipt:v1:` idempotency keys; and
5. unexpected or tampered artifacts must remain on disk and fail closed.

The revised local proof path is now:

`source scan → destination scan → manifest diff → local apply plan → staged inspection → chunk request → peer schedule → peer-bound response batch → peer transfer round continuation → receipt-gated materialization → committed staging cleanup → destination rescan → content convergence → SQLite session checkpoint → manifest chunk-row persistence → read-only checkpoint verification → exact chunk receipt coverage guard → source filesystem probe → destination filesystem probe → staging cleanup probe → DB-bound terminal staging repair sweeper`

## Public C++ surface

Rev0681 adds:

- `SyncSessionCheckpointStagingRepairOptions`
- `SyncSessionCheckpointStagingRepairFileResult`
- `SyncSessionCheckpointStagingRepairResult`
- `repair_sync_session_checkpoint_staging_artifacts`

The repair API uses `load_sync_session_checkpoint_resume_view` as a prerequisite gate and disables only `require_staging_artifacts_cleaned` for the pre-repair advisory read. Durable integrity, source filesystem matching, destination filesystem matching, and terminal checkpoint evidence remain required by default.

## Audit/refactor performed

The audit finding was that rev0680’s staging cleanup probe was correct but passive. It could reject a terminal checkpoint if a stale committed `.part` file or `.part.chunks` directory appeared, but the caller still lacked a safe in-cube primitive for recovery.

Rev0681 adds a narrow repair/refactor boundary that:

1. opens the checkpoint database read-only;
2. requires the database path to stay outside source, destination, and staging roots;
3. loads the resume view with strict durable/source/destination proof and advisory staging proof;
4. enumerates materialized, committed-cleaned file rows joined to apply intents and source manifest entries;
5. reconstructs the expected staged-file path from the source path and persisted remote entry digest;
6. verifies that the destination target is regular and still matches checkpointed size/hash evidence;
7. removes a stale `.part` file only when it is regular, non-symlinked, and matches the checkpointed remote content hash;
8. removes a stale receipt only when its path is derived from the committed chunk row and its bytes hash back to the persisted receipt idempotency key;
9. removes the receipt directory only if expected receipt cleanup leaves it empty;
10. prunes empty staging parents; and
11. reloads the strict resume view to prove staging cleanliness after repair.

This is not a broad cleanup command. It is a terminal checkpoint repair primitive with explicit failure counters for unsafe artifacts, staged-file content mismatches, receipt content mismatches, and unexpected receipt-directory contents.

## Selftest coverage added

`--selftest-sync-domain-model` now recreates stale committed artifacts for `docs/session-report.txt` after a completed fake peer session checkpoint:

- a stale `.part` staged file containing the exact source bytes;
- a stale `.part.chunks` directory; and
- matching receipt files whose bytes hash to the persisted `sync-chunk-receipt:v1:` ids.

Strict resume loading rejects the checkpoint before repair. The new repair API then removes only those DB-bound artifacts, verifies `post_repair_staging_artifacts_clean`, and strict resume loading succeeds again.

The selftest also writes a tampered stale staged file and verifies that the repair API fail-closes, reports `staging_file_content_mismatches == 1`, and leaves the suspicious file on disk.

Recorded result: `anonsync_core sync domain model selftest passed=216 failed=0`.

## Validation

The release CTest suite reports `100% tests passed, 0 tests failed out of 27`.

The focused sanitizer selftest reports `anonsync_core sync domain model selftest passed=216 failed=0`.

The package validator is:

```bash
python3 tools/validate_rev0681_staging_repair_resume_sweeper.py
```

## Remaining ceiling

Rev0681 repairs only stale terminal staging artifacts already marked committed-cleaned in SQLite. It still does not reconstruct non-terminal transfer work, persist request/schedule/batch rows before each peer round, coordinate live worker ownership, recover tombstone/conflict branches in the fake session, define peer/folder trust material, authenticate transport, reserve disk, or encode metadata/privacy policy.

The next best move is an actionable pending-transfer reconstruction view: combine durable rows, source/destination/staging probes, staged inspection, receipt sidecars, request state, and peer schedule state to decide per path whether to resume, retry, materialize, clean, quarantine, or reject.
