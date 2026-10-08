# Durable TLS Membership Anchor Audit — rev0892

## Mission boundary

The accepted TLS server must not authorize a peer from a membership database merely because that database is internally self-consistent. A complete older copy can also be internally self-consistent. rev0892 therefore separates three authorities:

1. `SyncReplicaTlsMembershipSqliteOwner` owns the append-only canonical membership history.
2. `SyncReplicaTlsMembershipAnchorSqliteOwner` owns an independently persisted monotonic checkpoint chain.
3. `SyncReplicaTlsMembershipAnchoredOwner` is the only component that can turn the raw history capability into `SyncReplicaTlsAnchoredMembershipAuthority`, the type accepted by the server.

The heart of the revision is a negative rule: **a raw membership capability cannot cross the accepted-session API, even when the raw history transaction committed successfully.** The server requires a different move-only type proving that the anchor store covered the exact membership cutpoint before capability emission.

## Why a second store is necessary

The membership history's domain-separated SHA-256 chain detects corruption, reordering, and divergence only relative to a retained trusted cutpoint. If an attacker, operator mistake, backup restore, or storage fault replaces the entire database with an older valid copy, internal verification alone has no newer fact to compare against.

The Update Framework makes the analogous rollback-protection obligation explicit: clients persist trusted version information and reject metadata older than that retained state. This does not make AnonSync a TUF implementation; it is the relevant architectural lesson that rollback resistance requires state outside the object being checked.

Primary source: https://theupdateframework.github.io/specification/latest/

SQLite documents WAL commit and checkpoint behavior and the effect of `synchronous` settings. rev0892 requires WAL with at least `FULL`, or a rollback journal with at least `EXTRA`, for both policy databases. Those settings are necessary SQLite policy observations, not proof that a VFS, filesystem, controller, volatile write cache, hypervisor, or physical medium honors persistence requests.

Primary sources:

- https://sqlite.org/wal.html
- https://sqlite.org/pragma.html#pragma_synchronous
- https://sqlite.org/atomiccommit.html

A TPM NV counter or equivalent hardware-backed monotonic state could provide a stronger rollback root. The current owner is deliberately an ordinary SQLite implementation and makes no TPM, secure-element, signature, remote-witness, or hardware monotonicity claim.

Primary source: https://trustedcomputinggroup.org/resource/tpm-library-specification/

## Exact crash ordering

The two SQLite transactions are not atomic together. rev0892 makes the unavoidable ordering explicit:

1. Reconstruct and validate the external anchor store.
2. Supply that exact anchor to the membership owner and validate the complete membership chain through it.
3. Reconcile any previously committed membership generation that is ahead of the anchor.
4. Compare the caller's expected membership anchor with the exact reconstructed current cutpoint.
5. Commit the next complete membership generation under `BEGIN IMMEDIATE`.
6. Keep the resulting raw move-only membership authority private.
7. Reconstruct both stores again and advance the independent anchor by exact compare-and-swap to the committed membership cutpoint.
8. Reconstruct both stores once more and require the membership head, retained durable anchor, and capability cutpoint to be exactly equal. “Covered by newer” is sufficient for reconciliation but never for capability emission; a known-superseded candidate triggers a bounded retry.
9. Only that anchored capability can enter the accepted-session server.

A failure after step 5 and before step 7 leaves membership ahead of the anchor. That is a recoverable crash gap, not a rolled-back membership transaction and not successful authority emission. `current_authority_or_throw()` or `reconcile_or_throw()` closes the gap on restart before returning authority.

## Crash and concurrency matrix

| Observation | Membership DB | Anchor DB | Authority outcome |
|---|---:|---:|---|
| Failure before membership commit | old | old | no authority; ordinary retry |
| Membership commit succeeds, anchor writer is blocked/fails | new | old | no authority escapes; restart reconciliation required |
| Anchor commit succeeds, caller loses response | new | new | exact retry observes `AlreadyCurrent`; no duplicate transition |
| Two reconcilers race from old to the same target | new | one winner/new | both re-read and converge; stale CAS never fabricates coverage |
| Membership contains several valid generations beyond anchor | newest | old | coordinator may jump directly to newest after proving both endpoints on the complete chain |
| Membership file rolled back below anchor generation | older | newer | fail closed before capability emission |
| Membership chain forks through retained generation | divergent | retained | fail closed before capability emission |
| Both databases are rolled back/replaced together | older pair | older pair | **not detected by this design** |

The runtime matrix deterministically creates the post-membership/pre-anchor gap by holding an independent `BEGIN IMMEDIATE` writer lock on the anchor database. WAL readers remain available, so coordinator preflight and the membership commit complete, while the anchor advance fails with `SQLITE_BUSY`. After the lock is released, the same coordinator reconciles and emits the exact committed authority.

## Independent-file preflight

Both low-level owners retain SQLite's main-database filename. Coordinator construction rejects:

- the exact same filename; and
- two filenames that `std::filesystem::equivalent` reports as the same filesystem object. The runtime matrix includes a hard-link alias with a distinct pathname, not only identical strings or lexical normalization.

Failure to prove distinct files is fail-closed. This catches accidental same-file composition and ordinary aliasing. It does **not** prove separate disks, controllers, power domains, VMs, cloud volumes, backup policies, administrators, credentials, or failure modes. Two distinct files in one directory can still be lost or rolled back together.

## Anchor store state machine

