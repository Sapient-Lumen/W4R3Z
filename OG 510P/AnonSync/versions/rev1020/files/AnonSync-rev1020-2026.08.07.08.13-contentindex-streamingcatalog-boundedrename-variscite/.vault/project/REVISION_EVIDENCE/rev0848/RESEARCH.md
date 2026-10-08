# Rev0848 research record

Accessed 2026-07-19. Sources are primary SQLite documentation.

## SQLite connection client data

Source: https://sqlite.org/c3ref/get_clientdata.html

`sqlite3_set_clientdata()` associates a named pointer with a connection. The
destructor runs exactly once on registration OOM, replacement of the same name,
or connection close; destructor order during close is unspecified. The API was
introduced in SQLite 3.44.0 and is intended for wrapper-library connection
state. This directly motivates the version floor, narrow namespace, exact
client-data claim, and explicit close-order protocol.

## Busy-handler contract

Source: https://sqlite.org/c3ref/busy_handler.html

A connection has only one busy handler. Installing another handler,
`sqlite3_busy_timeout()`, or `PRAGMA busy_timeout` replaces the previous one.
The callback is not reentrant, must not close the invoking connection or
statement, and may be skipped by SQLite when invoking it would contribute to a
deadlock. This means diagnostics must tolerate `SQLITE_BUSY` without a callback,
and ownership cannot infer that the callback remains installed merely from the
client-data claim.

## Serialized connections

Source: https://sqlite.org/threadsafe.html

`SQLITE_OPEN_FULLMUTEX` selects serialized mode for an individual connection,
so API calls affecting that connection are serialized as if ordered on one
thread. This is a library synchronization guarantee, not a transfer of C++
object lifetime or permission to race destruction. Rev0848 therefore permits
sequential cross-thread callback entry while requiring lock-free callback state
and quiescent detach.

## Fork inheritance

Source: https://www.sqlite.org/howtocorrupt.html#fork

SQLite warns not to use an inherited database connection after `fork()` and not
even to call `sqlite3_close()` on the parent-opened connection in the child.
This supports process-incarnation fail-stop checks on callback entry, owner
observation, detach, destruction, and client-data cleanup.

## Close semantics

Source: https://sqlite.org/c3ref/close.html

Strict `sqlite3_close()` fails with `SQLITE_BUSY` while unfinalized statements or
unfinished backups remain. `sqlite3_close_v2()` can zombify a connection and
defer deallocation. AnonSync's typed owners use strict close and exact-generation
borrows. Raw close remains a misuse surface and is exercised in isolated death
probes; a future callback registry should also inventory and prohibit raw
`close_v2` on owned connections.

## Inference and speculation

SQLite client data is an effective lifetime sentinel, but it is not a complete
callback registry. Because SQLite exposes no getter for the current busy
handler, the strongest future design is one typed connection policy object that
owns authorizer, progress, busy, update, commit, rollback, trace, and client-data
registrations together. Raw setter functions should be unreachable outside that
module. This would replace several lexical audits with one runtime-owned
connection state machine.

The focused lifecycle driver also demonstrates a broader build lesson: tests
whose corpus already lives in a runtime library should not require linking
unrelated monolithic selftest translation units. Similar extraction can reduce
compiler and sanitizer cost while preserving one separate CLI-dispatch test.
