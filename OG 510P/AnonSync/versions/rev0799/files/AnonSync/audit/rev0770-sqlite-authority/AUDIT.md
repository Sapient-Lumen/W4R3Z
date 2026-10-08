# rev0770 deep audit — SQLite connection authority and repository concentration

## Executive finding

The most severe issue was not a subtle SQLite edge case; it was a source/claim
divergence. Rev0769's narrative said the handle had a non-reusable incarnation
and exact authorizer generation. Its implementation stored a raw `sqlite3*`,
compared pointer equality, and installed an unowned callback. That made the
release notes stronger than the executable invariant.

Rev0770 corrects that defect with SQLite-owned connection client data, exact
generation fencing, a prepare-time callback challenge, and a mutex lease held
through commit or rollback. The source audit also makes direct production
`sqlite3_set_authorizer` calls illegal outside the new owner module.

## Baseline evidence

In the rev0769 parent:

- `PeerTransportIngressSchemaAttestation::authorizes()` returned only
  `db_ != nullptr && db_ == db`;
- the schema authorizer was installed with `nullptr` client data;
- no production source called `sqlite3_get_clientdata()` or
  `sqlite3_set_clientdata()`; and
- no executable authorizer-generation comparison existed.

The parent did detect schema-cookie changes and recompute the peer schema
manifest. Those are useful observations, but neither proves callback ownership
or connection lifetime.

## Corrected authority model

### Incarnation

A proof names the SQLite-owned client-data state by a random process salt and a
monotonic connection incarnation. Closing the connection destroys that state.
A new connection at the same allocator address has either no state or a
different incarnation.

### Generation

A deliberate reinstall on the same live connection advances the generation.
Every older attestation becomes stale even though the raw pointer remains
identical.

### Callback ownership

Comparison with client data alone would not detect an alien caller replacing
SQLite's single callback. Acquisition therefore sets a nonce in the state and
prepares a fixed statement. Only the owned bridge can echo it. Disabled or
replaced callbacks fail the challenge.

### TOCTOU closure

A successful challenge would be merely instantaneous if its lock were then
released. The returned lease retains the serialized connection mutex while the
caller verifies schema state, prepares and steps domain statements, and commits
or rolls back. A concurrent callback replacement blocks until lease release.

### Exception rollback ordering

The lease must outlive the transaction guard. All 12 lifecycle sites declare
the lease first and the transaction second. Reverse destruction therefore
rolls back before unlocking. The lexical release audit records this ordering
for every site.

## Adversarial results

The focused authority test exercises callback replacement and disablement,
stale same-handle generation, close/reopen, pre-prepared statement reprepare,
malformed return values, thrown exceptions, `NOMUTEX`, and cross-thread
replacement blocked through commit. The schema integration suite repeats the
ownership/generation checks through the real peer-ingress attestation. Full
CTest and sanitizer logs are retained separately rather than summarized away.

## Remaining authority gaps

### 1. The cohost claim is still too broad

The current checkpoint-host verifier checks one exact metadata-table DDL,
accepts two version strings, restricts namespace prefixes, rejects
virtual/shadow objects, and rejects foreign keys into peer-ingress tables. But
`schema_manifest_material()` still commits only the reserved peer-ingress
objects. The full expected checkpoint DDL is embedded in `sync_domain.cpp` and
is not shared with the cohost verifier.

Consequences:

- a new connection can admit altered `sync_session_*` DDL if the anchor/version
  and namespace rules still pass;
- restoring `PRAGMA schema_version` defeats the cookie optimization, while the
  peer-only manifest cannot identify which cohost DDL changed; and
- the term "reviewed cohost" currently overstates what is mechanically
  compared.

Correction: extract exact checkpoint schema objects and migrations into a
shared versioned module, then hash the complete bounded container manifest.

### 2. Connection recipe is adjacent evidence

