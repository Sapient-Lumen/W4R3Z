# rev0792 research notes

Accessed 2026-07-15. Primary technical sources are official SQLite
documentation.

## `sqlite_schema.sql` is the stored enforcement program

SQLite documents one schema-table row for each table, explicit index, view, and
trigger. Its `sql` field contains normalized `CREATE` text that would recreate
the object. The documented normalization uppercases initial keywords, removes
`TEMP` and database qualifiers, trims leading space, and normalizes the first
keyword spacing. SQL is null for internal indexes automatically created by
`UNIQUE` and `PRIMARY KEY` constraints.

That makes the exact non-null `(type, name, tbl_name, sql)` projection an
appropriate versioned evidence surface for AnonSync's application schema. It is
stronger than checking that familiar names or column tokens occur somewhere in
DDL.

Source: https://www.sqlite.org/schematab.html

## Foreign-key scans cannot prove that a foreign key exists

`PRAGMA foreign_key_check` returns violations of declared foreign-key
constraints. If an attacker removes the `REFERENCES` clause itself, there is no
constraint for the pragma to evaluate and no violation row to return. A clean
result is therefore relationship evidence only after the schema declaration is
independently attested.

Source: https://www.sqlite.org/pragma.html#pragma_foreign_key_check

## Integrity checking is complementary, not a schema contract

SQLite documents `PRAGMA integrity_check` as low-level consistency plus selected
constraint/index checks and explicitly notes that it does not find foreign-key
errors. Rev0792 retains integrity, foreign-key, exact scalar, row-semantic, and
hash-chain checks. Exact DDL attestation does not replace them; each proves a
different property.

Source: https://www.sqlite.org/pragma.html#pragma_integrity_check

## `table_info` omits generated and hidden columns

SQLite documents that `PRAGMA table_info` does not show generated or hidden
columns; `table_xinfo` is required for those. Rev0791's exact column-name set was
therefore not an exact table-shape proof even apart from missing constraints.
Rev0792 compares the canonical stored `CREATE TABLE` program and explicitly
tests a generated-column substitution.

Sources:

- https://www.sqlite.org/pragma.html#pragma_table_info
- https://www.sqlite.org/gencol.html

## Defensive mode and direct schema rewriting

SQLite describes `PRAGMA writable_schema` as a testing-oriented mechanism and
warns that direct schema-table changes risk corruption. The reproducer does not
propose it as an application workflow; it is a compact way to construct bytes
that an untrusted snapshot or local modifier could supply. SQLite's defensive
connection option disables writable-schema and related hazardous behaviors.
AnonSync already enables defensive mode on the dedicated untrusted read-only
snapshot connection. Live writable connections still rely on a closed SQL
surface and exact startup preflight rather than a fully documented global
defensive profile; that remains follow-up work.

Sources:

- https://www.sqlite.org/howtocorrupt.html
- https://www.sqlite.org/c3ref/c_dbconfig_defensive.html

## Design implication

Exact SQL identity is intentionally stricter than semantic equivalence. Schema
version 10 now names one canonical serialization. A differently formatted but
otherwise equivalent definition, an `ANALYZE`-created explicit statistics table,
or a locally altered schema fails closed. A future schema change should use an
explicit input contract, migration transform, output contract, and downgrade
proof rather than broadening version 10's acceptance language.
