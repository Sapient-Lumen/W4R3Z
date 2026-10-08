# Rev0812 audit: authority-bearing SQLite schema and atomic migration

## Scope

This review followed checkpoint-owner authority from schema bootstrap through
legacy migration, owner generation acquisition/release, recipient mutation,
checkpoint-root reset, CMake target ownership, focused tests, global SQLite
scalar extraction, and the complete registered test graph.

The rev0811 parent was treated as the exact source baseline. The audit did not
infer safety from successful SQL execution or valid-looking rows; it asked
whether the current connection and transaction snapshot proved the schema and
constraint machinery that gave those rows meaning.

## Severe finding

### `CREATE TABLE IF NOT EXISTS` was being mistaken for schema authority

Severity: authority confusion / constraint substitution.

The sticky owner-mode row determines whether a session that once entered
owner-fenced mode may ever mutate without a current capability. Rev0811 created
that table with `CREATE TABLE IF NOT EXISTS`, then queried it by name. A
same-named preexisting table or view could cause successful bootstrap without
matching the reviewed definition. Row-level policy rejected many malformed
values, but it did not prove:

- the object was a table rather than a view;
- the table had only the reviewed columns and defaults;
- required CHECK and primary-key constraints existed;
- the mode table remained independent of checkpoint-root cascades;
- the legacy owner table had exactly the reviewed cascade edge;
- no trigger program could rewrite, suppress, duplicate, or redirect effects;
- no TEMP object shadowed an unqualified authority name; or
- constraint enforcement was enabled on the live connection.

This was particularly serious because schema bootstrap also backfilled legacy
owner rows. A malformed legacy row could fail after the new mode table had
already been created, leaving a partial migration artifact.

## Correction

### Exact schema owner

Rev0812 adds `sync_checkpoint_owner_schema.cpp`, a focused independently linked
invariant owner. It verifies the owner-mode table and optional legacy owner-lock
table through several mutually reinforcing observations:

1. scan every SQL-bearing `main.sqlite_schema` object whose name or target table
   matches a reserved owner name, using C++ ASCII case folding;
2. require one exact table object and canonicalized stored SQL;
3. require exact `PRAGMA main.table_list` type, column count, rowid, and STRICT
   geometry;
4. require exact `pragma_table_xinfo(..., 'main')` order, names, declared types,
   NULL/default, primary-key, and hidden-column geometry;
5. require no owner-mode foreign key and one exact owner-lock cascade foreign
   key into the checkpoint root;
6. reject unexpected explicit indexes, views, triggers, TEMP objects, and
   checkpoint-root triggers;
7. require the root object and its `session_id` anchor; and
8. require live foreign-key and CHECK-constraint enforcement.

Authority-bearing runtime SQL is `main.` qualified, and every owner transition
attests before interpreting durable evidence.

### Atomic bootstrap and backfill

True absence is established before executing a plain `CREATE TABLE main...`
statement. Legacy owner-lock schema is attested before mode creation. Creation,
legacy backfill, post-write attestation, and publication all occur under a
nested savepoint. The exception path rolls back and releases the savepoint.

The focused corpus proves:

- a malformed legacy row causes backfill failure and removes the newly created
  mode table;
- the hostile legacy row remains for diagnosis rather than being partly
  rewritten;
- the savepoint is closed after failure;
- a caller-owned outer transaction remains active after successful ensure; and
- rolling back that outer transaction removes the schema created under the
  nested savepoint.

### Case-insensitive names without programmable resolution

SQLite resolves object names without ASCII case sensitivity, while ordinary
catalog equality may not. A query such as `WHERE name=?` could misclassify a
mixed-case alias as absence. Rev0812 scans the catalog and compares names in C++.
It intentionally avoids SQL `lower()` and collation-dependent equality because
functions and collations are connection-programmable surfaces.

### Live constraints are part of the proof

Exact DDL text is not enough if the current connection has disabled enforcement.
The boundary rejects foreign keys off or CHECK constraints ignored before any
owner row is treated as authority. Focused tests verify both refusals occur
without schema or row side effects.

