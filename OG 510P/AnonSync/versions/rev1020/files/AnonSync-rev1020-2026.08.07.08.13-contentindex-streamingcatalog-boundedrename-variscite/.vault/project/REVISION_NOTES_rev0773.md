# AnonSync rev0773 — transaction-scoped durable payload authority

## Heart of this revision

AnonSync treats a transport receipt as untrusted input, not convergence authority. Durable peer-ingress payload bytes become usable evidence only when their exact canonical frame, digest, queue identity, reviewed schema, and database snapshot are bound to one guard-owned SQLite transaction. A database handle, a prior schema check, or a successful insert is not enough: the evidence must still be true in the exact snapshot that consumes it and must commit atomically with its queue parent.

## Correctness and refactor work

- Replaced the payload store's comment-only “caller is in the right transaction” convention with a typed `SyncSqliteTransaction` capability.
- Added guard-lifetime `SyncSqliteTransactionAuthority` leases. They bind one RAII owner state to one SQLite handle and revoke on commit, rollback, destruction, an observed out-of-band commit, or automatic rollback. SQLite exposes no native transaction-generation identifier, so raw transaction-control SQL remains forbidden while a guard exists.
- Split authority into active transaction, established `main` snapshot, and `main` write-transaction checks using `sqlite3_get_autocommit()` plus `sqlite3_txn_state()`.
- Made payload schema capabilities snapshot-scoped instead of reusable handle-scoped tokens. A capability verified in transaction A cannot authorize transaction B on the same connection.
- Replaced arbitrary BEGIN SQL and adopt-after-BEGIN construction with typed `Deferred`, `Immediate`, and `Exclusive` modes. The write-lock helper now creates and returns the RAII transaction owner itself, eliminating the exception window between raw BEGIN and owner construction.
- Propagated the exact transaction guard through payload load/store and destructive retention selection.
- Bound payload schema catalogs, structural PRAGMAs, data reads/writes, schema creation, and lifecycle payload projections explicitly to `main`; TEMP look-alikes cannot redirect durable-evidence decisions.
- Upgraded column verification from ambient `table_info` to `main.table_xinfo`, including rejection of hidden/generated look-alikes.
- Corrected lifetime ordering so the transaction owner is destroyed before the connection/schema authority lease is released.
- Made `commit()` refuse a revoked guard and made rollback/destruction avoid touching a transaction boundary the guard has already observed as lost; this prevents stale owner cleanup from manufacturing errors or rolling back later work.
- Added a deterministic 38-check source-shape audit to keep the reviewed capability, namespace, transaction, and ownership boundaries from silently regressing.

## Adversarial proof added

The focused runtime suite now covers exact parent+payload commit and rollback, cross-connection and stale-generation rejection, read-snapshot rejection for writes, TEMP same-name tables, same-length BLOB corruption, digest/identity contradiction, foreign-key cascade/orphan behavior, raw-boundary lease revocation, and process termination via `_exit(0)` both before and after commit followed by database reopen. The crash probes intentionally bypass C++ destructors.

## Audit conclusion

The severe defect was an authority mismatch: the payload helper accepted a database pointer after a separately performed schema check and relied on comments to guarantee transaction co-location. The same pointer could host many later transactions, and SQLite resolves unqualified names through TEMP before `main`. This allowed code shape that looked transaction-safe while remaining vulnerable to stale-capability reuse, accidental autocommit separation, and namespace redirection.

The correction is structural rather than procedural: exact transaction ownership, exact snapshot authority, explicit durable schema, and process-crash reconstruction are now part of the API and tests.

## Measured source delta from the last verifiable parent

- Source parent: **rev0771**. The previously linked rev0772 archive was not present in the shared filesystem, so public numbering advances to rev0773 while lineage records the verifiable source parent explicitly.
- Changed active files: **13**.
- Added lines: **1,245**.
- Removed lines: **291**.
- New adversarial/static audit code is included in those counts.

## Validation summary

- Parent rev0771 baseline, independently rebuilt before edits: **40/40 CTest tests passed**.
- Current incremental tree: **40/40 passed**.
- Fresh Debug tree: **40/40 passed**.
- Fresh Release tree: **40/40 passed**.
- Focused repeat-until-fail: **80/80 executions passed** across payload store, retention integrity, schema attestation, and SQLite support.
- Direct focused checks: payload store **46 checks**, SQLite support **61 passed / 0 failed**, lifecycle **49 passed / 0 failed**.
- Current-source GCC ASan/UBSan tree: **39/39 non-domain tests passed** with leak detection and halt-on-error enabled; the domain-model sanitizer test exceeded the cloudtainer's per-command execution ceiling and is recorded as incomplete rather than success.
- `clang-format` was unavailable in this cloudtainer; that optional check is recorded as unavailable, not promoted to success.

## Remaining seam

Process crash atomicity is not the same as power-loss durability. The next boundary should combine transaction-control ownership with SQLite VFS fault injection around WAL writes, syncs, directory metadata, and checkpoints. A connection-level transaction authorizer can then deny raw `BEGIN`/`COMMIT`/`ROLLBACK` outside the typed guard, closing the last generation-observation limitation of the public SQLite transaction-state APIs.
