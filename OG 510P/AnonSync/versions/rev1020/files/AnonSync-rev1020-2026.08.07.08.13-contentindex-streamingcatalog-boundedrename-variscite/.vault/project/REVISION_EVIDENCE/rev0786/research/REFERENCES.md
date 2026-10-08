# rev0786 first-party research references and implications

Research was performed against first-party SQLite documentation on 2026-07-14.

## Per-connection mutex evidence

Source: https://sqlite.org/capi3ref.html (entry `sqlite3_db_mutex`)

SQLite documents that `sqlite3_db_mutex()` returns the mutex associated with a
database connection and returns null when the connection is operating without
a mutex. The returned object is owned by SQLite and must not be freed.

Implication: a connection owner can observe the mode actually materialized by
SQLite rather than trusting distant open-site intent. The pointer is retained
only as process-local generation evidence; AnonSync neither enters nor frees it.

## Threading modes and open-time selection

Sources:

- https://sqlite.org/threadsafe.html
- https://sqlite.org/c3ref/open.html

SQLite distinguishes single-thread, multi-thread, and serialized modes.
`SQLITE_OPEN_NOMUTEX` selects multi-thread behavior for a connection, while
`SQLITE_OPEN_FULLMUTEX` selects serialized behavior, subject to the library's
compile/start-time configuration. Serialized mode permits multiple threads to
use one connection with SQLite serializing access; multi-thread mode requires
that one connection not be used concurrently.

Implication: a C++ atomic borrow counter is not evidence that SQLite operations
on the borrowed connection are safe across threads. The connection's observed
mode belongs in the exact owner generation and typed SQL surfaces must reject
unserialized generations before calling SQLite.

## Fork boundary

Sources:

- https://www.sqlite.org/howtocorrupt.html#carrying_an_open_database_connection_across_a_fork
- https://sqlite.org/faq.html

SQLite warns against carrying an open connection across `fork()`, including
calling close on the inherited connection; the child should open a new
connection of its own.

Implication: inherited capabilities fail stopped before SQLite or copied
bookkeeping. Mutex-mode evidence does not authorize a child process and must
never weaken the process-incarnation check.

## Isolation context

Source: https://sqlite.org/isolation.html

SQLite explains serialized writes and snapshot isolation behavior for separate
connections, including WAL mode. This is a database concurrency guarantee, not
a substitute for application-level evidence about which generation, claim, or
durable receipt authorizes a transition.

## Project inference

SQLite does not prescribe AnonSync's capability API. Capture-on-adoption,
non-forgeable serialized borrows, exact-generation statement/transaction pins,
and deterministic migration inventories are project inferences that translate
SQLite runtime preconditions into reviewable C++ authority boundaries.