Defensive mode, trusted-schema policy, trigger/view enablement, limits,
foreign-key enforcement, journal policy, registered functions/collations,
virtual-table modules, VFS assumptions, and extension policy can affect
semantics without changing peer DDL. A sealed connection factory should emit a
versioned recipe digest after configuring all of them. Receipt authority
should bind that digest, not a collection of nearby booleans.

### 3. Process-local proof is not durable authority

Client data and mutex ownership disappear at restart. They prevent stale local
capabilities; they do not authorize convergence after a crash. The durable
receipt still needs one domain-separated envelope binding payload digest,
canonical frame, exact claim generation, writer proof, schema/container digest,
and connection-recipe version in the same SQLite transaction.

### 4. Same-process hostility is out of scope

Code that can call arbitrary SQLite APIs can replace callbacks, overwrite
client data, or mutate the database through another connection. Rev0770 makes
replacement observable and serializes cooperative users. Stronger isolation
requires not exporting raw handles, a dedicated connection/file, or a process
boundary.

### 5. Lease acquisition starts after BEGIN

Lifecycle connections are freshly opened, private local objects, so no other
code receives the handle before verification. The lease begins immediately
after `BEGIN` and remains through transaction completion. If pooling or handle
sharing is introduced later, acquisition must move before the first transaction
statement and the final schema check must still run inside the snapshot.

## Repository concentration and waste

Measured source concentration is retained in `source-metrics.json`:

- `src/sync_domain.cpp`: 1,935,564 bytes / 24,523 lines;
- `src/sqlite_replay_ledger.cpp`: 294,021 bytes / 4,340 lines;
- `src/reporting_selftests.cpp`: 283,545 bytes / 4,498 lines;
- `src/sync_peer_ingress_lifecycle.cpp`: 228,840 bytes / 3,777 lines; and
- `include/anonsync_core.hpp`: 170,385 bytes / 3,499 lines.

The problem is not line count by itself. Checkpoint DDL, migrations, validation,
operator projections, test fixtures, and authority assumptions are embedded in
large translation units, so a small invariant change recompiles and retests
unrelated systems. It also encouraged rev0769's documentation to describe a
module boundary that did not actually exist.

Rev0770 extracts one invariant-owned C++ module, adds a focused executable, and
replaces the stale rev0758 README. The next high-value extraction is the
checkpoint schema manifest, not a mechanical split by line count.

## Source-audit refactor

The inherited lexical audit allowed any path containing vague words such as
"connection" or "authorizer" and mixed tests with production. The revised tool:

- allows production authorizer/client-data calls only in the exact owner file;
- inventories adversarial test calls separately;
- checks client-data, mutex, generation, and challenge machinery;
- verifies all lifecycle consumers retain the lease; and
- verifies declaration order makes exception rollback occur before unlock.

It remains lexical and is explicitly paired with runtime tests.

## Online research and design implications

Primary SQLite documentation confirms:

- one authorizer exists per connection and later calls replace or disable it;
- authorization runs during prepare/reprepare, so the correct callback must
  remain installed through step;
- client data is connection-owned and has close/replacement destruction since
  SQLite 3.44.0; and
- `sqlite3_db_mutex()` is present only for serialized connections, with
  `SQLITE_OPEN_FULLMUTEX` selecting that mode.

References are retained in `evidence/rev0770/research/REFERENCES.md`.

## Speculative direction

A stronger end state is a sealed `PeerIngressConnection` that owns:

1. the SQLite handle and path-family guard;
2. an immutable construction recipe;
3. the client-data incarnation and authorizer generation;
4. transaction/statement factories that require a live lease; and
5. a canonical container-manifest digest.

No raw `sqlite3*` would escape. The durable receipt would store only versioned,
domain-separated digests—not the process-local incarnation. An executable
fault scheduler should then cut at install, challenge, begin, prepare, step,
commit, callback replacement, close, and reopen boundaries and compare traces
against a small state-machine oracle.
