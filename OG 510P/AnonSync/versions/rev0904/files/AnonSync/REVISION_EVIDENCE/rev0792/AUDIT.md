# rev0792 deep audit — schema declarations are durable authority

## The heart of the mission

AnonSync exists to converge replicas without laundering observations into
authority. That rule applies not only to rows and hashes, but also to the program
that governs future rows. A database that opens successfully and returns the
expected columns is not proof that its primary keys, foreign keys, defaults,
checks, uniqueness scopes, and type/nullability rules remain the ones the
protocol authorized.

The SQLite schema is therefore evidence at two distinct moments:

1. **restart/restore:** prove what enforcement program is already durable before
   promoting rows or making the database writable;
2. **creation:** produce one canonical program transactionally, then read back
   and verify what SQLite actually stored.

A repair action must not occur between those moments. Repairing a missing object
before verification destroys the evidence needed to distinguish historical
truth from startup intervention.

## What had gone severely wrong

### Expected names and columns masqueraded as exact schema proof

Rev0791 enumerated eight expected tables and six expected named indexes. Tables
were checked with `PRAGMA table_info`; indexes were checked by searching the
stored SQL for selected words. The verifier did not prove table constraints,
defaults, affinity declarations, generated/hidden columns, exact index column
order, partial predicates, collations, expressions, or additional indexed
columns.

The preserved reproducer keeps the expected table name, all fifteen expected
columns, and the primary key needed by the existing automatic index. It removes
all `NOT NULL`, `CHECK`, default, and `FOREIGN KEY` clauses. The current rows
remain well formed, so every row-semantic and hash-chain check passes.

### A clean foreign-key scan was allowed to imply a missing declaration

`foreign_key_check` evaluates declared relationships. Removing the declaration
removes the thing being checked. Rev0791 therefore accepted “no reported
violations” as if it also proved “the required foreign key exists.” That is an
absence-of-evidence inversion at the exact boundary where durable authority is
reconstructed.

### Restore copied the weakened program into future authority

After source verification, SQLite backup copied the database into a staged temp
file and then the active destination. Because the verifier accepted the source,
the weakened schema became the enforcement program for future writes.

### Live startup mixed verification with repair

Existing ledgers ran `CREATE ... IF NOT EXISTS` before their durable schema was
fully attested. A missing expected index could be created during startup and the
resulting state then treated as if it had been the historical state. A malformed
object with the expected name would not be repaired, producing inconsistent
behavior depending on the form of tampering.

## What changed

### One pure, versioned owner

`sqlite_replay_ledger_schema_contract.*` owns the exact normalized SQL and object
identity for all 14 explicit version-10 schema objects. It has no SQLite handle,
filesystem access, crypto, runtime singleton, or dependency on the application
core. Its result language is small and typed:

- unexpected object;
- duplicate object name;
- type mismatch;
- target-table mismatch;
- stored-SQL mismatch; and
- missing object.

Diagnostics contain only the failure category and a trusted expected object name
when one exists. Untrusted observed names or SQL never enter the message.

### Creation and verification now consume the same definitions

The ledger no longer owns a second hand-written DDL block. New databases iterate
the schema contract in one `BEGIN IMMEDIATE` transaction, initialize required
singleton rows, commit, and attest the stored schema. The core cannot silently
drift from the focused owner because CMake keeps the implementation outside the
core source list and both creation and verification call the owner.

### Existing state is verified before repair-capable DDL

A nonempty existing database is opened, trusted schema is disabled, and its
explicit schema is attested before journal-mode changes or any creation DDL. The
existing path never invokes schema creation. A rejected file is not repaired.

### Exact acquisition is bounded

The adapter reads exact SQLite TEXT storage classes and explicit bytes for
`type`, `name`, `tbl_name`, and `sql`. Field sizes are capped; enumeration stops
one object past the expected count. It selects every schema object whose SQL is
non-null, which excludes SQLite's automatic indexes but includes explicit
reserved-prefix objects such as `sqlite_stat1`.

### Existing proofs remain independent

Exact DDL is necessary but insufficient. Rev0792 retains:

- SQLite integrity checking;
- foreign-key violation scanning;
- exact scalar storage-class/byte extraction;
- hash-chain reconstruction;
- row grammar/range/uniqueness checks;
- replay-to-prepared tuple verification; and
- outbox/transition cross-table verification.

Each check has a different owner and failure meaning.

## Verification capacity and waste

The pure owner plus focused test is 448 first-party lines in 4 Ninja actions. The
integrated proof compiles 53,458 first-party lines in 49 actions; the core exposes
53,767 lines in 49 actions. The line-exposure ratios are 119.33× and 120.02×.

The focused ASan/UBSan lane completed five times. The integrated sanitizer build
did not finish the large core archive. This is not merely build inconvenience:
monolithic translation units directly consume the time available for dynamic
assurance. `sync_domain.cpp` remains 24,531 lines and
`sqlite_replay_ledger.cpp`, although reduced by this extraction, remains 4,514
lines with several unrelated durable protocols.

## Exactness tradeoff

Rev0792 treats schema version 10 as one canonical stored serialization. A
semantically equivalent reformat, an `ANALYZE`-created statistics table, or a
locally extended schema is rejected. This is intentionally strict: broadening
acceptance without a new version would turn schema identity back into a fuzzy
policy.

The cost is explicit migration work. A future revision must define accepted
input versions, a deterministic transform, a canonical output contract,
transaction/crash behavior, and downgrade rejection. It must not weaken version
10 in place to make old local alterations pass.

## What is still missing

### P0 — replay evidence provenance

Rev0791 verifies replay rows against an existing prepared tuple, but replay
evidence is not cryptographically included in the prepared decision material.
Valid-shaped substitution and deletion-versus-pruning ambiguity remain. A new
material/schema version should commit to a canonical replay-evidence digest and
auditable pruning policy.

### P0 — crash-cut combined-state oracle

Build a fault-injecting VFS plus protocol oracle that cuts writes, syncs,
truncates, WAL/journal publication, locks, sidecars, receipts, checkpoints, and
filesystem renames; restarts separately; and evaluates whether the combined
state is a protocol-permitted outcome, not merely whether SQLite is readable.

### P0 — explicit privacy/adversary model

Authentication, signatures, replay protection, and local persistence do not
establish content confidentiality, metadata privacy, anonymity, forward
secrecy, post-compromise recovery, or secret-memory lifecycle. The project name
must not outrun a versioned threat model and executable claims.

### P1 — bounded untrusted snapshot profile

Field caps and schema-object caps exist, but total file/page size, row count,
VDBE work, wall time, cache/heap, and allocation volume remain incompletely
bounded. Add a versioned resource contract with deterministic interruption and
compatibility tests.

### P1 — live defensive connection profile

The read-only untrusted snapshot verifier enables SQLite defensive mode. The
live writable path now attests exact schema before use but does not yet expose a
complete, independently tested defensive-mode policy for its entire lifetime.

### P1 — executable convergence contract

Model commutativity, idempotence, monotonicity, causality, deletion/edit races,
partitions, duplication, reordering, restart, and key epochs independently of
the production implementation, then differential-test generated traces.

## Proof boundary for rev0792

Rev0792 proves exact canonical explicit DDL for schema version 10 on new
creation, live restart, snapshot verification, staged restore, and final restore.
It proves that creation and verification have one semantic owner and that
failure occurs before repair/publication. It does not claim replay provenance,
full resource containment, integrated sanitizer completion, crash durability,
formal convergence, Byzantine safety, content confidentiality, metadata
privacy, or anonymity.
