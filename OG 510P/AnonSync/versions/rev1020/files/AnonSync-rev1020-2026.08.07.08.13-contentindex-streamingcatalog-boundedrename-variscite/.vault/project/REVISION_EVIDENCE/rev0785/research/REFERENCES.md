# rev0785 research references and implications

Research was performed against first-party SQLite documentation on 2026-07-14.

## SQLite close semantics

Source: https://sqlite.org/c3ref/close.html

SQLite documents that `sqlite3_close()` returns `SQLITE_BUSY` and leaves a
connection open when prepared statements, BLOB handles, or backup objects remain.
By contrast, `sqlite3_close_v2()` returns success, marks the connection a zombie,
and defers deallocation; SQLite describes that API as intended for garbage-collected
hosts with arbitrary destructor order. SQLite also automatically rolls back an
open transaction during close.

Implication: deferred zombie close and implicit rollback hide C++ lifetime-order
or transaction-boundary defects. AnonSync's managed owner uses strict close and
fails stopped on an open transaction or a busy close.

## Serialized connection mode

Source: https://www.sqlite.org/c3ref/open.html

SQLite documents `SQLITE_OPEN_FULLMUTEX` as serialized mode in which multiple
threads may safely attempt to use one connection, with SQLite mutexes serializing
actual work.

Implication: the C++ borrow counter may be thread-safe independently, but a
future typed borrowed connection should encode whether the underlying open used
FULLMUTEX before advertising cross-thread SQLite use.

## Fork boundary

Sources:

- https://www.sqlite.org/howtocorrupt.html#carrying_an_open_database_connection_across_a_fork
- https://sqlite.org/faq.html

SQLite explicitly warns not to carry an open connection across `fork()`, says a
child must open its own connection, and warns not even to call `sqlite3_close()`
on the inherited parent connection because cleanup can damage parent-visible
state.

Implication: child-side quarantine that locks or repairs copied C++ state is the
wrong model. Inherited capabilities must fail stopped before SQLite, allocator,
mutex, or cleanup work; the child should exec, `_Exit`, or construct entirely
new child-local state along a controlled path.

## Inference

These sources do not prescribe AnonSync's capability API. The owner-generation,
strict-close, read-only statement view, and source-audit design are project
inferences: they turn SQLite's runtime preconditions into explicit C++ ownership
and release gates that can be tested and reviewed.
