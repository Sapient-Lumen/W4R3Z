# rev0773 primary-source research and design implications

Research was limited to official SQLite documentation and the bundled SQLite 3.53.3 header/source contract.

## Sources consulted

- SQLite current release and version: https://sqlite.org/
- Transaction semantics: https://sqlite.org/lang_transaction.html
- `sqlite3_get_autocommit()`: https://sqlite.org/c3ref/get_autocommit.html
- `sqlite3_txn_state()` and state constants: https://sqlite.org/c3ref/txn_state.html and https://sqlite.org/c3ref/c_txn_none.html
- Database-object name resolution: https://sqlite.org/lang_naming.html
- PRAGMA `table_info` / `table_xinfo`: https://sqlite.org/pragma.html#pragma_table_xinfo
- CREATE INDEX schema rules: https://sqlite.org/lang_createindex.html
- Write-ahead logging and synchronous behavior: https://sqlite.org/wal.html
- Authorizer API and action codes: https://sqlite.org/c3ref/set_authorizer.html and bundled `sqlite3.h` (`SQLITE_TRANSACTION`, `SQLITE_SAVEPOINT`)

## Findings applied directly

1. `BEGIN` disables autocommit and COMMIT/ROLLBACK re-enable it. SQLite also documents that selected statement failures may automatically roll back a transaction, and `sqlite3_get_autocommit()` is the way to discover that boundary. This supports permanent lease revocation once autocommit is observed.
2. `sqlite3_txn_state(db, "main")` distinguishes no transaction, read transaction, and write transaction for the durable database. This permits separate “active,” “snapshot,” and “write” authority checks instead of a single ambient boolean.
3. Unqualified object references can resolve to TEMP before `main`. Durable-state code therefore needs explicit `main` qualification even when a same-name TEMP object seems unlikely in normal operation.
4. `table_info` omits hidden/generated columns while `table_xinfo` exposes them. Exact schema attestation should use `table_xinfo` and require hidden state zero for ordinary reviewed columns.
5. A schema-qualified index name constrains index creation to that database. The revision adds `main.` at execution time while continuing to compare SQLite's canonical stored SQL against the reviewed unqualified manifest.
6. In WAL mode with `synchronous=FULL`, writers sync the WAL at each commit. That is useful evidence for local process-crash tests, but it does not remove the need for power-cut/VFS testing or SQLite's documented local-filesystem constraints.

## Speculative next steps

### Transaction-control authorizer token

The bundled SQLite API exposes `SQLITE_TRANSACTION` for BEGIN/COMMIT/ROLLBACK and `SQLITE_SAVEPOINT` for savepoint operations. The existing connection-authority owner could deny those actions by default and allow them only while a typed transaction guard presents a short-lived internal token. This would turn the current static “no raw boundary” rule into runtime enforcement and close the raw COMMIT+BEGIN-between-checks ambiguity.

The design needs care: SQLite authorizer callbacks run during statement preparation, only one authorizer may be installed per connection, and the project already has an authorizer owner. The token must therefore be integrated into that single owner rather than installed as a competing callback.

### Fault-injecting VFS

A process crash after COMMIT exercises recovery but not every durability edge. A purpose-built VFS wrapper could count and selectively fail or drop `xWrite`, `xSync`, `xTruncate`, and directory-sync-equivalent operations. Each crash point would reopen the database and compare state against an oracle that permits only “entire transition visible” or “entire transition absent.” Contradictory parent/payload visibility would be a hard failure.

### Unified repository capability

Connection authority, guard-lifetime transaction state, schema snapshot, and payload repository access currently compose correctly but remain separate C++ objects. A move-only repository scope could own them together and expose only transaction-safe operations. This would reduce parameter plumbing and make destruction order a property of one type rather than a convention checked by a source audit.

### Bounded WAL evidence

Long-lived readers can delay checkpoints and allow WAL growth. Operator status should eventually report WAL/checkpoint pressure and enforce bounded read-snapshot duration. This is both an availability concern and an anonymity concern: unbounded retry or checkpoint timing can become an observable traffic side channel.
