# Rev0860 research notes

Primary-source review used during the audit:

1. **SQLite database object name resolution** — unqualified object lookup
   searches the TEMP database first, then `main`, then attached databases. A
   schema-qualified reference searches only that schema. This directly
   motivates `main.sync_session_manifest_chunks` and the TEMP-shadow regression.
   https://sqlite.org/lang_naming.html

2. **SQLite integer representation** — SQLite records and the public
   `sqlite3_int64` interface use a signed 64-bit integer domain. Caller values
   outside that domain cannot be exact persisted INTEGER evidence and should be
   rejected before a data step.
   https://sqlite.org/capi3ref.html
   https://www.sqlite.org/fileformat.html

3. **Prepared statement lifecycle** — `sqlite3_reset()` makes a statement ready
   for re-execution but retains bound values; `sqlite3_clear_bindings()` is the
   separate operation that clears them. The owner deliberately performs both on
   success and failure.
   https://sqlite.org/c3ref/reset.html
   https://sqlite.org/c3ref/clear_bindings.html

4. **Regression discipline** — SQLite's own testing guidance treats a defect as
   fixed only after a reproducing regression is added and emphasizes testing
   both sides of defined limits. Rev0860 follows that pattern for TEMP
   redirection, signed-domain boundaries, duplicate rows, and exact limits.
   https://sqlite.org/testing.html

## Speculation

The current cube has many locally careful SQL statements but no first-class
notion of a *query authority*. A useful next abstraction would own:

- exact database generation and schema digest;
- explicit schema-qualified SQL;
- expected access path or index identity;
- maximum VM steps, rows, scalar bytes, aggregate bytes, and wall time;
- exact output cardinality and ordering; and
- the frozen caller value the query is permitted to authorize.

Such a capability would make accidental O(N) reconstruction, TEMP/attached
schema drift, and “query first, budget later” patterns structurally harder to
write. It could also become the request protocol for a future disposable
hostile-persistence worker, reducing how much SQLite interpretation remains in
the principal process.
