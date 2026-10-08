# AnonSync revision notes — rev0891

## Revision theme

Rev0891 turns rev0890's immutable TLS membership value into durable accepted-
session authority. The parent snapshot was canonical and callback-free, but any
caller could construct one with any positive policy label. The new
`SyncReplicaTlsMembershipSqliteOwner` owns an append-only SQLite history,
reconstructs every retained snapshot, performs exact compare-and-swap
publication, emits move-only authority only for committed state, and optionally
checks an externally retained generation/digest anchor for rollback or fork.

The revision also replaces the accepted server's borrowed raw `SSL_CTX*` with a
move-only retained OpenSSL reference, audits the SQLite connection and schema
closure, corrects a ceiling-crossing append defect discovered during review,
and moves caller-visible authority allocation before commit so allocation
failure rolls policy publication back.

## Parent

The exact parent handoff is:

`AnonSync-rev0890-2026.07.23.08.18-immutablesnapshot-callbackretirement-servicebinding-evidenceseal.zip`

The parent archive digest and exact parent-relative delta are recorded under
`REVISION_EVIDENCE/rev0891/` in the sealed artifact.

## Production C++ changes

### Durable membership history owner

Added:

- `src/sync_replica_tls_membership_sqlite_owner.hpp`
- `src/sync_replica_tls_membership_sqlite_owner.cpp`

The owner persists three exact `STRICT` tables for metadata, update history, and
complete per-generation entries. It binds one folder and local actor at genesis,
uses domain-separated canonical snapshot and chain digests, requires contiguous
state generation and strictly increasing policy epoch, and reconstructs the
complete chain on every read and write.

Publication validates and allocates caller-controlled candidate state before
writer authority, enters `BEGIN IMMEDIATE`, performs complete reconstruction,
compares one exact expected anchor, enforces retention ceilings, appends the
history and entries, advances metadata, allocates the return capability, commits,
and only then returns authority.

A separately retained anchor can detect whole-database rollback below its
generation or divergence through that exact generation. The digest chain is
unkeyed and is not signed provenance.

### Connection and schema ownership

The owner installs and re-attests a dedicated SQLite profile: defensive mode,
untrusted schema, disabled schema triggers/views/extensions/attachments, no
dirty reads, active CHECK constraints, zero attached-database and trigger-depth
limits, and no schema other than `main`/optional `temp`.

Main schema closure now counts both reserved-prefix objects and arbitrary-named
objects attached to an owned table. TEMP schema closure rejects connection-local
objects attached to owned tables. This corrects the prefix-only shape that
would have missed an arbitrary-named index or TEMP trigger.

The owner requires a named writable database, WAL with at least `FULL`, or
rollback `DELETE`/`TRUNCATE`/`PERSIST` with `EXTRA`. These are necessary SQLite
policy observations, not proof of the underlying storage stack.

### Retention crossing fix

Hard limits existed for 65,536 history records and 4,194,304 retained entry
rows, but the first implementation enforced them only when reading. The append
that crossed a limit could therefore commit and make all later reconstruction
fail. Publication now checks the exact retained totals under its writer
transaction before inserting. A pure planning predicate has exact boundary
coverage but does not replace the transactional check.

### Immutable snapshot integration

Extended:

- `src/sync_replica_tls_membership_snapshot.hpp`
- `src/sync_replica_tls_membership_snapshot.cpp`

The snapshot exposes a read-only span over its already canonical sorted entries
so the durable owner can persist the exact sequence without a second
normalization interface.

### Accepted TLS server authority

Extended:

- `src/sync_replica_file_tls_server.hpp`
- `src/sync_replica_file_tls_server.cpp`

The server now consumes `SyncReplicaTlsMembershipAuthority`, not a raw snapshot.
Every terminal result carries state generation, policy epoch, entry count,
snapshot digest, previous chain digest, and current chain digest.

