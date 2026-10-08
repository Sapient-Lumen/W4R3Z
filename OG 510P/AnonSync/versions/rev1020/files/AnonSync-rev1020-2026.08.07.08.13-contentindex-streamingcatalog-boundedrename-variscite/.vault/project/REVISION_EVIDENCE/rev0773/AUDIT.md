# AnonSync rev0773 — durable payload transaction-authority audit

## Mission boundary

A peer-ingress payload is convergence evidence only when all of the following are simultaneously true:

1. its canonical frame decodes and binds the submitted queue identity and payload digest;
2. its exact reviewed payload schema is present in the durable `main` database;
3. the schema check and row consumption belong to one explicit SQLite snapshot;
4. a payload insert and its queue parent belong to one exact write transaction;
5. under the single-owner transaction-control rule, the authority cannot be replayed against a later transaction on the same `sqlite3*`;
6. committed state reconstructs after process death without relying on C++ destructors.

The previous API proved some of these properties through caller convention, comments, and pointer identity. That was not a sufficient authority boundary.

## Severe findings corrected

### 1. Comment-only transaction co-location

`store_or_verify_peer_transport_ingress_payload_or_throw()` accepted a connection pointer but no transaction object. Correctness depended on every caller remembering to place parent-row and payload-row work inside the same transaction. A future or exceptional call path could silently split the two into separate autocommit commits.

**Correction:** load/store/retention APIs consume the exact `SyncSqliteTransaction` guard. Writes require `authorizes_write(db)`; reads require a verified capability tied to the same live snapshot.

### 2. Reusable handle-scoped schema capability

The previous payload schema capability was effectively “this `sqlite3*` was checked once.” A connection pointer is not a generation: one handle can host arbitrarily many snapshots and write transactions.

**Correction:** `VerifiedPeerTransportIngressPayloadStoreSchema` carries a weak, guard-lifetime transaction authority. Commit, rollback, destruction, an observed raw commit, or automatic rollback permanently revokes all copies. This is a C++ owner-generation, not a SQLite-supplied transaction identifier.

### 3. TEMP-first namespace ambiguity

SQLite resolves unqualified object names through TEMP before `main`. Some structural probes and payload queries therefore expressed ambient namespace intent even though they were making durable-state decisions.

**Correction:** payload `sqlite_schema` queries, `table_xinfo`, `foreign_key_list`, table creation, index creation, row reads/writes, shared persistent table probes, and lifecycle payload aggregates are explicitly `main`-qualified. A new static audit rejects unqualified lifecycle payload accesses.

### 4. Raw BEGIN followed by RAII adoption

The write-lock helper previously began a transaction and then constructed an owner that adopted it. An allocation or argument-construction exception in that interval could leave a live transaction with no owner.

**Correction:** transaction mode is a closed enum, and the helper constructs `std::unique_ptr<SyncSqliteTransaction>` directly. No arbitrary BEGIN string or adoption constructor remains.

### 5. Stale lease revival after an out-of-band boundary

A lease that only checked `sqlite3*` plus “a transaction is active” could become valid again if the original transaction ended and a later transaction began on the same handle.

**Correction:** authority is backed by one shared guard state. Observing autocommit permanently flips that state inactive, and later transactions cannot revive it through the supported API. `commit()` refuses a revoked owner; rollback and destruction disarm without issuing transaction SQL once the owned boundary is known to be gone. SQLite has no public transaction-generation identifier, so an unobserved raw COMMIT+BEGIN pair remains forbidden API misuse and is not claimed to be detectable.

### 6. Rollback after releasing connection authority

RAII destruction is reverse declaration order. A transaction owner declared before its connection/schema lease would roll back after releasing the mutex/authorizer ownership that made the connection safe.

**Correction:** connection/schema authority leases are declared first and transaction owners second, so transaction completion/destruction occurs while connection authority remains held. Both static audits verify the ordering.

## Runtime evidence

The tests exercise:

- typed deferred, immediate, and exclusive transactions;
- exact-handle, guard-lifetime, and stale-lease checks;
- commit, rollback, destructor, and observed raw-boundary revocation;
- TEMP-only and same-name table/column shadows;
- exact parent+payload commit versus rollback;
- stale schema capability and cross-connection rejection;
- rejection of a deferred/read transaction as write authority;
- canonical-frame identity/digest mismatch and contradictory duplicate evidence;
- same-length durable BLOB tamper detection and recovery;
- parent cascade and orphan foreign-key rejection;
- `_exit(0)` immediately after commit, followed by reopen and exact reconstruction;
- `_exit(0)` before commit, followed by reopen proving that neither parent nor payload survived;
- WAL with `synchronous=FULL` and final `integrity_check`.

## Static audit evidence

`tools/audit_peer_payload_transaction_authority.py` currently enforces 38 reviewed source-shape invariants, including:

- typed transaction modes and no transaction adoption;
- owner construction inside the write-lock helper;
- exact transaction/snapshot/write authority APIs;
- transaction-before-lease destruction order;
- `main`-qualified schema/data access;
- transaction-scoped retention;
- process-crash, TEMP-shadow, stale-capability, and raw-boundary test markers;
- absence of production raw BEGIN handoff in peer lifecycle;
- absence of unqualified lifecycle payload-table access.

`tools/audit_sqlite_authorizer_ownership.py` independently verifies connection-level authorizer ownership and retained schema-authority lease lifetimes.

## Remaining limitations and risks

1. **Process crash is not power failure.** `_exit(0)` proves atomic reconstruction across process death but does not simulate torn writes, lost cache flushes, or filesystem lies. A test VFS or syscall fault layer is still needed.
2. **SQLite exposes state, not a native transaction generation ID.** If hostile code executes raw COMMIT and raw BEGIN between all checks, public `sqlite3_get_autocommit()`/`sqlite3_txn_state()` cannot identify that invisible boundary. The peer-ingress source audit forbids raw boundaries, and connection ownership serializes use, but the stronger future design is to make the connection authorizer deny `SQLITE_TRANSACTION`/`SQLITE_SAVEPOINT` actions unless the typed guard temporarily holds a transaction-control token.
3. **Concurrent autocommit inspection has an API caveat.** SQLite documents `sqlite3_get_autocommit()` as undefined if another thread changes autocommit concurrently. The audited path retains the FULLMUTEX connection authority lease through transaction completion; that ownership must remain non-optional.
4. **WAL is a local-filesystem design.** The database path must not be placed on unsupported network filesystems merely because process-crash tests pass locally.
5. **Raw transaction code remains elsewhere in the cube.** This revision intentionally hardens peer-ingress payload authority. The large checkpoint/replay modules still contain hand-written BEGIN/COMMIT/ROLLBACK patterns and should migrate by invariant-owned slices rather than a mechanical global replacement.
6. **Translation-unit debt remains material.** `src/sync_domain.cpp` is about 24.5k lines and `src/sync_peer_ingress_lifecycle.cpp` about 3.8k lines. Fresh builds are slow, review locality is poor, and transaction policy is harder to prove. Future extraction should follow state-machine/repository/transaction-authority/operator-projection ownership.

## Refactor direction

The next high-leverage extraction is a peer-ingress repository object that owns, in one scope:

- the connection authority lease;
- the typed transaction owner;
- the exact schema/snapshot capability;
- queue and payload repositories;
- commit/rollback and crash-point instrumentation.

That object would make invalid destruction order and partial capability propagation unrepresentable. After that, a deterministic SQLite VFS fault harness should enumerate crash points around WAL append, WAL sync, database checkpoint write, database sync, and WAL reset, comparing reopened state to a small executable transition oracle.
