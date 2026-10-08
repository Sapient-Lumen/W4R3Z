# AnonSync revision notes — rev0892

## Revision theme

Rev0892 closes two authority gaps that remained after rev0891.

First, the durable membership database could validate a caller-supplied retained
anchor, but AnonSync did not own that anchor's persistence, commit ordering, or
restart recovery. Rev0892 adds an independently persisted append-only SQLite
anchor owner and a coordinator that never emits accepted-session membership
authority until the second store covers the exact committed membership
cutpoint. The protocol deliberately uses two transactions rather than pretending
they are atomic: membership commits first, anchor commit follows, and restart
reconciliation closes the explicit crash gap before authority can escape.

Second, outbound file delivery still invoked arbitrary caller code after a
durable claim had been minted. Rev0892 replaces that callback with a bounded
immutable payload snapshot. During review, the first callback-free draft exposed
a liveness defect: claiming before discovering content absence could repeatedly
lease and release an unavailable canonical head while later ready payloads
starved. The corrected owner takes a typed immutable content inventory and proves
availability inside the same SQLite claim transaction. Absent content consumes
no attempt authority.

The revision also extracts one shared SQLite policy profile for membership and
anchor stores, rejects different pathnames that alias the same database object,
pins each owner to the exact serialized connection generation and retained
SQLite path-family capability, and replaces a borrowed digest-view inventory
with an owned, folder-scoped, shared-const value.

## Parent

The exact parent handoff is:

`AnonSync-rev0891-2026.07.23.09.58-durablemembership-rollbackanchor-schemaclosure-contextretention.zip`

The parent archive digest, exact imported baseline, and parent-relative source
delta are recorded under `REVISION_EVIDENCE/rev0892/`.

## Production C++ changes

### Independently persisted membership anchor

Added:

- `src/sync_replica_tls_membership_anchor_sqlite_owner.hpp`
- `src/sync_replica_tls_membership_anchor_sqlite_owner.cpp`
- `src/sync_replica_tls_membership_anchored_owner.hpp`
- `src/sync_replica_tls_membership_anchored_owner.cpp`

`SyncReplicaTlsMembershipAnchorSqliteOwner` owns one named writable SQLite
database scoped to the exact folder and local actor. It initializes at the
canonical generation-zero membership anchor and records each successful
monotonic advance in an append-only, domain-separated transition-digest chain.
Every snapshot reconstructs and validates the complete retained transition
history, schema closure, metadata/history agreement, connection generation, and
durable backend profile.

The low-level transition is strict compare-and-swap under `BEGIN IMMEDIATE`:

- exact expected current plus a newer target appends and commits;
- an exact retry of the already-current target returns `AlreadyCurrent`;
- any other observed state returns `StaleExpected` without mutation; and
- generation regression, same-generation digest replacement, malformed digest,
  identity mismatch, or retention overflow fails closed.

`SyncReplicaTlsMembershipAnchoredOwner` composes the membership and anchor
owners. Publication order is executable:

1. reconstruct both stores and prove the durable anchor lies on the membership
   chain;
2. reconcile any earlier committed-membership/lagging-anchor gap;
3. perform exact membership compare-and-swap and commit the new generation;
4. retain the resulting move-only membership capability privately;
5. advance the anchor store to that exact cutpoint;
6. reconstruct both stores again; and
7. emit `SyncReplicaTlsAnchoredMembershipAuthority` only when membership and
   durable anchor are still exactly current at the target.

If a newer publisher wins before emission, current-authority acquisition retries
from a fresh reconstruction rather than knowingly returning a superseded
capability. If anchor persistence fails after membership commit, the call throws
and no unanchored capability escapes; restart reconciliation is the recovery
path.

### Same-file composition fence

Added to the shared SQLite profile:

- exact main-database filename retention;
- rejection of identical filename strings; and
- `std::filesystem::equivalent` rejection for aliases of the same filesystem
  object.

Runtime coverage includes hard-link aliases, not only lexical path aliases. Each
owner additionally retains the shared `SqlitePathFamilyGuard`: construction
binds the no-symlink parent/main/sidecar namespace and open main-file identity,
and every durable operation rechecks that capability plus
`SQLITE_FCNTL_HAS_MOVED` where supported. A live rename of an open membership
database therefore fails closed. These observations prevent ordinary accidental
composition and live namespace retargeting; they do not prove separate storage
media, power domains, controllers, administrators, credentials, backup policies,
rollback domains, hostile-VFS behavior, or post-reboot provenance.

### Anchored accepted-session authority

Extended:

