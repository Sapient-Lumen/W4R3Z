# rev0792 durable-schema defect reproduction

`schema_enforcement_stripping_reproducer.cpp` is compiled separately against
rev0791 and rev0792. It creates a valid ledger snapshot, uses SQLite's testing
`writable_schema` mechanism to replace only the stored
`ingress_sender_replay_cache` `CREATE TABLE` text, retains the primary key so the
automatic index remains valid, and removes every `NOT NULL`, `CHECK`, default,
and `FOREIGN KEY` clause.

Rev0791 accepted the source and restored the weakened schema. Rev0792 rejects it
at the source read-only preflight with the typed, value-free
`schema_sql_mismatch` failure. Both binaries returned zero because the
reproducer reports observed behavior rather than encoding the expected revision
as process success/failure.

The parent compatibility log loads an untouched canonical rev0791 schema through
rev0792, proving the exact contract is not merely self-compatible with newly
created rev0792 files. The TSV is the exact explicit `sqlite_schema` projection
from that canonical parent database; SQL-NULL automatic indexes are omitted.
