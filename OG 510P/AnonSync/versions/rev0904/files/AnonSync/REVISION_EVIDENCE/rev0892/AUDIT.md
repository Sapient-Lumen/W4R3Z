# AnonSync rev0892 implementation audit

## Mission boundary

AnonSync's heart remains exact authority accounting. Identity, policy, causality,
claim, retry, receipt, receiver admission, visible effect, recovery, migration,
and cleanup may advance only from exact evidence owned at an explicit cutpoint.
Derived projections, hashes, summaries, labels, and source audits are subordinate
evidence; none may silently mint authority.

Rev0892 advances that mission at two boundaries. Accepted TLS sessions now require
membership whose exact database cutpoint has also been covered by a separately
persisted anchor history. Outbound file delivery no longer executes a caller
payload callback while a durable outbox claim exists; it consumes a bounded,
immutable, folder-scoped payload snapshot and proves content availability inside
the same SQLite transaction that selects a claim.

## C++ implementation

### Separately persisted membership anchor

`SyncReplicaTlsMembershipAnchorSqliteOwner` owns a second named writable SQLite
database with one exact folder/local-actor identity, canonical genesis, a strict
singleton state row, and an append-only transition chain. Every read reconstructs
and validates the complete retained history. Every advance is an exact
compare-and-swap under `BEGIN IMMEDIATE` and is either a monotonic append, an
idempotent already-current retry, or a no-mutation stale result.

`SyncReplicaTlsMembershipAnchoredOwner` composes the membership and anchor owners
without claiming a cross-database transaction. It first proves the retained
anchor is a prefix of membership history, reconciles any prior
membership-committed/anchor-lagging crash gap, commits membership first, advances
the anchor second, re-reads both stores, and emits a move-only
`SyncReplicaTlsAnchoredMembershipAuthority` only when the exact target is still
current and covered. Failure after the first commit returns no unanchored
accepted-session authority; restart reconciliation is the explicit recovery
path.

The accepted TLS server consumes only the anchored type and binds terminal
results to both histories: membership generation, epoch, snapshot and chain
digests, plus anchor generation, digest, transition sequence, and transition
digest.

### Shared SQLite policy and live path-family binding

Membership and anchor stores now use one
`SyncReplicaTlsPolicySqliteConnectionBinding` and one reviewed backend profile.
The refactor removed duplicated policy code and reused the cube's existing
`SqlitePathFamilyGuard` instead of maintaining a weaker parallel path check.
Each owner retains the exact serialized connection generation, raw handle,
main filename, open main-file identity, and parent directory capability. Before
and after durable operations it rejects slot move/refill, raw-handle change,
filename change, symlink-family drift, inode replacement, and SQLite-reported
main-file movement where `SQLITE_FCNTL_HAS_MOVED` is supported.

Composition rejects identical path strings and filesystem aliases. Runtime
coverage includes hard-link aliases and live rename of an open membership
path. These are process-local connection and live-namespace observations. They
are not claims about separate media, independent administrators, a hostile VFS,
power-loss hardware, coordinated rollback while stopped, or post-reboot
provenance.

### Callback-free payload ownership

`SyncReplicaFilePayloadSnapshot` validates and owns one bounded set of payload
bytes. Construction binds one folder, exact lowercase SHA-256 identities,
per-payload and aggregate byte ceilings, sorted uniqueness, and immutable private
shared state. The delivery path no longer accepts `SyncReplicaFilePayloadSource`
or any outbound payload `std::function`.

`SyncReplicaFileContentInventory` is a smaller typed value used during claim
selection. It owns every digest string, binds one folder, rejects malformed,
duplicate, oversized, moved-from, and cross-folder inventories, and exposes a
stable span over private const state. A caller's input vector may be modified or
destroyed after construction without changing claim decisions.

### Availability-aware claim selection

The first callback-free draft still claimed a canonical operation before
learning that its payload was absent. Repeated release could churn attempt
metadata and starve later operations whose payloads were present. Rev0892 moves
availability selection inside the exact SQLite writer transaction.

For each canonical ready candidate, the owner now checks destination/lease/kind,
permanent wire policy, permanent payload-size policy, and then exact digest
presence in the immutable inventory. Missing content is skipped without an
attempt number, claim ID, lease, worker identity, retry provenance, or outbox
generation change. The first policy-compatible available candidate may be
claimed. Permanent policy failure remains fail-closed before claim and is not
misclassified as temporary absence.

After selection, size contradiction or bounded-copy failure exact-releases the
same claim. A scripted-clock regression proves that expiry after immutable lookup
but before dispatch-guard acquisition remains an expired attempt and requires a
fresh later claim.

## Defects found and corrected during the audit/refactor

1. **Anchor persistence was caller belief.** Rev0891 could compare a supplied
   anchor, but did not own its storage, update ordering, or restart recovery.
   Rev0892 adds the second durable owner and makes the crash gap explicit.