- `src/sync_replica_file_tls_server.hpp`
- `src/sync_replica_file_tls_server.cpp`

The accepted TLS server now consumes only
`SyncReplicaTlsAnchoredMembershipAuthority`; raw durable membership authority is
not implicitly convertible. Every terminal result binds the membership state
generation, policy epoch, snapshot digest, previous/current chain digests, plus
the durable anchor generation/digest, transition sequence, and transition
digest that authorized the session.

The anchor proves only that this process observed the second durable store cover
the membership cutpoint before capability emission. It does not retroactively
revoke already-issued session authority.

### Shared TLS-policy SQLite profile

Added:

- `src/sync_replica_tls_policy_sqlite_profile.hpp`
- `src/sync_replica_tls_policy_sqlite_profile.cpp`

Refactored:

- `src/sync_replica_tls_membership_sqlite_owner.hpp`
- `src/sync_replica_tls_membership_sqlite_owner.cpp`

Rev0891 had duplicated connection configuration and backend re-attestation logic
inside the membership owner. Both policy databases now use one retained
connection-generation binding, one retained `SqlitePathFamilyGuard`, and one
reviewed profile. The binding holds an exact serialized-generation borrow for the
owner lifetime and rejects slot move/refill, raw-handle replacement, filename
change, symlink-family drift, inode replacement, or SQLite-reported main-file
movement before authority is read or returned. The profile requires defensive
mode, untrusted schema, disabled extension/attachment/trigger hazards, active
CHECK constraints, exact named writable `main`, and WAL with at least `FULL` or
rollback journal with at least `EXTRA`. These are necessary process-local SQLite
and live-namespace observations, not proof of a hostile VFS or hardware
persistence stack.

### Callback-free bounded payload ownership

Added:

- `src/sync_replica_file_payload_snapshot.hpp`
- `src/sync_replica_file_payload_snapshot.cpp`
- `src/sync_replica_file_content_inventory.hpp`
- `src/sync_replica_file_content_inventory.cpp`

Removed from production delivery APIs:

- `SyncReplicaFilePayloadSource`; and
- every outbound file-payload `std::function` call.

`SyncReplicaFilePayloadSnapshot` validates one folder identity, entry count,
per-payload bytes, aggregate retained bytes, and exact payload SHA-256 identities
before becoming active. It sorts by digest, rejects duplicate content authority,
retains bytes behind inaccessible `shared_ptr<const State>`, and returns selected
bytes by owned copy rather than a dangling view.

`SyncReplicaFileContentInventory` is a separate bounded value containing no
payload bytes. Construction owns all digest strings, validates lowercase full
SHA-256, sorts, rejects duplicates, applies a 65,536-entry hard ceiling, and
binds one folder. Cheap copies share private const state. The SQLite owner no
longer borrows `string_view` spans whose lifetime or contents could change while
claim selection is in progress, and it no longer repeats O(n) validation on
every retry.

### Availability-aware exact claim selection

Extended:

- `src/sync_replica_sqlite_owner.hpp`
- `src/sync_replica_sqlite_owner.cpp`
- `src/sync_replica_file_delivery_service.hpp`
- `src/sync_replica_file_delivery_service.cpp`

Before entropy or a writer transaction, the owner validates that an engaged
inventory is active, File-scoped, and bound to the exact folder. Inside the same
`BEGIN IMMEDIATE` transaction that reconstructs current outbox authority, each
canonical ready candidate is checked in this order:

1. destination, lease, and operation-kind scope;
2. permanent wire-policy validation;
3. permanent payload-size policy; and
4. exact content presence in the immutable inventory.

The first policy-compatible available operation may be claimed. A missing digest
is skipped without an attempt number, claim ID, lease deadline, worker identity,
retry provenance, or outbox-generation change. Permanent wire/payload policy
still blocks before claim rather than being mislabeled as transient content
absence.

The service then resolves the selected operation from the same immutable
snapshot. Size contradiction or bounded-copy failure exact-releases the exact
claim before the exception propagates. A scripted-clock test proves that expiry
after lookup but before dispatch-guard acquisition remains an expired exact
attempt and requires a fresh later claim.

## Runtime coverage

Added:

- `tests/sync_replica_tls_membership_anchor_sqlite_owner_test.hpp`
- `tests/sync_replica_tls_membership_anchor_sqlite_owner_test.cpp`

Extended:

- `tests/sync_replica_tls_transport_test.cpp`
- `tests/sync_replica_sqlite_owner_test.cpp`
- `tests/sync_replica_file_delivery_service_test.cpp`

