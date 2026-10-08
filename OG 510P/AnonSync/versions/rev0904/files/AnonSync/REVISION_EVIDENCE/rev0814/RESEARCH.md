# Rev0814 research notes

Only primary SQLite documentation and the bundled SQLite source were used for
the transaction-stack design.

## Savepoint semantics

SQLite documents that savepoints may be nested; `ROLLBACK TO` rewinds changes
but leaves the named savepoint on the stack; `RELEASE` removes the matching mark
and newer marks; an outermost `RELEASE` can commit; plain `COMMIT` empties the
entire transaction stack; and transaction-stack closure is last-in-first-out.

Source: https://sqlite.org/lang_savepoint.html

Design consequence: rollback ownership must issue `ROLLBACK TO` followed by
`RELEASE`, generated names must be unique, inner closure must be LIFO, and the
typed outer transaction must refuse commit while any owned inner mark remains.

## Authorizer evidence

SQLite exposes `SQLITE_SAVEPOINT` with the operation string and savepoint name.
The authorizer is invoked while statements are compiled, only one authorizer may
be installed per connection, and a later `sqlite3_set_authorizer()` replaces the
previous callback.

Sources:

- https://sqlite.org/c3ref/c_alter_table.html
- https://sqlite.org/c3ref/set_authorizer.html

Design consequence: AnonSync arms one exact single-use operation/name permit,
verifies that its bridge observed the statement, treats callback replacement as
loss of authority, and never interprets `SQLITE_IGNORE` as permission for a
transaction-stack operation.

## Observation versus identity

`sqlite3_get_autocommit()` reports whether an explicit transaction is active and
is the documented way to discover automatic rollback after selected errors. It
does not identify a transaction or savepoint generation. `sqlite3_txn_state()`
reports NONE/READ/WRITE state, not stack identity.

Sources:

- https://sqlite.org/c3ref/get_autocommit.html
- https://sqlite.org/c3ref/txn_state.html

Design consequence: autocommit and transaction state are observations, not
sufficient authority. Fenced operations bind process incarnation, connection
incarnation, authorizer generation, outer transaction generation, savepoint
generation, owner thread, and retained close-fence lifetime. The explicitly
unfenced compatibility constructor is documented as observation-based and is
accepted only when no AnonSync authority is installed.

## Bundled implementation check

The bundled SQLite 3.53.3 amalgamation was inspected to confirm that the
authorizer operation strings used by savepoint statements are `BEGIN`,
`RELEASE`, and `ROLLBACK`. Runtime adversarial tests then verify the exact bridge
behavior; source inspection is not used as a substitute for execution.
