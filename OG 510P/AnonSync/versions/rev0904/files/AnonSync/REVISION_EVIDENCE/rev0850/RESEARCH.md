# AnonSync rev0850 research notes

Research was rechecked against live primary SQLite documentation on 2026-07-19.

## Compile-time authorizer semantics

A connection has only one authorizer. Every `sqlite3_set_authorizer()` call
overrides the previous callback, and a null callback disables it. The callback
receives the setter's third argument as its first argument. SQLite can invoke
the authorizer during statement preparation and again during `sqlite3_step()`
when schema change causes automatic reprepare. Therefore the callback context
must remain valid for the complete prepare/reprepare frontier, not merely for
the setter call.

Source: https://sqlite.org/c3ref/set_authorizer.html

## Connection client-data destruction

`sqlite3_set_clientdata()` invokes a non-null destructor on registration OOM,
same-name replacement, or connection close. SQLite promises exactly-once
destruction but explicitly makes no guarantee about destructor ordering during
close. Client data can therefore witness premature context destruction, but two
client-data slots cannot depend on SQLite choosing a favorable close order.
Explicit callback revocation must precede either slot's destruction.

Source: https://sqlite.org/c3ref/get_clientdata.html

## Strict close and zombie close

`sqlite3_close()` returns `SQLITE_BUSY` and leaves the connection open when
statements, BLOBs, or backup objects remain. `sqlite3_close_v2()` instead returns
success, marks the connection as an unusable zombie, and defers destruction
until dependents are released. A strict typed close is therefore a useful
lifetime-order assertion. A client-data sentinel cannot synchronously reject a
raw zombie transition because its destructor runs only at eventual destruction.

Source: https://sqlite.org/c3ref/close.html

## Design inference

The safe unit is not an authorizer setter; it is an exact-generation callback
slot with four coupled resources: connection, callback function, context
address, and destruction witness. Installation must freeze and publish those in
one direction, while teardown consumes them in reverse dependency order. Since
SQLite has no authorizer getter, executable challenge/response and confined
setter inventory are necessary complements to lifetime ownership.
