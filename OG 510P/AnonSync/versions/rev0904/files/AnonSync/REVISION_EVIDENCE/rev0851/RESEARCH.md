# Rev0851 primary-source research

## SQLite client data lifetime

SQLite's client-data API states that the supplied destructor may run when
allocation fails during `sqlite3_set_clientdata`, when the same name is
replaced, or when the connection closes. Close-time destructor order is not
specified, and the destructor is called exactly once for accepted storage.

Source: SQLite `sqlite3_get_clientdata` / `sqlite3_set_clientdata` documentation:
https://sqlite.org/c3ref/get_clientdata.html

Design consequence: publish connection state policy-empty until every fallible
SQLite ownership step is complete; never depend on close-time client-data
ordering to revoke a separately retained callback.

## SQLite authorizer retention and reprepare

SQLite permits one authorizer per connection. A subsequent setter overrides the
prior callback. The third argument is retained as callback context. Authorizer
calls occur while statements are compiled and may occur again during
`sqlite3_step()` when schema changes trigger reprepare.

Source: SQLite `sqlite3_set_authorizer` documentation:
https://sqlite.org/c3ref/set_authorizer.html

Design consequence: the policy context needs connection-lifetime ownership, not
install-call stack lifetime.

## Serialized connection mutex

For a serialized database connection, `sqlite3_db_mutex()` returns the mutex
protecting that connection. SQLite's mutex API defines `sqlite3_mutex_try()` as
returning `SQLITE_BUSY` when another thread owns the mutex and `SQLITE_OK` when
acquisition succeeds.

Sources:
https://sqlite.org/c3ref/db_mutex.html
https://sqlite.org/c3ref/mutex_alloc.html

Design consequence: a custom context deleter running on another thread can use
`sqlite3_mutex_try()` as an executable witness that policy retirement occurs
after the connection guard has left the mutex.

## C++ destruction order

C++ automatic objects in one block are destroyed in reverse order of completed
construction. Return sequencing destroys local variables before function
parameters, and automatic-storage lifetime follows the enclosing block.

Sources: current C++ working draft sections:
https://eel.is/c++draft/stmt.dcl
https://eel.is/c++draft/stmt.return
https://eel.is/c++draft/basic.stc.auto

Design consequence: declare retired policy before the mutex guard. Reverse local
destruction then leaves SQLite's mutex before releasing user-owned context; a
by-value incoming policy parameter also outlives the local guard on failure.

## Speculation and next architecture

The same pattern should become a connection-level callback registry: each
retained callback slot would bind callback identity, typed context ownership,
process incarnation, exact connection generation, replacement policy, and
teardown order. That would reduce distributed close logic and make callback
composition testable as one state machine. A future typed factory should avoid
`shared_ptr<void>` casts while preserving the non-templated C bridge.
