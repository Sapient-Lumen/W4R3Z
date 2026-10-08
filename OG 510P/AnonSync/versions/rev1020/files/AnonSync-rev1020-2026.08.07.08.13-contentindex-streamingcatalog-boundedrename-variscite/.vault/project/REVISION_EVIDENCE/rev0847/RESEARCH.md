# Rev0847 research record

Accessed 2026-07-19. Only primary SQLite documentation and the public C++ draft
were used for the correction's external premise.

## SQLite progress callback

SQLite documents `sqlite3_progress_handler(D,N,X,P)` as registering one callback
`X` and an opaque pointer `P` for a database connection. The callback is invoked
periodically during `sqlite3_step()`, `sqlite3_prepare()`, and related work; the
opaque pointer is passed back as the callback's sole argument. Only one handler
is active per connection, and disabling or replacing it changes that
connection-level registration.

Source: https://sqlite.org/c3ref/progress_handler.html

Implication for AnonSync: passing `this` as `P` creates a raw callback-context
lifetime boundary. SQLite does not own or extend the lifetime of the C++ object,
and the interface carries no C++ thread-affinity proof.

## SQLite serialized connections

SQLite documents serialized mode as permitting API calls affecting one
connection or derived object from multiple threads, with SQLite mutexes making
the effect equivalent to some single-thread order. `SQLITE_OPEN_FULLMUTEX`
selects that serialized connection mode when the global configuration permits
it.

Sources:

- https://sqlite.org/threadsafe.html
- https://sqlite.org/c3ref/open.html

Implication for AnonSync: SQLite's connection mutex can serialize entry into
SQLite. It does not, by itself, transfer ownership of an application-owned
callback context, synchronize every application field outside SQLite, or
establish a C++ lifetime protocol for destruction and handler detachment. This
is an inference from the documented division between SQLite's connection
serialization and the application's opaque `void*` callback context.

## C++ memory model

The public C++ draft defines a data race as potentially concurrent conflicting
actions, at least one non-atomic, with no happens-before relationship; a data
race is undefined behavior. Mutex and atomic operations have specifically
defined synchronization roles.

Source: https://eel.is/c++draft/intro.races

Implication for AnonSync: a comparison against a thread-incarnation token is an
authority check, not synchronization. If callers race an ordinary counter or
end the owner's lifetime before the guard can execute, the token cannot repair
the program. Shared use requires explicit synchronization and a lifetime
architecture, not merely a stronger identity check.

## Resulting design rule

Any C API that stores an application `void*` and later calls back into C++ must
be classified along four axes:

1. who owns the pointed-to object's lifetime;
2. which process and exact thread incarnation may enter it;
3. how replacement, detach, move, and destruction are serialized; and
4. whether callback-visible fields are atomic, externally synchronized, or
   strictly thread-affine.

Rev0847 makes this rule executable for `SqliteVerificationBudget`; it does not
yet prove that every callback context in the cube has been classified.
