# Rev0674 — durable fake-session checkpoint

## Scope of this linked revision

Rev0674 is code-bearing. It promotes a new active C++ executable:

- `bin/rev0674/anonsync_core-linux-x86_64-gcc-openssl3-sqlite3`

The revision closes a concrete restart-readiness gap left by rev0673: the fake peer file-fetch session could converge and clean committed staging receipts, but the completed session evidence still existed only as in-memory C++ result structs and already-cleaned filesystem side effects. Rev0674 adds a first durable checkpoint boundary for completed fake sessions.

## Mission fit

The heart of AnonSync is folder convergence under evidence-bound local truth. Local truth cannot stay only in memory if the product is meant to survive process restart. Rev0674 writes completed fake-session evidence to SQLite using WAL mode and `synchronous=FULL`, then reopens the database read-only and verifies the checkpoint idempotency key plus row counts.

The revised local proof path is now:

`source scan → destination scan → manifest diff → local apply plan → staged inspection → chunk request → peer schedule → peer-bound response batch → peer transfer round continuation → receipt-gated materialization → committed staging cleanup → destination rescan → content convergence → SQLite session checkpoint → read-only checkpoint verification`

## Public C++ surface

Rev0674 adds:

- `SyncSessionCheckpointOptions`
- `SyncSessionCheckpointResult`
- `persist_sync_fake_peer_session_checkpoint`

The new API takes `SyncFakePeerFileFetchSessionOptions` and `SyncFakePeerFileFetchSessionResult`, validates identity and aggregate evidence, and persists a completed checkpoint under a deterministic `sync-session-checkpoint:v1:` idempotency key.

## Checkpoint schema content

The rev0674 SQLite checkpoint stores:

- one `sync_session_checkpoints` row for the completed session;
- three manifest snapshots: source, destination-before, and destination-after;
- manifest entry rows with entry and publisher-neutral version digests;
- local apply intent rows;
- per-file transfer/materialization result rows;
- materialization idempotency key rows;
- cleanup idempotency key rows; and
- per-chunk receipt idempotency rows marked `committed-cleaned` when committed cleanup ran.

The checkpoint function rejects metadata database paths inside the source root, destination root, or staging root. That audit/refactor matters because a local sync database must not be scanned as user content, replicated to peers, or confused with staged transfer debris.

## Audit/refactor performed

The audit finding was that rev0673 had solved terminal cleanup but not restart observability. After cleanup, the receipts were intentionally gone, and the only aggregate proof of what happened was the caller-held `SyncFakePeerFileFetchSessionResult`. That is not a product-shaped recovery boundary.

Rev0674 refactors the terminal fake-session result into a durable checkpoint seam rather than hiding it in a test-only JSON file or in the existing authorization replay ledger. The seam is sync-domain-specific and records sync-native evidence:

1. manifest identity and content convergence digests;
2. apply intent idempotency keys;
3. materialization and cleanup terminal keys;
4. receipt idempotency rows for every transferred chunk; and
5. reload verification after commit.

This is intentionally completed-session checkpointing only. It does not claim resumable in-flight scheduling yet, because that requires persisting request plans, peer assignments, accepted batches, and cleanup state transitions before each crash point.

## Selftest coverage added

`--selftest-sync-domain-model` now requires the two-file fake peer session to persist and reload a SQLite checkpoint after convergence. The selftest requires:

- checkpoint transaction commit;
- read-only reload verification;
- file result row count equal to materialized files;
- apply intent row count equal to considered apply entries;
- receipt row count equal to the source manifest chunk count; and
- rejection of a checkpoint database inside the destination sync root.

Recorded result: `anonsync_core sync domain model selftest passed=199 failed=0`.

## Validation

The release CTest suite reports `100% tests passed, 0 tests failed out of 27`.

The focused sanitizer selftest reports `anonsync_core sync domain model selftest passed=199 failed=0`.

The package validator is:

```bash
python3 tools/validate_rev0674_sync_session_checkpoint.py
```

## Remaining ceiling

Rev0674 persists completed fake-session evidence. It still does not claim production sync. Missing pieces include recovery from checkpoint rows, durable in-flight request/schedule/batch state, cleanup state transitions before and after filesystem mutation, abandoned-transfer garbage collection, tombstone and conflict branches inside the fake session, peer/folder trust material, invite/share-key authority, protocol serialization, authenticated transport, resource governance, and metadata/privacy policy.

The next best move is restart consumption: use the checkpoint rows plus staged-transfer inspection to reconstruct pending work, prove idempotent resume for partially transferred files, and record cleanup transitions as durable state rather than merely completed-session evidence.
