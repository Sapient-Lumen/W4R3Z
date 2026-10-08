# Rev0815 research notes

Primary SQLite documentation and the bundled SQLite 3.53.3 source were used.
Online sources were rechecked on 2026-07-17.

## Savepoint partial-state semantics

SQLite documents `ROLLBACK TO` as rewinding changes after the corresponding
mark while leaving that mark on the stack. `RELEASE` removes the matching mark
and newer marks. Transaction-stack closure is LIFO; plain `COMMIT` empties the
stack.

Source: https://sqlite.org/lang_savepoint.html

Design consequence: successful rewind followed by failed release is a valid,
retryable partial state. The C++ owner must keep exact mark authority, prevent
outer commit, and make retry roll back any work added after the first rewind.
The owner should not add unrelated throwing allocations between those two
SQLite effects.

## Authorizer boundary

SQLite invokes the authorizer while compiling statements. Only one authorizer
may be installed on a connection, later installation replaces the earlier one,
the callback must not modify the invoking connection, and applications must keep
the intended callback installed across possible automatic reprepare.

Source: https://sqlite.org/c3ref/set_authorizer.html

Design consequence: AnonSync probes callback ownership, arms one exact
operation/name permit for one synchronous statement, verifies observation, and
treats replacement as loss of authority rather than silently issuing raw
fallback SQL.

## Automatic outer rollback observation

SQLite documents that selected errors including `SQLITE_FULL`, `SQLITE_IOERR`,
`SQLITE_NOMEM`, `SQLITE_BUSY`, and `SQLITE_INTERRUPT` may automatically roll
back a multi-statement transaction. `sqlite3_get_autocommit()` is the documented
way to discover whether that happened.

Source: https://sqlite.org/c3ref/get_autocommit.html

Design consequence: retry authority must be revalidated after failure. Autocommit
is necessary recovery evidence but does not identify a transaction or savepoint
generation, so it cannot replace the typed process/connection/callback/owner
proof.

## Allocation failure testing

SQLite describes robust allocation-failure handling and an allocator overlay
that fails the Nth allocation, then advances the failure point until the test
completes. It also documents application-defined allocators and allocator
overlays installed through SQLite startup configuration.

Source: https://sqlite.org/malloc.html

Design consequence: the next exception-composition expansion should be a
one-shot worker that installs an Nth-allocation overlay before SQLite
initialization. Global allocator configuration should not be introduced into the
long-lived test process after other SQLite users have initialized the library.

## Crash and VFS testing

SQLite's test documentation describes separate-process crash tests using an
alternative VFS that simulates crashes and reorders or corrupts unsynchronized
writes. SQLite exposes the VFS abstraction as its operating-system boundary.

Sources:

- https://sqlite.org/testing.html
- https://sqlite.org/vfs.html

Design consequence: AnonSync needs a domain oracle above SQLite. A database can
be structurally recoverable while disagreeing with receipts, manifests,
sidecars, staging files, renames, or directory-sync state. Those artifacts must
be tested as one publication/recovery protocol.

## Bundled version check

SQLite 3.53.3 was released on 2026-06-26 and includes a fix for the WAL-reset
database-corruption bug listed in its release notes. AnonSync already bundles
3.53.3, so rev0815 makes no third-party source replacement.

Source: https://sqlite.org/releaselog/3_53_3.html