## Refactor performed

The resulting dependency graph is:

```text
anonsync_core_lib
  -> anonsync_sync_checkpoint_owner_fence
       -> anonsync_sync_checkpoint_owner_schema
            -> anonsync_sqlite_schema_identity
            -> anonsync_sqlite_support / exact-value boundary
       -> anonsync_sync_checkpoint_owner_fence_policy

anonsync_peer_ingress_schema
  -> anonsync_sqlite_schema_identity
```

The schema canonicalizer is no longer privately compiled by peer ingress. It has
one CMake source owner and two focused consumers. Neither focused proof links the
core monolith. Legacy backfill moved out of the recipient runtime, reducing it
from 912 to 889 lines.

## Integration audit finding

The first whole-suite attempt passed behavior but failed three structural gates:

- one direct `sqlite3_column_type` use bypassed exact-value ownership;
- the peer schema target audit encoded private canonicalizer compilation; and
- the active persistence inventory had not learned the new focused boundary.

Those failures were correct. The implementation now uses
`sqlite_exact_optional_text_or_throw`, the canonicalizer has one independent
CMake owner, and the active persistence inventory reports zero unreviewed direct
extractions. The 84/87 run is retained at
`validation/ctest-integration-regression-before-fix.log` as negative evidence.

## Proof surface

The 50-check owner source audit verifies, among other obligations:

- exact public capability geometry and propagation;
- dependency direction and no-core focused linkage;
- removal of `IF NOT EXISTS` from authority bootstrap;
- hostile legacy schema rejection before migration mutation;
- live constraint enforcement;
- SQL, columns, foreign keys, object programs, and TEMP attestation;
- savepoint ordering and rollback behavior;
- one schema/bootstrap/backfill owner;
- C++ name folding rather than programmable SQL folding;
- explicit `main.` qualification;
- attestation before every owner transition;
- typed write-transaction and reset-permit ordering;
- exact acquisition/release compare-and-replace and proof reload;
- operator repair lease acquisition, propagation, and retirement;
- filesystem-effect reservation ordering;
- adversarial focused and domain corpora;
- shared canonicalizer source ownership; and
- CTest and sanitizer graph registration.

Final behavioral and structural evidence:

- complete CTest: 87/87;
- sync-domain model: 594/594;
- owner policy: 39/39;
- owner schema: 31/31;
- owner recipient SQLite: 42/42;
- owner source audit: 50/50;
- peer schema ownership: 26/26;
- SQLite scalar extraction: 30/30;
- ten focused iterations: 1,120 assertions;
- strict GCC/Clang: 8/8 combinations; and
- focused ASan/UBSan: 3/3 binaries, 112/112 checks.

## Remaining high-risk gaps

### Complete root schema identity

The owner boundary verifies that the checkpoint root is the reviewed table name
and contains the required `session_id` anchor, and it rejects root triggers. It
does not pin every checkpoint-root column and constraint. The larger checkpoint
schema still needs a versioned exact contract.

### Administrative disable

`administratively-disabled` is a representable state, not a complete protocol.
A safe production transition needs real administrative authorization, prior
owner generation and policy/key-epoch binding, immutable audit evidence,
replay/idempotency rules, retention, reactivation semantics, and crash recovery.

### Hostile database process isolation

Schema SQL tokenization and SQLite catalog interpretation remain in the
long-lived process. Exact geometry and connection checks reduce authority
confusion but do not bound parser, allocator, CPU, descriptor, or kernel
resource failures. A disposable worker remains the stronger boundary.

### Cooperative time and local serialization

Lease and observation epochs are caller supplied. SQLite serialization applies
only to compliant participants sharing one database/VFS, not to devices or
independent stores.

### Crash atomicity and convergence

Database commit and filesystem publication are not one crash-atomic protocol.
The project still lacks an exhaustive crash-cut oracle and executable
convergence algebra. Privacy, payload confidentiality, metadata leakage, key
rotation, forward secrecy, and post-compromise recovery are separate unproved
missions.