2. **Callback retirement initially preserved a liveness bug.** Claim-first,
   lookup-second could repeatedly lease an unavailable head-of-line item.
   Availability is now part of canonical claim selection and absent content
   consumes no attempt authority.
3. **The first inventory API borrowed caller views.** `string_view` storage could
   be mutated or invalidated across validation and selection. The inventory is
   now an immutable value with owned strings and one stable span per claim.
4. **Two pathnames could name one failure domain.** Exact string comparison did
   not reject hard links. Construction now checks filesystem equivalence, with
   executable alias coverage.
5. **The new connection binding duplicated weaker path logic.** It now retains
   the established `SqlitePathFamilyGuard` and re-attests the live path family
   before authority is returned.
6. **Lexical audits tracked retired shapes.** Nine selected audits were updated
   to follow the current anchored capability, immutable inventory, and CMake
   boundaries. They remain hygiene checks and explicitly disclaim semantic
   proof.

## Validation

- Exact parent archive: **26/26 package checks** and **5,875/5,875-file exact Git
  import match**.
- GCC 14.2 Debug complete all-target graph: complete across retained Ninja
  continuation slices; final dependency closure: `ninja: no work to do`.
- Registered CTest: **211/211** in one post-commit two-worker invocation,
  **29.33 seconds**.
- Audit/policy CTest: **83/83**, **20.69 seconds**.
- Focused owner/file/real-TLS matrix: **2,333/2,333** independently under GCC
  Debug, Clang 17 Release C++ `-Werror`, and GCC ASan/UBSan with leak detection
  and bundled SQLite instrumentation; **6,999/6,999** lane checks total.
- Repeated real-TLS membership/payload stress: **10/10 Debug runs,
  19,910/19,910 checks**, and **3/3 sanitizer runs, 5,973/5,973 checks**.
- Selected source audits: **260/260**. Release package-path and verifier policy
  matrices: **27/27**.
- Parent-relative source delta: **40 non-evidence paths** — 17 additions, 23
  modifications, 0 removals; **5,943 insertions, 1,023 deletions**.
- Active implementation projection: **436 files, 20,808,653 bytes**, SHA-256
  `f0e48f5bc513708c0d5fae68890367fb22defe47aeb0b204ca8b5538781c7e67`.

## Audit finding: build modularity remains partly cosmetic

The current top-level build still contains **87 literal libraries, 100 literal
executables, and 214 literal `add_test` declarations**. Narrow authority changes
continue to fan into a large graph because semantic centers remain giant:
`src/sync_domain.cpp` is about 15,167 lines,
`src/sync_domain_selftests.cpp` about 9,601,
`tests/sync_replica_tls_transport_test.cpp` about 5,987,
`src/sqlite_replay_ledger.cpp` about 4,529, and
`src/sync_replica_sqlite_owner.cpp` about 3,906.

The full build again spent its meaningful time in legacy monoliths after the new
focused authority graph was already complete. The correction should remain
incremental: split by durable owner and state-machine boundary, replace repeated
CMake wiring with reviewed declarative helpers, keep a fast affected-authority
gate, and retain periodic full-graph closure. Target count alone is not semantic
modularity.

## Largest remaining gaps

1. The shipped `anonsync_core` executable still does not make the newer causal
   SQLite/file/TLS path its sole durable replica authority.
2. The anchor is a second ordinary same-host SQLite database. Coordinated
   rollback of both stores, hostile same-process writers, stopped-process path
   replacement, and common storage failure remain outside the proof. A stronger
   root needs signed provenance and a separately administered, remote, or
   hardware-backed monotonic witness.
3. Enrollment, key rotation, revocation, recovery, freshness/freeze policy, and
   already-issued session treatment remain undefined.
4. The payload snapshot is an in-memory correctness seam, not a durable indexed
   content store. Retention leases, disk accounting, expiry, dead-letter state,
   garbage collection, and fair per-principal budgets are absent.
5. Full-history membership and anchor reconstruction remain O(history)
   correctness oracles, not production-scale serving implementations.
6. “Anon” is still not an implemented anonymity, unlinkability, endpoint-hiding,
   or traffic-analysis-resistance property.

## Nonclaims

Rev0892 does not claim atomicity across the membership and anchor databases,
independent physical failure domains, resistance to coordinated rollback,
hardware monotonicity, signed membership provenance, malicious same-process
writer defense, live revocation, durable payload availability, global memory or
disk fairness, payload garbage collection, complete retry/dead-letter/compaction
semantics, a production daemon, bounded concurrent sessions, exactly-once
network delivery, anonymity, formal verification, ThreadSanitizer coverage,
full-project Clang `-Werror`, full-project sanitizer coverage, or externally
trusted signed build provenance.
