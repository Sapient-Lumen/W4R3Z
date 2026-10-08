# Rev0774 primary-source research — SQLite transaction authority

Accessed 2026-07-14. Only SQLite's official documentation is used for the
technical contract summarized here.

## Sources

1. SQLite compile-time authorization callbacks  
   https://sqlite.org/c3ref/set_authorizer.html
2. SQLite authorizer action codes  
   https://sqlite.org/c3ref/c_alter_table.html
3. SQLite transaction language  
   https://sqlite.org/lang_transaction.html
4. SQLite savepoints  
   https://sqlite.org/lang_savepoint.html
5. SQLite autocommit state  
   https://sqlite.org/c3ref/get_autocommit.html
6. SQLite per-schema transaction state  
   https://sqlite.org/c3ref/txn_state.html
7. SQLite database-connection mutex  
   https://sqlite.org/c3ref/db_mutex.html

## Findings mapped to implementation

### Authorization is compile-time and replaceable

SQLite invokes the authorizer while statements are compiled. Only one
callback exists per connection, and a later installation replaces it. A
statement prepared with the v2/v3 interfaces may be reprepared during step, so
the correct callback must remain installed through execution.

**Design consequence:** rev0774 owns callback installation, challenges the
exact callback generation before use, retains same-handle serialization through
finalization, and tests a transaction statement prepared before installation.
The authorizer is not treated as a step-time sandbox.

### Transaction and savepoint actions are distinct codes

`SQLITE_TRANSACTION` reports an operation in argument 1. `SQLITE_SAVEPOINT`
reports operation and savepoint name. Protecting only transaction action 22
would miss action 32.

**Design consequence:** typed BEGIN/COMMIT/ROLLBACK consume operation-specific
permits; all savepoint operations are denied until a typed parent/depth model
exists.

### END and savepoints create aliases around the stack

SQLite documents END as an alias for COMMIT. An outermost SAVEPOINT outside
BEGIN behaves like BEGIN DEFERRED; releasing the outermost savepoint commits;
ROLLBACK TO rewinds but keeps the transaction active.

**Design consequence:** tests include END, outermost SAVEPOINT, nested
SAVEPOINT, RELEASE, and ROLLBACK TO. The policy is based on action semantics,
not keyword matching.

### COMMIT failure can preserve a live transaction

A COMMIT can return SQLITE_BUSY while the transaction remains active and may be
retried. Selected errors can also trigger automatic rollback; SQLite directs
applications to inspect autocommit/transaction state.

**Design consequence:** explicit commit failure does not automatically revoke
the generation. Authority remains only if exact proof, callback challenge, and
explicit transaction state still agree. Automatic rollback clears the
generation at the next check.

### Autocommit is unsafe under concurrent mutation

SQLite states that `sqlite3_get_autocommit()` has undefined results if another
thread changes autocommit concurrently.

**Design consequence:** the FULLMUTEX connection mutex is retained across the
complete typed generation. This is not merely a performance lock; it is part of
the correctness proof for state observation.

### Database mutex availability reflects threading mode

`sqlite3_db_mutex()` returns the mutex that serializes the connection in
Serialized mode and returns null in Single-thread or Multi-thread modes.

**Design consequence:** owned authority rejects handles without a connection
mutex. Production opens use FULLMUTEX, and an adversarial NOMUTEX test verifies
fail-closed behavior.

## Inferences and speculation

These are design inferences, not claims made by SQLite:

- The most reliable local capability is an affine transaction object that owns
  both the generation proof and execution strand. A copyable bool or raw handle
  cannot encode the necessary lifetime.
- Typed savepoint authority should include parent transaction generation,
  monotonic savepoint generation, stack depth, and a canonical name digest.
  RELEASE should consume the exact top-of-stack capability; ROLLBACK TO should
  preserve that capability but revoke descendants.
- Alien callback replacement should eventually quarantine the connection in an
  actor-owned state so no new domain operation can use it before close/reopen.
- A VFS fault harness should make every durable operation an explicit crash
  point and compare reopened state with a small state-machine oracle. The
  transaction-generation fence then becomes one part of a larger durable
  evidence proof, not the final durability result.
