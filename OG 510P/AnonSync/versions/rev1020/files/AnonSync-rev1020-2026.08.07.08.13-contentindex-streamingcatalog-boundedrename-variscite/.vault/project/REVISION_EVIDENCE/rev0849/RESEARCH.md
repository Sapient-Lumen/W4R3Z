# AnonSync rev0849 research notes

Research was limited to primary SQLite documentation for the semantics used by
this revision. Rechecked against the live upstream documentation on 2026-07-19.

## SQLite connection client data

`sqlite3_set_clientdata()` associates a named pointer with one connection. When
both the pointer and destructor are non-null, SQLite invokes the destructor
exactly once on registration allocation failure, same-name replacement, or
connection close. Destructor order during close is unspecified. This supports a
connection-owned lifetime sentinel, but not an assumption about ordering among
multiple client-data owners.

Source: https://sqlite.org/c3ref/get_clientdata.html

## Progress-handler singleton semantics

Only one progress handler exists per connection. Registering another cancels the
old handler; setting a null callback or interval below one disables it. SQLite
exposes no getter for the current handler. Therefore exact connection ownership
and source inventory can prevent reviewed replacement, but the runtime cannot
query SQLite to prove that arbitrary foreign code did not replace the handler.

Source: https://sqlite.org/c3ref/progress_handler.html

## `sqlite3_close_v2()` zombie lifetime

With outstanding statements, BLOB handles, or backup objects,
`sqlite3_close_v2()` returns success but marks the connection as an unusable
zombie and defers deallocation until dependents are destroyed. A client-data
destructor therefore cannot reject that call synchronously; it runs only at
actual destruction. Exact-generation typed ownership is the immediate defense
for reviewed code, while the claim converts deferred raw misuse into a fail-stop
at final destruction.

Source: https://sqlite.org/c3ref/close.html

## Design inference

The combination implies that retained callback lifetime should be modeled as a
connection-generation lease, not a raw setter call. Client data can witness
actual destruction and named replacement; typed generation borrows can prevent
reviewed close/reopen transitions; a connection callback registry can arbitrate
singleton callback slots that SQLite itself does not expose for inspection.
