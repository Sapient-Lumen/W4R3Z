# AnonSync rev0774 — transaction-stack authority and refactor audit

## Audit question

Can any ambient SQL path replace, commit, roll back, or nest the SQLite
transaction that currently authorizes durable peer-ingress evidence while a
typed guard still appears live?

Before rev0774, the answer was yes in principle. Rev0773 could detect an
observed end, but SQLite exposes state rather than an identity for the active
transaction. The audit therefore treated the transaction stack as an authority
surface, not merely an exception-safety utility.

## Findings corrected

### 1. Raw boundary replacement was not mechanically fenced

A source audit forbade raw transaction SQL in the focused lifecycle, but the
runtime connection still accepted it. An unobserved COMMIT+BEGIN sequence could
replace generation N with N+1 while retaining the same `sqlite3*` and a false
`autocommit == false` observation.

**Correction:** the owned authorizer denies all ambient
`SQLITE_TRANSACTION` actions. Typed code receives one operation-specific,
single-use permit only after exact proof validation.

### 2. Savepoints were a complete alternate transaction stack

Outermost SAVEPOINT begins a transaction; outermost RELEASE commits it;
ROLLBACK TO rewinds without ending the transaction. A literal-BEGIN fence would
have left a second control plane.

**Correction:** every `SQLITE_SAVEPOINT` action is denied. The existing payload
bootstrap savepoint helper is inventoried and has no production caller on an
owned connection. A future nested-scope API must own savepoint generation
explicitly.

### 3. Connection serialization ended too early

The typed BEGIN path acquired the connection mutex only around boundary setup.
Schema verification later acquired its own lease, leaving a small interleaving
window in which another thread could replace the authorizer on the same handle.

**Correction:** successful BEGIN transfers the recursive mutex entry to the
transaction proof. The owner retains it until exact commit, rollback, or
revocation. Copied capabilities explicitly clear the mutex pointer and cannot
release it.

### 4. Alien replacement made naïve destructor rollback unsafe

After an alien callback replaces the bridge, it can commit the original
transaction and begin another. SQLite does not expose a transaction generation
identifier. Issuing raw ROLLBACK from the stale destructor could destroy the
new transaction.

**Correction:** destructor cleanup attempts only exact fenced rollback. If
proof or callback ownership no longer matches, it revokes local authority and
leaves connection close or explicit alien cleanup to end SQL state.

### 5. Recovery could deadlock itself at typed BEGIN

A handle retained AnonSync client data after callback replacement. Typed BEGIN
correctly rejected the alien callback, but schema recovery tried to begin before
reinstalling the bridge.

**Correction:** prior authority state is detected and the restrictive schema
bridge is reinstalled before compiling the recovery snapshot.

### 6. Audit ownership had become stale after refactor

The older payload audit searched the generic support file for transaction
checks that had moved. Without adjustment, an audit could fail for the wrong
reason or eventually be weakened around obsolete locations.

**Correction:** both predecessor audits now include the transaction and
connection-authority owners. A new audit independently checks the split,
permit/generation shape, mutex ownership, recovery order, adversarial markers,
and legacy inventory.

## Exact runtime model

For an owned connection, a live proof consists of:

- process-local random salt;
- connection incarnation allocated at first client-data installation;
- authorizer generation advanced on deliberate reinstall;
- transaction generation advanced on typed BEGIN;
- exact `sqlite3*` identity;
- exact active generation in connection-owned state;
- the owned callback responding to a prepare-time nonce challenge;
- SQLite explicit-transaction state; and
- one retained recursive FULLMUTEX entry.

All elements must remain current. A pointer, bool, callback success, or SQLite
state alone is insufficient.

## Audit results

- Transaction-stack audit: 45/45 checks passed.
- Payload transaction-authority audit: 38/38 checks passed.
- SQLite authorizer ownership audit: passed.
- Fresh Debug CTest: 40/40.
- Focused GCC Release, GCC ASan/UBSan, and Clang 17 boundary suites: passed.
- Stress: 200 focused executions total, all passed.

The machine-readable reports are adjacent to this document.

## Legacy boundary inventory

The audit reports 95 raw transaction-control occurrences outside the new owner:

| File | Count | Interpretation |
|---|---:|---|
| `src/sync_domain.cpp` | 45 | Highest-risk migration and build-review bottleneck |
| `src/reporting_selftests.cpp` | 15 | Test/report scaffolding; should consume shared owner |
| `src/sqlite_replay_ledger.cpp` | 15 | Durable replay authority deserves its own typed repository |
| `src/sync_peer_ingestion.cpp` | 6 | Separate ingress path, not covered by peer transport owner |
| `src/sync_peer_ingress_payload_store.cpp` | 6 | Isolated bootstrap savepoint helper and fixtures; inventoried |
| `src/sync_peer_ingress_lifecycle.cpp` | 5 | Selftest lock-holder fixtures; production slice is raw-free |
| `src/runner.cpp` | 3 | Operational orchestration boundary |

These counts are not all defects of equal severity. They are intentionally not
silenced by an allowlist because the inventory is the migration roadmap.

## Remaining risks

1. **Thread affinity is contractual.** Retaining SQLite's recursive mutex means
   the guard must finalize and destruct on its constructing thread. The class is
   non-movable, but a pointer can still be transferred. A connection actor is
   the structural fix.
2. **Policy callbacks are trusted code.** SQLite forbids an authorizer callback
   from modifying its own connection. The bridge blocks C++ exceptions and
   malformed results, but cannot make a policy that violates SQLite's callback
   contract safe.
3. **Client-data namespace is same-process state.** Arbitrary cohost code can
   deliberately replace the authorizer or private client-data slot. AnonSync
   detects callback replacement at use time, but same-process memory-adversary
   resistance is outside this design.
4. **Unowned utility connections remain observation-based.** To avoid
   overwriting a caller's unknown authorizer, the generic typed guard preserves
   legacy state observation on unowned handles. Durable peer-ingress handles
   are owned and fenced; unowned mode must not be treated as equivalent proof.
5. **Process crash is not power loss.** No claim is made about dishonest flushes,
   torn sectors, directory durability, or network filesystems.
6. **Complete optimized/sanitizer builds are resource-limited.** The revised
   boundary passes those focused profiles, while the unchanged domain monolith
   exceeded the cloudtainer command ceiling.

## Refactor direction

The next extraction should be `sqlite_replay_ledger` transaction ownership,
followed by slices of `sync_domain.cpp` chosen by one durable state machine at a
time. Each extracted repository should own:

- connection actor/strand;
- authorizer and transaction generations;
- typed transaction or typed savepoint;
- reviewed schema/snapshot capability;
- durable evidence codecs; and
- commit ambiguity plus crash-point reporting.

Mechanical file splitting without moving invariant ownership would only spread
the same ambient authority across more files.
