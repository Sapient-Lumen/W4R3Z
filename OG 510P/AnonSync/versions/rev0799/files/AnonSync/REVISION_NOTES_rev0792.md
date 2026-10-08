# AnonSync rev0792 — schema truth before repair, one exact DDL owner

Prepared from the supplied and independently verified parent archive
`AnonSync-rev0791-2026.07.15.01.52-replaytruth-fkfence-exacttuple-overflowproof.zip`.
Its SHA-256 and the complete 25-check parent-package verification are recorded
under `REVISION_EVIDENCE/rev0792/lineage/`.

## Mission

AnonSync's heart is **evidence-authorized convergence**. Durable bytes may be
promoted after restart or restore only when the boundary that owns each
invariant verifies the exact evidence needed for the transition. Schema is part
of that evidence: familiar table and column names do not prove that future
writes will enforce the protocol relationships the application assumes.

## Severe durable-schema promotion defect corrected

Rev0791's read-only verifier inventoried expected tables/indexes and checked
column-name sets. It did not attest exact table DDL. Index checks searched for a
few substrings. Therefore a table could retain the expected name, columns, and
primary key while losing `NOT NULL`, `CHECK`, defaults, and `FOREIGN KEY`
clauses.

The preserved reproducer starts with a valid snapshot, enables
`writable_schema`, and replaces only the stored
`ingress_sender_replay_cache` table definition. All rows remain valid and the
primary-key autoindex remains usable. Rev0791 accepted and propagated the
weakened schema:

```text
weakened_schema_restore_accepted=true
restored_schema_has_foreign_key=false
restored_schema_has_not_null=false
restored_schema_has_check=false
```

`PRAGMA foreign_key_check` cannot close this gap: it reports violations of
foreign keys that are declared. A removed `REFERENCES` clause leaves no
constraint to check. `integrity_check` proves low-level consistency and selected
constraints, not the intended application schema.

Rev0792 rejects the same source before staging or publication:

```text
weakened_schema_restore_accepted=false
rejection=sqlite-wal snapshot restore source read-only verifier schema contract rejected: sqlite_replay_ledger_schema[schema_sql_mismatch]:ingress_sender_replay_cache
```

## Refactor: one versioned schema owner

`src/persistence/sqlite_replay_ledger_schema_contract.*` is a pure C++ boundary
that owns all 14 explicit schema objects for ledger schema version 10:

- eight tables;
- six named indexes;
- exact object type and target table;
- exact normalized `sqlite_schema.sql` text; and
- the backend profile constants coupled to that schema version.

The owner returns typed, value-free failures for unexpected, duplicate,
missing, wrong-type, wrong-target, and SQL-mismatched objects. Hostile observed
names or SQL are never copied into diagnostics.

Creation now consumes the same definitions used for verification. New ledgers
are created inside one immediate transaction, initialized, committed, and then
attested from SQLite's stored schema representation. Existing nonempty ledgers
are attested before journal-mode mutation and before any creation DDL. Existing
ledgers never pass through `CREATE ... IF NOT EXISTS`, so startup cannot silently
repair a missing index and then mistake the repaired result for historical
truth.

The snapshot adapter reads bounded exact TEXT values for
`(type, name, tbl_name, sql)` and stops after one object beyond the contract
size. It selects all explicit objects with non-null SQL. This excludes only
SQLite's SQL-NULL automatic indexes; explicit `sqlite_*` objects such as
`sqlite_stat1`, hidden/generated-column substitutions, extra views/triggers, and
other additions are visible and rejected.

## Adversarial proof

The 499-check focused test mutates every expected object through missing,
duplicate, wrong-type, wrong-target, and changed-SQL cases; checks create
statement identity; verifies diagnostics do not leak hostile bytes; and covers
stripped constraints, a generated hidden column, and a widened nonce uniqueness
index.

The 31-check integrated proof covers:

- valid new creation, backup, restore, and reload;
- exact compatibility with the canonical parent schema;
- weakened table DDL rejected on restore and live startup;
- no repair after a failed live preflight;
- a deleted required index rejected rather than recreated;
- an `ANALYZE`-created explicit statistics table rejected;
- semantically equivalent but differently serialized DDL rejected; and
- no destination publication after a rejected restore.

## Verification economics

The focused boundary compiles 4 Ninja actions, 2 first-party translation units,
448 lines, and 23,413 bytes. The full core requires 49 actions and 53,767
first-party lines—120.02× the line exposure and 12.25× the action count. The
integrated proof still exposes 53,458 first-party lines plus the SQLite
amalgamation.

This is a useful refactor rather than a cosmetic split: schema definitions,
comparison semantics, typed failures, and adversarial mutation tests are cheap
and independent; only exact SQLite acquisition and publication remain in the
large ledger translation unit.

## Validation

Required gates passed:

- GCC 14 Debug/`-Werror`, full build and **52/52 CTest**;
- focused schema-contract proof, **499 checks × 20/20**;
- integrated schema integrity proof, **31 checks × 20/20**;
- focused GCC ASan/UBSan, **5/5**;
- Clang 17 `-Wconversion -Wsign-conversion -Werror`, **5/5**;
- GCC 14 `-O3 -DNDEBUG` with conversion warnings and `-Werror`, **5/5**;
- ten deterministic authority audits, all exit zero; and
- immediate rev0791 package verification, **25/25**.

The integrated ASan/UBSan target did not finish compiling the large core archive
within the execution window, so no integrated sanitizer completion is claimed.
The bundled SQLite amalgamation was intentionally not instrumented in the
focused first-party lane.

## Explicit proof boundary

Rev0792 proves that a version-10 ledger's explicit stored DDL is exactly the
canonical enforcement program before existing durable state is promoted, and
that new creation and verification have one owner. It retains independent
integrity, foreign-key, exact scalar, hash-chain, row-semantic, and cross-row
checks; exact DDL complements rather than replaces those proofs.

It does not prove replay-row original provenance. Replay evidence remains
outside the prepared decision hash material, and deletion remains ambiguous
with legitimate pruning. It also does not fully bound hostile snapshot file
size, page count, row count, VDBE work, wall time, SQLite heap, or allocation
volume.

## Highest-value next work

1. Bind a canonical replay-evidence digest and auditable pruning policy into a
   new prepared-entry material/schema version, with explicit migration and
   downgrade rejection.
2. Add a versioned untrusted-snapshot resource profile: file/page ceilings,
   row budgets, progress interruption, cache/heap limits, and deterministic
   compatibility behavior.
3. Build the fault-injecting VFS plus protocol state oracle for crash cuts across
   database, WAL/journal, sidecar, checkpoint, receipt, and filesystem
   publication boundaries.
4. Formalize the convergence and privacy/adversary contracts before expanding
   claims implied by the project name.
5. Continue extracting independently expressible invariant owners from the
   replay ledger and 24k-line domain unit.