A new `SyncReplicaFileTlsServerContext` retains `SSL_CTX` with
`SSL_CTX_up_ref`/`SSL_CTX_free`. The server takes the wrapper by value and
allocates connection-local `SSL` state before spending accept authority.
Context lifetime is owned; concurrent context mutation remains caller-prohibited.

### Build graph refactor

The snapshot and durable owner are built as the focused
`anonsync_sync_replica_tls_membership` library. The accepted server links that
library publicly instead of compiling membership persistence into the server
translation unit. This separates policy-history churn from socket/session
implementation while adding only one semantically coherent target.

## Runtime coverage

Added:

- `tests/sync_replica_tls_membership_sqlite_owner_test.hpp`
- `tests/sync_replica_tls_membership_sqlite_owner_test.cpp`

Extended:

- `tests/sync_replica_tls_transport_test.cpp`

The compiled matrix covers concurrent first open, exact genesis, no pre-policy
authority, connection-profile installation and mutation, attached-schema
rejection, durability modes, integer and retention boundaries, canonical
publication, restart, stale compare-and-swap across independent connections,
rotation, trusted-anchor extension, rollback/fork detection, identity mismatch,
row/chain/orphan/schema/TEMP-trigger tamper, and end-to-end real TLS attribution.

## Audit and refactor work

Added:

- `tools/audit_sync_tls_membership_sqlite_owner.py`
- `TLS_DURABLE_MEMBERSHIP_AUTHORITY_AUDIT_rev0891.md`
- `TLS_SERVER_CONTEXT_RETENTION_AUDIT_rev0891.md`

Extended:

- `tools/audit_sync_tls_membership_snapshot.py`
- `tools/audit_sync_file_tls_server.py`
- `tools/verify_release_package.py`
- `CMakeLists.txt`

The lexical audits follow the new value/capability/context boundaries and
explicitly disclaim semantic proof. They no longer reward the retired raw
snapshot or raw `SSL_CTX*` API.

## Research

Primary-source research is summarized in the two rev0891 audits and in
`REVISION_EVIDENCE/rev0891/RESEARCH.md`. It includes current SQLite transaction,
WAL, PRAGMA, and TEMP-trigger documentation; OpenSSL context reference-count and
mutation rules; and TUF's separation of persisted trusted version from newly
fetched metadata.

## Validation

Exact final build, test, sanitizer, stress, audit, lineage, projection, and
package results are bound under:

- `REVISION_EVIDENCE/rev0891/validation/VALIDATION_SUMMARY.json`
- `REVISION_EVIDENCE/rev0891/AUDIT.md`
- `RELEASE_GATE.json`

The handoff archive is published only after the staged directory and immutable
ZIP independently pass the release verifier.

## Largest remaining gaps

The next membership milestone is an external monotonic/authenticated anchor
owner with explicit crash ordering, followed by signed update provenance,
enrollment/revocation/recovery/key-epoch semantics, freshness for already-issued
accept calls, and an incremental production reader differentially tested against
this full-history oracle.

The largest overall delivery gap is unchanged: the shipped `anonsync_core`
executable still does not make the newer causal SQLite/file/TLS path its sole
durable replica authority.

The largest remaining arbitrary callback is outbound payload acquisition.
`SyncReplicaFilePayloadSource` is fenced, but still runs unbounded caller code
while a durable outbox lease exists. A bounded content-addressed reader
capability should replace it.

The system also still needs a bounded accept pool, peer/folder fairness, total
disk accounting, staging expiry and garbage collection, dead-letter ownership,
causal-stability compaction, rejoin policy, and an explicit privacy/anonymity
threat model.

## Nonclaims

Rev0891 does not claim signed membership provenance, an external anchor store,
atomic database/anchor update, malicious-writer defense, live revocation,
freeze-attack protection, compaction, production-scale membership reads,
read-only serving, stable SQLite path/device identity, a production daemon,
bounded concurrent sessions, hostile same-process isolation, exactly-once
network delivery, anonymity, unlinkability, traffic-analysis resistance, formal
verification, or externally trusted build provenance.
