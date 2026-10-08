# Rev0673 — committed staging cleanup

## Scope of this linked revision

Rev0673 is code-bearing. It promotes a new active C++ executable:

- `bin/rev0673/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3`

The revision closes a specific lifecycle gap left by rev0672: after the fake peer file-fetch session materialized staged bytes, the `.part.chunks` receipt sidecars remained in the staging root. Those receipts are useful before commit, but after a verified terminal materialization they need an explicit cleanup boundary so the cube does not accumulate unowned transfer evidence.

## Mission fit

The heart of AnonSync is folder convergence under evidence-bound local truth. Evidence has a lifecycle: it must gate unsafe mutation before commit, and it must be cleaned only after terminal state is proven. Rev0673 adds that post-commit gate for staged file transfers.

The revised fake-session path is now:

`source scan → destination scan → manifest diff → local apply plan → staged inspection → chunk request → peer schedule → peer-bound response batch → peer transfer round continuation → receipt-gated materialization → committed staging cleanup → destination rescan → content convergence`

## Public C++ surface

Rev0673 adds:

- `SyncStagedTransferCleanupOptions`
- `SyncStagedTransferCleanupResult`
- `cleanup_sync_staged_transfer_artifacts`

It also extends:

- `SyncFakePeerFileFetchSessionOptions` with `cleanup_staged_transfer_artifacts_after_materialization`;
- `SyncFakePeerFileFetchSessionFileResult` with cleanup receipt/directory counters and `staging_artifacts_cleaned`; and
- `SyncFakePeerFileFetchSessionResult` with aggregate cleanup receipt/directory counters.

## Audit/refactor performed

The audit finding was that rev0672 correctly gated materialization on receipt-backed staged bytes, but it did not define ownership of those receipts after commit. Leaving receipt sidecars around makes later resume/cleanup behavior ambiguous: a future daemon could confuse committed receipts with resumable transfer evidence, or the staging root could accumulate stale proof material indefinitely.

Rev0673 refactors cleanup into a separate C++ boundary rather than hiding deletion inside materialization. That keeps the mutation sequence inspectable:

1. materialization verifies and atomically renames the staged file;
2. cleanup verifies the terminal target independently;
3. cleanup refuses to run while the staged `.part` file exists;
4. cleanup removes only matching receipt files for the exact remote entry, apply key, and chunk tuple; and
5. cleanup prunes only empty directories below the staging root.

This is intentionally committed cleanup only. It does not attempt abandoned-transfer garbage collection yet, because abandoned cleanup needs durable age/session ownership policy.

## Selftest coverage added

`--selftest-sync-domain-model` now requires the two-file fake peer session to clean committed staging artifacts after convergence. The selftest requires:

- cleanup receipt count equal to the source manifest chunk count;
- each materialized file to report `staging_artifacts_cleaned`;
- each materialized file to remove at least one receipt and at least one staging directory; and
- the staging root to be empty after the session converges.

Recorded result: `anonsync_core sync domain model selftest passed=197 failed=0`.

## Validation

The release CTest suite reports `100% tests passed, 0 tests failed out of 27`.

The focused sanitizer selftest reports `anonsync_core sync domain model selftest passed=197 failed=0`.

The package validator is:

```bash
python3 tools/validate_rev0673_committed_staging_cleanup.py
```

## Remaining ceiling

Rev0673 cleans committed transfer receipts. It still does not claim production sync. Missing pieces include durable transfer/session state, persisted manifest/index rows, cleanup checkpoints, abandoned-transfer garbage collection, tombstone and conflict branches inside the fake session, peer/folder trust material, invite/share-key authority, protocol serialization, authenticated transport, resource governance, and metadata/privacy policy.

The next best move is still durable session state: persist manifests, apply intents, chunk requests, peer assignments, accepted response batches, receipt rows, materialization terminal states, and cleanup checkpoints.
