# Rev0812 research notes

Research was limited to primary SQLite documentation and the implementation's
own source/evidence. Sources were reviewed on 2026-07-17.

## 1. `IF NOT EXISTS` is not an attestation primitive

SQLite documents that `CREATE TABLE IF NOT EXISTS` has no effect when a table or
view with the same name already exists and does not verify that the existing
object resembles the requested definition. This directly supports rev0812's
choice to establish true absence, execute a plain CREATE, and attest the stored
object before interpreting it as authority.

Primary source:

- SQLite CREATE TABLE documentation: https://sqlite.org/lang_createtable.html

## 2. `sqlite_schema.sql` preserves normalized creation SQL

SQLite's schema table records one row per schema object and stores normalized
CREATE SQL. The normalization is useful durable evidence but is not by itself a
complete shape proof: rev0812 also checks object type, table geometry, columns,
foreign keys, and program surfaces.

Primary source:

- SQLite schema table documentation: https://sqlite.org/schematab.html

## 3. Table metadata requires more than `table_info`

`PRAGMA table_xinfo` includes generated and hidden columns that ordinary
`table_info` can omit. `PRAGMA table_list` reports object type, column count,
WITHOUT ROWID, and STRICT properties. Rev0812 uses both so hidden or virtual
geometry cannot remain outside the reviewed proof.

Primary source:

- SQLite PRAGMA documentation: https://sqlite.org/pragma.html

## 4. Constraints are connection-state evidence

Foreign-key enforcement is connection-specific and can be disabled. SQLite also
exposes `ignore_check_constraints`. Therefore an exact stored CHECK or FOREIGN
KEY clause is not enough when the connection executing authority transitions is
not enforcing it. Rev0812 rejects the unsafe live profile before row
interpretation.

Primary sources:

- SQLite foreign-key documentation: https://sqlite.org/foreignkeys.html
- SQLite PRAGMA documentation: https://sqlite.org/pragma.html

## 5. Nested savepoints fit caller-owned transaction boundaries

SQLite savepoints can nest and RELEASE of an inner savepoint does not necessarily
make changes durable; outer rollback can still undo them. This matches the
schema boundary's requirement to make create/backfill/attestation atomic without
stealing the caller's commit authority.

Primary source:

- SQLite SAVEPOINT documentation: https://sqlite.org/lang_savepoint.html

## 6. Name handling is part of schema authority

SQLite identifiers are generally resolved without ASCII case sensitivity, while
stored schema text retains creation spelling and catalog comparison can use
normal text semantics. A case-sensitive existence query is therefore an unsafe
absence oracle for a reserved object name. Rev0812 scans and folds names in C++
instead of relying on SQL functions or collations that may be registered by the
connection.

Primary sources:

- SQLite language keywords and identifier behavior: https://sqlite.org/lang_keywords.html
- SQLite schema table documentation: https://sqlite.org/schematab.html

## 7. Defensive configuration remains layered, not absolute

SQLite recommends defensive configuration for applications that may process
hostile databases. Schema attestation, trusted-schema restrictions, exact value
extraction, authorizers, limits, and resource budgets are complementary. None
turns in-process hostile database parsing into a complete sandbox, so a
resource-bounded disposable worker remains a worthwhile future boundary.

Primary sources:

- SQLite security guidance: https://sqlite.org/security.html
- `SQLITE_DBCONFIG_DEFENSIVE`: https://sqlite.org/c3ref/c_dbconfig_defensive.html

## Design implications beyond rev0812

1. A durable authorization record needs a durable, versioned schema contract;
   row validation alone is insufficient.
2. The connection profile that gives constraints meaning should be represented
   as an explicit capability or attestation, not repeatedly rediscovered by
   unrelated call sites.
3. The next owner-state model should include schema and connection-profile
   transitions, not only owner row transitions.
4. A future migration protocol should record schema version and migration
   evidence rather than infer version solely from object shape.
5. Process isolation should return a small typed schema verdict bound to a
   sealed database snapshot or immutable handle, avoiding re-open races.
6. Exact local authority does not establish distributed convergence; operation
   algebra, causal dependencies, idempotency, and epoch compatibility still need
   an independent executable model.
