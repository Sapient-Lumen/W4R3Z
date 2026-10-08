# Rev0854 primary-source research

Checked against current SQLite documentation on 2026-07-20 UTC.

## Serialized mode is per-connection API serialization

SQLite distinguishes single-thread, multi-thread, and serialized modes. In
serialized mode, mutexes allow a database connection and derived objects to be
used safely from multiple threads; `SQLITE_OPEN_FULLMUTEX` selects the serialized
connection mode when the build supports mutexes.

Source: https://sqlite.org/threadsafe.html

Design consequence: serialized mode protects SQLite API execution, but it does
not automatically turn several separately serialized API calls into one
application-level state transition.

## `sqlite3_db_mutex()` exposes the exact serializer

SQLite documents that `sqlite3_db_mutex(D)` returns the mutex that serializes
access to database connection `D` in serialized mode and returns null in
single-thread or multi-thread mode.

Source: https://sqlite.org/c3ref/db_mutex.html

Design consequence: the exact connection mutex is the narrowest SQLite-owned
witness available for making a multi-call claim-plus-setter transition atomic
against other reviewed users of the same connection.

## SQLite mutex entry is recursive

SQLite permits applications to use the mutex interfaces. The database-connection
mutex is recursive, so a thread may enter it and then call ordinary SQLite APIs
that re-enter the same mutex. Entry and leave must occur on the same thread.

Source: https://sqlite.org/c3ref/mutex_alloc.html

Design consequence: an RAII owner can hold `sqlite3_db_mutex()` across
`sqlite3_get_clientdata`, `sqlite3_set_clientdata`, and a callback setter without
deadlocking ordinary serialized SQLite calls. The C++ owner must prevent thread
transfer before leave.

## Same-name client-data publication is destructive replacement

SQLite documents that a later `sqlite3_set_clientdata(D,N,...)` call with the
same database and name invokes the prior destructor. Closing the connection also
invokes attached client-data destructors, with no guaranteed order among names.

Source: https://sqlite.org/c3ref/get_clientdata.html

Design consequence: “check empty” and “publish claim” cannot be independent
operations. Replacement is not a benign overwrite; it is an immediate lifetime
transition that may destroy callback-visible state.

## Speculation

The next durable abstraction should be a connection-generation callback-slot
orchestrator that owns all retained SQLite hooks for one exact connection. API-
specific owners should remain typed because busy, progress, authorizer, trace,
commit, rollback, and update hooks have different callback and replacement
contracts. A compact orchestrator can nevertheless own dependency order,
mutation permits, revoke-all-before-close, and generated lifecycle histories.

A second useful step is a debug/race-detection build against system SQLite with
ThreadSanitizer. The current lock witness makes intended synchronization
explicit, but repeatability alone cannot prove absence of C++ data races.