The anchor database has two exact `STRICT` tables:

- one singleton identity/current-state row; and
- one append-only transition table.

The store begins at the canonical generation-zero membership anchor. Each transition binds:

- folder and local actor identity;
- schema version;
- transition sequence;
- exact previous membership generation and digest;
- exact current membership generation and digest; and
- previous transition digest.

Every read and write re-attests the mutable SQLite connection profile, backend profile, exact schema closure, complete transition sequence, previous-link continuity, transition digests, and metadata/history agreement. Transition count is hard-capped. The low-level advance is strict compare-and-swap, permits generation jumps for crash recovery, returns `AlreadyCurrent` for exact ambiguous retry, and returns `StaleExpected` without mutation when another writer won.

The anchor digest is structural evidence, not authenticated provenance. A malicious writer with authority over the store can poison it and deny service. The coordinator prevents a poisoned or unrelated anchor from authorizing a session by proving every retained anchor against the complete membership chain.

## Type-level bypass closure

Before this review, adding an anchor coordinator alone would have been insufficient: the server still accepted `SyncReplicaTlsMembershipAuthority`, which the raw history owner could mint directly. That made anchoring a caller convention.

rev0892 introduces `SyncReplicaTlsAnchoredMembershipAuthority`:

- move-only;
- not publicly constructible;
- constructed only by `SyncReplicaTlsMembershipAnchoredOwner`;
- contains the exact raw membership capability plus the durable anchor generation, chain digest, transition sequence, and transition digest; and
- is the only membership type accepted by `serve_one_sync_replica_file_delivery_tls_session_or_throw`.

Every terminal server result binds both membership evidence and retained anchor-store evidence before accept authority is spent. This does not create live revocation: a capability already issued for an older anchored generation remains valid for that one in-progress server call.

## Shared SQLite profile refactor

rev0891 duplicated durable-backend and connection-policy code inside the membership owner. rev0892 extracts that logic into `sync_replica_tls_policy_sqlite_profile.*` and reuses it for both databases. The refactor preserves:

- defensive mode;
- untrusted schema;
- disabled triggers, views, extension loading, DQS, attach-create, and attach-write where supported;
- zero attached-database and trigger-depth limits where supported;
- `query_only=OFF`, `read_uncommitted=OFF`, and CHECK enforcement;
- no attached authority databases;
- a named writable main database; and
- WAL+FULL or rollback-journal+EXTRA.

This removes a drift-prone duplicate policy surface. The review also found that both owners retained only a reference to a refillable handle slot while claiming to be stationary. `SyncReplicaTlsPolicySqliteConnectionBinding` now retains an exact serialized connection-generation borrow for the owner lifetime and re-attests raw handle identity, slot generation, and main filename before and after durable operations. A moved or refilled slot therefore fails closed instead of redirecting policy authority.

A second review found that this new binding duplicated a weaker subset of the cube's existing `SqlitePathFamilyGuard`. The binding now retains that shared guard as well. Construction proves a no-symlink parent/main/sidecar family, binds the open main-file inode and retained parent directory, and consults `SQLITE_FCNTL_HAS_MOVED` where supported. Every policy operation rechecks the live namespace before authority is returned. The runtime matrix moves each live owner’s slot and separately renames an open membership database path; both cases fail closed. These are process-local connection and live-namespace observations, not storage-media provenance. Lexical audits were updated to inspect the shared semantic owner rather than requiring retired local function names.

## Interaction with payload callback retirement

The sibling rev0892 work removes an arbitrary payload callback from live outbox-claim authority and replaces it with an immutable bounded snapshot. The two changes close different bypasses:

- payload snapshot ownership prevents unknown caller code from running between durable claim mutation and request construction; and
- anchored membership ownership prevents an internally valid but unanchored policy database from authorizing an accepted session.

Both use the same mission rule: derived or caller-retained state must not impersonate exact durable authority.

## Remaining risks and next work

1. **Joint rollback remains possible.** Distinct files are not independent trust domains. The next stronger root is a hardware-backed monotonic counter, remote witness, signed transparency checkpoint, or separately administered append-only service.
2. **Membership updates are unsigned.** The owner validates structure and exact local sequencing, not who was authorized to change policy. Enrollment, key rotation, revocation, recovery, and administrative signatures remain missing.
3. **No live revocation.** An already issued anchored capability is a fixed cutpoint for one accepted-session invocation.
4. **Full-history cost remains O(history).** Both owners are correctness oracles. An indexed production implementation should be differentially tested against them rather than weakening their reconstruction semantics.
5. **Cross-database commit is not atomic.** Recovery is intentional and tested; any future refactor that claims atomicity across the two SQLite files would be false.
6. **Filesystem identity is observational.** The retained path guard detects ordinary live parent/main rebinding, symlink drift, inode replacement, and SQLite-reported movement while the process and guard survive. It cannot attest a hostile VFS, storage below the filesystem, coordinated replacement while the process is stopped, or the provenance of a later reboot/open.
7. **No cryptographic anchor authentication.** SHA-256 transition chains detect accidental alteration relative to a retained root; they are not signatures or MACs.
8. **Lexical audit nonclaim.** Source tokens and ordering do not prove C++ object semantics, SQLite durability, filesystem behavior, cryptographic security, race freedom, or crash recovery. Compiled adversarial tests, independent compilers, sanitizers, stress, and sealed package verification remain load-bearing.
