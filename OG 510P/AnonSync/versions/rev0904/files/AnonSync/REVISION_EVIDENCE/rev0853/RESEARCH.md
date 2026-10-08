# Rev0853 primary-source research

Checked on 2026-07-20 UTC.

## `sqlite3_busy_timeout` replaces the busy handler

SQLite documents that `sqlite3_busy_timeout()` installs a busy handler and that
calling it clears any previously installed busy handler. A nonpositive timeout
disables the handler.

Source: https://sqlite.org/c3ref/busy_timeout.html

Design consequence: it is not a harmless numeric option. It is an alternate
setter for the same singleton callback slot owned by
`SqliteBusyHandlerOwner`.

## `PRAGMA busy_timeout` is another replacement surface

SQLite documents `PRAGMA busy_timeout` as an alternative to the C interface and
notes that each database connection can have only one busy handler; the pragma
may therefore overwrite a previously set handler.

Source: https://sqlite.org/pragma.html#pragma_busy_timeout

Design consequence: source confinement must inventory SQL spellings as well as
C function calls. Literal scanning cannot prove the absence of dynamically
constructed SQL, so the release records that limitation.

## Connection mutex semantics

`sqlite3_db_mutex()` returns the mutex for a database connection when SQLite is
operating in serialized mode and returns null for single-thread or multi-thread
connections. SQLite's mutex interface permits null as a no-op, and recursive
mutexes may be re-entered by the owning thread.

Sources:

- https://sqlite.org/c3ref/db_mutex.html
- https://sqlite.org/c3ref/mutex_alloc.html
- https://sqlite.org/threadsafe.html

Design consequence: on a serialized connection, holding the database mutex
across the client-data ownership probe and `sqlite3_busy_timeout()` makes that
pair atomic with respect to other SQLite calls using the same connection. The
raw `NOMUTEX` lane remains valid only under SQLite's ordinary single-user
contract; AnonSync's retained owner requires serialized-generation evidence and
cannot be attached there.

## Speculation

The next durable abstraction is likely a connection-generation callback-slot
orchestrator, not a universal type-erased callback class. Each SQLite callback
API has different replacement, reentrancy, and teardown rules, while the
connection-level object can own slot names, dependency order, mutation permits,
and revoke-all-before-close state. A generated lifecycle model can then test
all setter aliases and teardown permutations without expanding lexical audits
indefinitely.
