# Rev0853 deep audit

## Finding

The busy-handler lifetime owner was not the sole authority over its SQLite
slot. Eight production `sqlite3_busy_timeout()` calls used an API that SQLite
documents as replacing the current busy handler. A live C++ owner, exact
connection-generation borrow, atomic report, and client-data claim could all
remain present while the actual callback had been silently superseded.

The previous source audit confined direct `sqlite3_busy_handler()` calls but did
not globally confine `sqlite3_busy_timeout()` and did not scan for
`PRAGMA busy_timeout`. This was a policy- and lifetime-integrity gap, not merely
a style inconsistency.

## Correction reviewed

The final source has these exact production inventories:

- `sqlite3_busy_handler(`: **2** calls, both in
  `sqlite_busy_handler_owner.cpp` for installation and revocation;
- `sqlite3_busy_timeout(`: **1** call, in the reviewed gateway;
- `sqlite_set_busy_timeout_or_throw(`: all eight production configurations plus
  declarations and implementation composition;
- `PRAGMA busy_timeout`: **0** production literals; and
- busy-owner client-data name: one shared definition consumed by the owner and
  alternate-setter gateway.

For serialized handles, `SqliteDatabaseMutexScope` enters the connection mutex,
probes the shared live-owner client-data slot, rejects a conflict, and only then
calls the alternate setter before leaving the same recursive mutex. The typed
overload first mints an exact serialized-generation borrow. The raw overload
retains a documented single-user lane for SQLite `NOMUTEX` connections.

## Runtime proofs

The focused busy-owner corpus now has **38 checks**. New proofs cover:

- deterministic rejection while an owner is live;
- preservation and invocation of the bounded callback after rejection;
- post-detach timeout configuration;
- no accidental client-data claim creation by ordinary timeout configuration;
- 64 concurrent owner/setter orderings per process run; and
- release of every exact-generation borrow.

The support corpus has **77 checks**, including exact configured interval,
exception validation, typed borrow release, and a real `NOMUTEX` connection.
The repeatability lane ran the two executables 100 times each and exercised
6,400 concurrent race iterations without failure.

## Audit composition

The existing audits were extended rather than multiplied:

- busy-handler owner: **36/36**;
- SQLite mutex capability: **70/70**;
- authorizer owner composition: **41/41**;
- verification budget composition: **61/61**;
- SQLite owner generation: **27/27**;
- SQLite process authority: **89/89**; and
- transaction-stack authority: **100/100**.

The first complete audit run failed because the owner-generation audit encoded
five typed support helper mints. The new busy-timeout helper made six. The audit
was upgraded to require the new overload and exact mint count, then the full
registry was rerun successfully. This is retained as evidence that the audit
suite can detect integration drift, while also demonstrating why hand-maintained
numeric source counts should eventually become generated inventories.

## Residual risk

Source confinement is not runtime interposition. Code outside the audited tree
that holds a raw `sqlite3*` can still replace the handler directly or through
dynamically composed SQL. There is no continuous callback-address attestation.
ThreadSanitizer was not available in this lane, so the concurrent corpus is a
behavioral ordering proof, not a data-race detector. The bundled SQLite C
translation unit was intentionally outside ASan+UBSan instrumentation.

No claim is made for arbitrary concurrent close/use, a full callback-slot
orchestrator, distributed convergence, hostile-worker isolation, or privacy/key
semantics.
