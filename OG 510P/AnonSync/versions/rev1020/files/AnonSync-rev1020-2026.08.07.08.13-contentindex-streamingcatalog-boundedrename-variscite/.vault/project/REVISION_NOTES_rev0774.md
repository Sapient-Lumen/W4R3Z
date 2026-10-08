# AnonSync rev0774 — typed transaction-stack generation authority

## Heart of the mission

AnonSync is not fundamentally a transport library. It is a convergence engine
whose transitions must be justified by durable, reconstructible evidence.
Transport bytes, callback completion, a worker token, a connection pointer, and
SQLite success codes are observations. Authority exists only when the exact
claim generation, canonical content, reviewed schema, snapshot, and durable
writer outcome agree at the point of use.

Rev0774 applies that rule one layer lower: the SQLite transaction stack itself
must not be ambient mutable state. The transaction that verifies evidence and
the transaction that commits it must be the same exact generation.

## Severe correctness gap corrected

Rev0773 introduced a typed RAII transaction owner and guard-lifetime authority,
but SQLite's public state APIs expose whether a transaction is active, not
which transaction it is. Unsupported code could execute raw `COMMIT` and raw
`BEGIN` between observations. Pointer identity plus `autocommit == false` could
then describe a later transaction and let a stale owner appear current.

Savepoints made the bypass wider: an outermost `SAVEPOINT` behaves like `BEGIN
DEFERRED`, and releasing the outermost savepoint behaves like `COMMIT`.
Protecting only literal BEGIN/COMMIT/ROLLBACK strings would therefore be
incorrect.

## Implementation

1. The AnonSync-owned authorizer now intercepts `SQLITE_TRANSACTION` and
   `SQLITE_SAVEPOINT` actions. Savepoints are denied until a typed nested-scope
   owner exists.
2. A typed boundary arms one single-use permit for BEGIN, COMMIT, or ROLLBACK.
   The callback consumes the permit before delegating to policy; malformed,
   throwing, repeated, mismatched, and `SQLITE_IGNORE` outcomes fail closed.
3. The connection state allocates a monotonically increasing transaction
   generation. Boundary proof binds process salt, connection incarnation,
   authorizer generation, and transaction generation.
4. Successful typed BEGIN retains one recursive entry on the FULLMUTEX database
   mutex for the complete generation. Other threads cannot interleave on the
   same handle or replace its callback before finalization.
5. Commit and rollback revalidate exact proof, challenge callback ownership,
   consume one permit, verify autocommit restoration, clear the active
   generation, revoke all copied authority, and release the mutex once.
6. Retryable COMMIT failure retains authority only if the exact transaction and
   bridge remain current.
7. Destructor rollback attempts only the exact fenced generation. After an
   alien callback replacement it deliberately avoids a raw fallback because
   that could roll back a newer transaction.
8. Schema recovery detects existing AnonSync client data and reinstalls the
   restrictive schema bridge before compiling typed BEGIN.

## Refactor and audit

Transaction implementation moved from the generic  SQLite support file into
`src/sync_sqlite_transaction.cpp`. The authorizer bridge remains the sole owner
of client data, callback installation, permit state, and connection-level
proof. This is an invariant-owned split, not a cosmetic file split.

`tools/audit_sqlite_transaction_stack_authority.py` enforces 45 reviewed source
shape checks and emits a full raw-boundary inventory. The older payload and
authorizer audits were refactored to inspect the new owner files. All three
pass.

The inventory finds 95 legacy raw boundaries outside the new owner. This is
migration debt, not proof: 45 occur in the 24,523-line `sync_domain.cpp`, 15 in
reporting selftests, 15 in the SQLite replay ledger, and 20 across smaller
modules.

## Adversarial proof

The revised authority suite tests:

- raw deferred, immediate, and exclusive BEGIN denial;
- a BEGIN prepared before bridge installation and reauthorized at step;
- outermost and nested SAVEPOINT, RELEASE, and ROLLBACK TO denial;
- raw COMMIT, END, and ROLLBACK denial during a typed generation;
- exact typed commit and rollback;
- malformed policy and `SQLITE_IGNORE` fail-closed behavior;
- refusal to reinstall owned authority inside a live transaction;
- alien callback replacement invalidating typed commit;
- a stale destructor preserving a later alien transaction rather than falsely
  rolling it back; and
- a competing thread blocked from same-handle callback replacement until typed
  rollback releases the generation mutex.

## Validation outcome

- Incremental GCC Debug: 40/40 CTest.
- Fresh GCC Debug: 66 targets built; 40/40 CTest.
- Focused direct checks: runtime 38/0, support 61/0, authority 71/0, schema 58/0,
  domain 588/0, lifecycle 49/0.
- Stress: authority 100/100, schema 50/50, support 50/50.
- GCC Release focused boundary build/tests: pass.
- GCC ASan/UBSan focused boundary build/tests with leak detection and
  halt-on-error: pass.
- Clang 17 focused boundary build/tests: pass.
- Complete Release and complete sanitizer builds: incomplete because unchanged
  `sync_domain.cpp` exceeded the cloudtainer per-command ceiling. This remains
  optional and is recorded verbatim.
- `clang-format`: unavailable.

## What remains missing

- A typed savepoint/nested-scope owner. Deny-all is safe but intentionally
  restrictive.
- Structural thread affinity, preferably a per-connection actor/strand. The
  current guard documents but does not dynamically enforce same-thread
  destruction.
- Connection quarantine after alien callback replacement. Current operations
  fail closed and require explicit cleanup/close, but the raw handle can still
  be used by alien code.
- A fault-injecting VFS and executable crash oracle for power-loss semantics.
- Migration of the 95 legacy transaction boundaries into typed, invariant-owned
  repositories.
- Decomposition of `sync_domain.cpp`; its size is now a measured validation and
  review bottleneck, not merely a style concern.

## Speculative next design

A high-leverage next step is a connection actor that owns the SQLite handle,
authorizer generation, typed transaction, schema lease, and repository
capabilities on one execution strand. Transaction authority would become an
affine message-local capability rather than a thread-affinity convention.
After that, add typed savepoints whose proof includes parent transaction
generation and savepoint depth/name digest, then drive both through a VFS fault
matrix and executable transition oracle.
