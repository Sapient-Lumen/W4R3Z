# AnonSync rev0812 revision notes

## Mission-level result

Rev0812 makes the durable schema carrying checkpoint-owner authority part of the
authority proof itself. A successful `CREATE TABLE IF NOT EXISTS`, prepared
query, returned row, or satisfied row-level predicate is no longer enough: the
recipient first proves the reviewed `main`-schema objects, column and foreign-key
geometry, program surface, TEMP absence, and live constraint-enforcement profile
on the connection and transaction snapshot that will contain the transition.

This follows AnonSync's central rule: observation is not authority, and the
boundary that owns a state transition must verify the exact evidence it relies
on before any destructive or authority-bearing effect.

## Parent and lineage

The exact parent is:

`AnonSync-rev0811-2026.07.17.01.05-stickyowner-cascadepermit-repairlease-lineagerepair.zip`

SHA-256:

`8d8b873a832281e6c24e5999c44ebdb8624b616c6ad520c122326006f6760fdc`

The parent ZIP passes 25/25 package-verifier checks when pinned to rev0811. Its
canonical extracted `AnonSync/` directory passes 21/21. Rev0812 was derived from
that exact extracted source. No build output was used as source, and no bundled
third-party file changed.

## Severe defect corrected

Rev0811's sticky owner-mode bootstrap used `CREATE TABLE IF NOT EXISTS`. SQLite
may successfully perform no creation when a same-named table or view already
exists. The successful call therefore did not establish that the existing
object had the reviewed SQL, constraints, columns, foreign keys, type, rowid
geometry, or trigger surface.

Because the object stores whether capability-bearing ownership is permanently
required, a permissive lookalike could turn malformed or partially constrained
rows into apparent authority. A hostile legacy owner-lock table could also be
read and backfilled before its own schema was authenticated. TEMP aliases and
mixed-case aliases enlarged the confusion surface.

## Production corrections

### 1. Focused owner-schema invariant boundary

Added `sync_checkpoint_owner_schema.hpp/.cpp`. The boundary owns:

- exact reviewed owner-mode and owner-lock SQL;
- C++ ASCII case folding of SQLite object names;
- SQL-bearing `main.sqlite_schema` inspection;
- TEMP-object rejection;
- `table_list`, `table_xinfo`, rowid, STRICT, default, hidden-column, primary-key,
  and foreign-key geometry;
- unexpected index/view/trigger rejection;
- checkpoint-root trigger rejection and root `session_id` anchor verification;
- live `foreign_keys` and `ignore_check_constraints` profile verification;
- true-absence creation without `IF NOT EXISTS`;
- legacy owner-row backfill; and
- post-migration re-attestation.

### 2. Savepoint-atomic migration

Schema creation, legacy backfill, and post-write attestation now run inside the
nested savepoint `anonsync_checkpoint_owner_schema_migration`. Any exception
rolls back to and releases that savepoint. A failed malformed-row backfill
therefore cannot leave a newly created mode table behind. When invoked inside a
caller transaction, releasing the nested savepoint does not commit the caller's
transaction; a focused proof rolls the outer transaction back and confirms the
created schema disappears.

### 3. Live constraint enforcement is required

Exact DDL is not useful authority evidence if its constraints are disabled on
the current connection. Attestation now rejects `PRAGMA foreign_keys=0` and
`PRAGMA ignore_check_constraints=1` before rows are interpreted. The focused
corpus proves rejection has no migration side effect.

### 4. Case-insensitive SQLite names are handled without programmable SQL

SQLite object resolution is case-insensitive, while ordinary catalog equality
can be case-sensitive. The verifier scans the catalog and folds ASCII names in
C++ rather than calling SQL `lower()` or depending on a connection-programmable
collation. Mixed-case `main` and TEMP aliases are rejected as occupied authority
names, not misclassified as absence.

### 5. Recipient SQL and ordering are tightened

Owner authority SQL is explicitly `main.` qualified. Acquisition, release,
recipient authorization, root-reset authorization, and reset consumption all
attest the schema before interpreting owner evidence. Legacy backfill was
removed from the recipient runtime; it now has one owner in the schema boundary.
The recipient implementation shrank from 912 to 889 lines.

### 6. Shared schema canonicalizer refactor

`sync_sqlite_schema_identity.cpp` is now compiled once in the independent
`anonsync_sqlite_schema_identity` target. Peer-ingress and checkpoint-owner
schema boundaries link that target. Configure-time guards reject duplicate
source ownership or any focused dependency on `anonsync_core_lib`.

## Audit corrections found during integration

The first complete integration attempt exposed three structural failures even
though behavioral tests passed. The new verifier directly inspected one SQLite
column type, bypassing the exact scalar owner, and two inventories encoded the
old schema-canonicalizer target ownership.

The final implementation routes optional/default inspection through
`sqlite_exact_optional_text_or_throw`, leaves zero unreviewed direct SQLite
extractions, and updates both global ownership inventories. The failed 84/87
run is retained as defect evidence; it is not used as final validation.

## Source delta

Eight active files changed: four modified and four added. The exact textual delta
is 1,849 added and 82 removed lines.

Key sizes after the change:

- `src/sync_checkpoint_owner_schema.cpp`: 735 lines;
- `src/sync_checkpoint_owner_schema.hpp`: 26 lines;
- `src/sync_checkpoint_owner_fence.cpp`: 889 lines;
- `tests/sync_checkpoint_owner_schema_test.cpp`: 651 lines;
- `tests/sync_checkpoint_owner_fence_sqlite_test.cpp`: 1,126 lines;
- `src/sync_domain.cpp`: unchanged at 15,371 lines.

Exact hashes and the unified active-source patch are retained in
`REVISION_EVIDENCE/rev0812/CHANGESET.json` and
`REVISION_EVIDENCE/rev0812/SOURCE_DIFF_rev0811_to_rev0812.patch`.

## Final validation

- Current Release/NDEBUG all-target graph completed with GCC 14.2, C++20,
  bundled SQLite 3.53.3, Ninja 1.12.1, and explicit `-O1`. The final command was
  incremental against the same previously complete build tree; a fresh build or
  default `-O3` claim is not made.
- One complete CTest invocation: 87/87 in 43.32 seconds.
- Domain model: 594/594.
- Owner policy: 39/39.
- Owner schema: 31/31.
- Owner SQLite recipient: 42/42.
- Owner source audit: 50/50.
- Peer schema ownership audit: 26/26.
- SQLite scalar extraction audit: 30/30.
- Runtime selftest separation: 9/9.
- Domain selftest separation: 13/13.
- Scheduler source separation: 22/22.
- Advertised and registered selftests: 38/38.
- Ten focused repeat iterations: 1,120/1,120 assertions.
- Strict GCC/Clang compilation: 8/8 compiler-unit combinations.
- Focused GCC ASan/UBSan: 3/3 binaries and 112/112 checks. Leak detection and
  bundled-SQLite instrumentation were disabled; no full-program sanitizer claim
  is made.

## Remaining boundaries

The result is local to compliant participants sharing one SQLite database and
VFS. Time remains caller supplied. The administrative-disable state has no
complete authorization/audit/reactivation protocol. The complete checkpoint
root is not exact-schema-attested. Hostile schema interpretation remains in the
long-lived process. SQLite and filesystem publication are not one crash-atomic
transaction. Distributed convergence, privacy, encryption, metadata leakage,
key lifecycle, forward secrecy, and post-compromise recovery remain separate
unproved protocols.