The compiled matrix covers:

- exact anchor genesis, append, idempotent retry, stale expected state, and
  retention ceilings;
- restart reconstruction, committed-membership/lagging-anchor recovery, and
  concurrent reconciliation;
- whole-file membership rollback, divergent membership replacement, anchor
  rollback, transition-chain tamper, schema tamper, and identity mismatch;
- identical database names, lexical aliases, and hard-link aliases;
- owner handle-slot move/refill and live main-database path displacement;
- concurrent policy supersession before capability emission;
- accepted mutual-TLS attribution to the exact durable anchor cutpoint;
- immutable payload canonicalization, malformed/duplicate/oversized input,
  moved-from misuse, folder mismatch, and copied-state lifetime;
- mutation of caller digest storage after inventory construction;
- no-attempt skipping of an unavailable canonical head;
- exact claim of a later available payload;
- permanent wire/payload policy before claim;
- post-selection contradiction release; and
- claim expiry after successful immutable lookup.

## Audit and refactor work

Added:

- `tools/audit_sync_tls_membership_anchor.py`
- `tools/audit_sync_file_payload_snapshot.py`
- `TLS_DURABLE_MEMBERSHIP_ANCHOR_AUDIT_rev0892.md`
- `FILE_PAYLOAD_SNAPSHOT_AUTHORITY_AUDIT_rev0892.md`

Extended:

- `tools/audit_sync_tls_membership_sqlite_owner.py`
- `tools/audit_sync_tls_membership_snapshot.py`
- `tools/audit_sync_file_tls_server.py`
- `tools/audit_sync_replica_file_delivery.py`
- `tools/audit_sync_outbox_dispatch_guard.py`
- `tools/audit_sync_file_effect_path_capability.py`
- `tools/audit_authority_callback_boundaries.py`
- `tools/verify_release_package.py`
- `CMakeLists.txt`

Several older lexical audits still encoded retired source shapes. They now track
the anchored capability, immutable snapshot, typed inventory, and current CMake
authority boundaries. These checks remain source-shape hygiene; they do not prove
C++ lifetime, transaction, cryptographic, or progress semantics.

## Research

Primary sources reviewed for this revision are summarized in the two rev0892
audits and `REVISION_EVIDENCE/rev0892/RESEARCH.md`. They include:

- C++ Core Guidelines CP.22 on unknown code while holding locks;
- RFC 6920 on hash-based content naming;
- NIST FIPS 180-4 for SHA-256;
- SQLite transaction, isolation, WAL, synchronous, and atomic-commit behavior;
- The Update Framework's retained-version rollback model; and
- the TPM 2.0 library specification as a stronger future monotonic-root option.

## Validation

Exact final compiler, sanitizer, stress, audit, lineage, projection, and package
results are bound under:

- `REVISION_EVIDENCE/rev0892/validation/VALIDATION_SUMMARY.json`
- `REVISION_EVIDENCE/rev0892/AUDIT.md`
- `RELEASE_GATE.json`

The handoff archive is published only after both the staged directory and the
immutable ZIP independently pass the release-package verifier.

## Largest remaining gaps

The strongest next membership step is authenticated update provenance and a
rollback root outside ordinary same-host SQLite: a hardware monotonic counter,
remote witness, signed transparency checkpoint, or separately administered
append-only service. Enrollment, key rotation, revocation, recovery, freshness,
and treatment of already-issued session capabilities remain product-level
policy work.

The immutable payload snapshot is a safe callback-free seam, not the final
payload store. A durable indexed content store should expose value-owned read
snapshots, exact lifecycle/garbage-collection authority, process/folder/peer
budgets, and differential tests against this in-memory oracle. Missing payloads
are skipped, not diagnosed, expired, dead-lettered, or reclaimed.

The largest delivery gap remains unchanged: the shipped `anonsync_core`
executable still does not make the newer causal SQLite/file/TLS path its sole
durable replica authority. The project also needs bounded concurrent sessions,
fair admission, total disk accounting, compaction/rejoin, and an explicit
anonymity/metadata threat model.

## Nonclaims

Rev0892 does not claim atomicity across the membership and anchor databases,
independent physical failure domains, resistance to coordinated rollback of both
stores, a hardware monotonic counter, signed membership provenance, malicious
same-process writer defense, live revocation of already-issued authority,
durable payload availability, global memory fairness, payload garbage
collection, a production daemon, bounded concurrent sessions, exactly-once
network delivery, anonymity, unlinkability, traffic-analysis resistance, formal
verification, or externally trusted build provenance.
