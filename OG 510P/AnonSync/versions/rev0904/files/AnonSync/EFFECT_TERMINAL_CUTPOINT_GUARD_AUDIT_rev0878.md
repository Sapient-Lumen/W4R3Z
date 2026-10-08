# AnonSync rev0878 — effect-terminal cutpoint guard, live authority composition, and cube audit

## Executive finding

AnonSync's heart is **authority accounting under crash, concurrency, partial
trust, duplication, reordering, resource pressure, and ambiguous response**. It
is not fundamentally a file copier. The project is trying to make every identity,
causal edge, projection decision, dispatch attempt, retained payload, receiver
admission, visible effect, retry, and sender settlement attributable to exact
bounded evidence and an explicit durable transition.

Rev0877 corrected an authentication seam: public channel-description bytes no
longer authorized durable delivery. Rev0878 reaches the next mission boundary by
composing that live capability with exact payload staging and a visible immutable
file effect. During that composition, a severe stale-projection race was found:
causal projection was checked in one SQLite snapshot, the snapshot ended, and the
filesystem effect occurred later. A second writer could supersede the operation
in that gap.

The primary rev0878 correction is a scope-bound causal cutpoint guard that
retains exact `BEGIN IMMEDIATE` authority from the transaction-bound evidence
receipt through filesystem materialization and terminal receipt construction.
It does not claim that SQLite and the filesystem are one transaction. It makes
the authorizing causal cutpoint stable while an independently crash-reconciled
idempotent effect is performed.

The resulting focused path is:

`live authenticated channel capability → File-only wire/payload preflight →`
`durable claim → exact payload frame → bounded receiver stage → causal admission`
`and exact receipt cutpoint → writer-serializing active-primary guard → immutable`
`create-new publication → file and directory durability → effect database`
`cutpoint → terminal receipt → exact sender settlement`

Only `Published` and `AlreadyPublished` are effect-terminal. Every other outcome
preserves sender intent.

## Mission invariant

> Given the same authorized canonical evidence and trust state, independent
> replicas must derive the same state; no untrusted bytes, fabricated channel
> description, missing dependency, stale projection, stale receipt, clock
> movement, duplicate, crash frontier, schema mutation, namespace race, resource
> decision, retry response, or summary may silently manufacture authority.

This implies:

- canonical operation bytes own operation identity;
- exact payload bytes must match the operation's size and digest;
- live channel authority is distinct from descriptive channel evidence;
- payload retention, causal admission, active projection, visible publication,
  effect-database marking, receipt construction, and sender settlement are
  separate transitions;
- a terminal receipt must bind the exact request attempt and both receiver
  cutpoints;
- byte equality alone does not prove a private immutable filesystem effect;
- a syscall result does not resolve a crash ambiguity by itself;
- summaries and cached projections do not replace exact history; and
- independent durable systems require reconciliation, not fictional atomicity.

## Lineage and integration choice

The primary parent is the user-supplied rev0877 live-channel archive. A separate
cloudtainer archive, based on rev0876, implemented an independently validated
file-effect branch. Rather than discard either line, rev0878 merged the effect
branch into rev0877 and adapted every public file-service entry point to the
opaque channel capability.

This exposed integration bugs that neither branch alone could reveal:

1. a file operation could be wire-compatible but larger than the payload limit,
   acquiring a lease that request encoding could never use;
2. the file orchestrator needed private access to channel liveness without
   publishing a forgeable validation API; and
3. loose causal projection checking allowed a second writer to invalidate the
   visible-effect decision.

The merge therefore produced more than feature aggregation; it exercised the
exact authority seams the project is meant to protect.

## Live channel authority through the effect boundary

`SyncReplicaFileDeliveryService` requires
`SyncReplicaDeliveryChannelAuthority` for:

- outbound claim and request construction;
- inbound staging, admission, publication, and receipt construction; and
- sender receipt validation and settlement.

The capability remains non-default-constructible, noncopyable, move-only,
process-bound, thread-lifetime-bound, and privately minted. The file service is
an explicit friend so it can invoke the private liveness verifier before any
context read or durable operation. Ordinary callers still cannot mint or bless
an authority.

The receiver passes the same capability into the nested evidence service. It
does not downgrade to `SyncReplicaDeliveryChannelContext`. The sender
revalidates after the payload callback because arbitrary caller code could clear
or otherwise invalidate a transport-backed OpenSSL session before the service
returns bytes that claim its exporter binding.

Production CMake linkage excludes the deterministic test mint. The test target
alone links `anonsync_sync_replica_delivery_test_channel`. This is build-graph
hygiene and same-process domain separation, not a cryptographic sandbox against
hostile code already executing in the process.

## Preclaim payload compatibility

The inherited delivery preflight checked the canonical operation against the
wire model but did not compare a File operation's committed size to the outer
payload limit. The resulting cycle was wasteful and persistent:

1. claim the first ready File;
2. increment attempt and mint claim identity;
3. fetch payload;
4. reject the request as too large;
5. wait for lease expiry; and
6. claim the same impossible operation again.

The owner claim core now accepts:

- optional destination identity;
- optional exact operation kind;
- optional complete delivery operation limits; and
- optional positive maximum File payload bytes.

After `BEGIN IMMEDIATE`, full restore, owned clock observation, and exact intent
lookup, the owner validates the selected canonical operation and compares
`size_bytes` before calling the lease transition. Failure rolls back without a
new attempt, claim, worker, deadline, or cutpoint.

The ordering is deliberately fail-closed. The first ready matching operation
that violates permanent local policy blocks later matching work. Skipping it
would invent undeclared ordering and starvation semantics. Production needs a
typed permanent-rejection/dead-letter transition with policy generation and
operator-visible reason.

A remaining liveness gap is local payload availability. The callback occurs
after claim. A throw, missing object, short payload, or digest mismatch leaves a
valid lease. A future payload store should support exact reservation/peek plus an
atomic claim of that operation, or publish a typed local-unavailable outcome.

## The stale-projection race

### Original sequence

The first file-effect composition performed:

1. receive and stage exact payload;
2. atomically admit causal evidence and obtain a receipt;
3. call `snapshot_or_throw()` and inspect active projection;
4. release the causal transaction;
5. publish the filesystem effect;
6. mark the effect database; and
7. construct a terminal receipt.

Between steps 4 and 5, an independent causal owner could accept a child or
conflicting operation that changed the path's primary. The filesystem write and
terminal receipt would still use the earlier decision.

That was not merely a theoretical TOCTOU concern. The causal owner is explicitly
usable from multiple SQLite connections, and its projection is derived from
mutable exact history. Releasing transaction authority before the external
effect meant a summary observation was being treated as a durable authorization.

### Guard semantics

`SyncReplicaSqliteProjectionGuard` owns:

- a `std::unique_ptr<SyncSqliteTransaction>` begun in Immediate mode;
- the exact fully restored `SyncReplicaSqliteSnapshot`; and
- a diagnostic label.

It is noncopyable and nonmovable. Destruction rolls back an unchanged live
writer-serializing transaction. Explicit `commit_or_throw()` commits and clears
its transaction capability.

The owner mints a guard only when:

- expected generation is nonzero;
- expected cutpoint is a lowercase SHA-256 digest;
- current generation and complete cutpoint exactly equal the evidence receipt;
- canonical operation validation succeeds under persisted limits;
- exact retained operation bytes equal the request operation;
- operation kind is File;
- evidence state is Active;
- the visible path exists;
- the operation is its primary File;
- visible operation count is exactly one; and
- preserved file alternates are empty.

Any cutpoint or projection mismatch commits an unchanged transaction and returns
null. The service maps that to `ProjectionBlocked`. It does not silently adopt a
newer cutpoint, because the existing evidence receipt does not own the newer
state.

### Guard coverage

The receiver retains the guard across:

- immutable namespace reconciliation/publication;
- file and directory synchronization;
- effect database publication marking and re-attestation;
- effect snapshot acquisition;
- outer receipt validation and encoding; and
- outer receipt digest construction.

The guard commits only after those exact receipt bytes exist. If an exception
occurs first, the causal transaction rolls back and no receipt is returned. A
filesystem effect that already completed is not undone; the next duplicate
request reconciles the immutable file and completes or verifies the effect row.

### Runtime proof

The causal-owner test opens two independent SQLite connections to one database.
It:

1. admits a File and obtains the exact active cutpoint;
2. acquires the projection guard on owner A;
3. configures owner B with zero busy timeout;
4. attempts to admit a causal child through owner B;
5. observes SQLite “database is locked” while the guard is live;
6. proves the guarded generation/digest remain exact;
7. commits the guard;
8. admits the child successfully through owner B;
9. proves the child becomes primary; and
10. proves the old generation/digest returns no guard and changes no durable
    state.

SQLite's primary documentation supports the serialization premise: only one
write transaction can be active, and `BEGIN IMMEDIATE` begins that write
transaction immediately or fails busy when another writer exists.

- https://sqlite.org/lang_transaction.html
- https://sqlite.org/isolation.html

This is executable evidence for the current SQLite configuration, not a formal
proof of arbitrary storage systems.

## Cross-store atomicity and crash frontiers

There are three independent durable domains:

1. causal SQLite;
2. effect SQLite; and
3. filesystem namespace/data.

No API can atomically commit all three. Rev0878 uses monotone state and exact
reconciliation instead.

Important frontiers include:

- payload stage commits, causal admission fails;
- causal admission commits, projection guard cannot be acquired;
- file inode and directory entry become durable, effect mark has not committed;
- effect mark commits, post-mark namespace proof fails;
- receipt bytes are constructed, causal guard commit fails;
- causal guard commits, response is lost;
- receiver returns terminal receipt, sender crashes before settlement; and
- sender settles, an old receipt is replayed.

The design response is:

- staged-but-nonactive state is retained and nonterminal;
- changed causal cutpoints are retried through duplicate admission;
- immutable exact files are recognized after restart;
- contradictory namespace state after `Published` fails closed;
- no terminal receipt is returned before exact effect and receipt construction;
- a lost response produces a fresh claim after exact lease expiry;
- receiver duplicate handling returns exact current effect evidence; and
- sender settlement is fenced by destination, operation, and current claim ID.

## Immutable filesystem effect

The first effect is intentionally create-new only. It never replaces an existing
entry. This makes reconciliation finite and explicit:

- `Absent`: publication may be attempted;
- `ExactAndDirectorySynced`: publication already owns the exact private effect;
- `ConflictingEntry`: preserve the existing namespace and return nonterminal
  conflict.

Exact reconciliation on POSIX requires:

- component-by-component parent traversal without symlink following;
- regular final file type;
- stable descriptor identity before and after read/sync;
- exact payload bytes;
- effective-UID ownership;
- exact 0600 mode;
- link count one;
- file synchronization;
- containing-directory synchronization; and
- post-directory-sync identity revalidation.

The publisher normalizes the exact writer-owned inode with `fchmod(0600)` rather
than assuming requested creation mode survives `umask`. Hard links, symlinks,
mode widening, ownership mismatch, unstable bytes, and path conflicts do not
become `AlreadyPublished`.

Linux documents that file `fsync()` does not necessarily persist the directory
entry and that the directory itself must be synchronized:

- https://man7.org/linux/man-pages/man2/fsync.2.html

Windows remains fail-closed for the unproved directory-durability boundary.

## Stable root identity: severe remaining gap

The effect owner persists an absolute lexically normalized root-path string. Each
atomic publication securely resolves and pins its destination parent for that
call, but the owner does not retain one root directory identity across calls or
restart.

A privileged local actor can rename, replace, bind-mount, or otherwise rebind the
configured path between operations. A later publication may then be internally
safe under a different directory object while the persisted root text and effect
identity appear unchanged.

The correction should include:

1. an administrator-authorized root enrollment transition;
2. a retained process-lifetime root directory descriptor/capability;
3. persisted platform root identity and policy epoch;
4. restart comparison against the enrolled identity;
5. explicit root-rebind intent and audit evidence; and
6. all descendant resolution relative to the retained capability.

On Linux, `openat2()` can constrain resolution with `RESOLVE_BENEATH`,
`RESOLVE_IN_ROOT`, `RESOLVE_NO_MAGICLINKS`, and `RESOLVE_NO_SYMLINKS`. It does not
by itself define enrollment, restart identity, mount policy, or portable
semantics.

- https://man7.org/linux/man-pages/man2/openat2.2.html

## Protocol and terminality

The outer request contains the complete canonical evidence request plus exact
payload bytes. Validation requires File kind, exact size, exact SHA-256 content
digest, actor/channel identity, bounded frame geometry, and the inherited
canonical operation limits.

The receipt binds:

- folder;
- sender and receiver actor epochs;
- operation, claim, and attempt;
- exact outer request digest;
- channel binding;
- explicit disposition;
- inner evidence receipt where admission occurred;
- structural effect ID;
- receiver effect generation; and
- receiver effect cutpoint digest.

`Published` and `AlreadyPublished` require an evidence-terminal inner receipt in
Active state and the expected effect ID. They alone settle sender intent.

The effect cutpoint and frame digest are unkeyed structural seals. The receipt is
authenticated while processed through the exact live channel capability; it is
not independently verifiable after the session. A durable archival design should
sign an append-only receiver effect log using a device key epoch and bind
revocation/recovery semantics.

RFC 9266 defines TLS exporter channel bindings and their security properties. A
channel binding proves linkage to that TLS session; it is not a substitute for
an offline receiver signature.

- https://www.rfc-editor.org/rfc/rfc9266.html

## Lock order and scalability

The receive path's overlapping order is:

`causal SQLite guard → effect SQLite materialization → filesystem`

The earlier staging transaction is complete before causal admission, and current
effect-owner code does not call back into the causal owner. Future code must not
introduce an effect-to-causal nested path without redesigning the order.

The guard holds the causal writer slot while the effect owner performs O(history)
restore and while the filesystem may block on I/O and fsync. This is safe but
expensive. It can amplify contention and causes unrelated causal changes to make
an exact full cutpoint stale.

A production evolution could use a narrower projection authorization object:

- exact path;
- exact primary operation ID;
- projection generation/digest;
- membership/policy epoch;
- bounded expiry or one-shot nonce; and
- durable revocation/supersession rules.

That design must not merely cache a summary. It should be derived and published
under the full oracle, then differentially tested so every accepted terminal
effect corresponds to an oracle-authorized state.

## Effect owner and staging availability

`SyncReplicaFileEffectSqliteOwner` stores exact canonical operation bytes and
payload bytes in a separate strict schema. On every public operation it reads
exact schema text, decodes every retained operation, recomputes payload hashes,
effect IDs, generations, counters, set digest, and complete cutpoint.

This is intentionally O(history). Its purpose is correctness, migration, repair,
fuzzing, and differential comparison. A production object store should avoid
copying every payload through a complete SQLite BLOB restore on each operation.

Staging before causal admission is correct for effect availability but creates a
storage-denial surface. Authenticated work that is dependency-pending,
quarantined, or perpetually projection-blocked remains staged. Aggregate byte and
count ceilings prevent unbounded growth but provide no fairness.

Required future authority includes:

- per-peer/folder quota reservation tied to authenticated membership;
- temporary ingress versus promoted retained-object states;
- expiry and garbage-collection policy generation;
- dead-letter reason and operator replay authority;
- deduplicated content-addressed object storage; and
- accounting that cannot be reset by actor-field spoofing.

## Audit and refactor findings

### New file-delivery lexical audit

`tools/audit_sync_replica_file_delivery.py` contains 23 checks for:

- live authority in every public service signature;
- private capability validation before context/durable work;
- payload and wire policy before lease mutation;
- bounded stage before causal admission;
- same opaque authority passed to nested evidence service;
- nontransferable projection guard shape;
- exact cutpoint and unambiguous-primary conditions;
- guard coverage through materialization and receipt construction;
- named cross-store ambiguity handling;
- terminal-only settlement;
- O(history) owner honesty;
- negative runtime cases; and
- test-only mint separation.

The audit labels itself `lexical-hygiene-not-semantic-proof`. It cannot prove
control flow, exception safety, SQLite semantics, TLS liveness, or filesystem
durability. Runtime, compiler, sanitizer, and crash evidence remain load-bearing.

### Causal owner audit

The owner audit is version 7 with 41 checks. It was refactored to inspect the
shared claim core rather than assuming all authority sits in a public wrapper.
It now requires guard nontransferability, exact `BEGIN IMMEDIATE` ordering,
cutpoint equality, retained operation equality, active/sole-primary projection,
independent-writer runtime blocking, and stale-cutpoint no-op proof.

### Package-verifier correction

The merged atomic publisher added a restart-reconciliation executable. Its source
audit correctly required the test in the release verifier, but the verifier had
not been updated. The complete 185-test registry exposed the omission. Rev0878
adds the reconciliation test and the complete file-effect surface to
revision-scoped package requirements. The source audit was not weakened.

### Build modularity

The cube now has 75 literal libraries, 96 executables, and 188 literal CMake
`add_test` calls. Yet the largest files remain:

- `src/sync_domain.cpp`: about 15,167 lines;
- `src/sync_domain_selftests.cpp`: about 9,601 lines;
- `src/sqlite_replay_ledger.cpp`: about 4,529 lines;
- `src/sync_replica_sqlite_owner.cpp`: about 3,713 lines; and
- `tests/sync_replica_sqlite_owner_test.cpp`: about 3,722 lines.

The complete Debug build spent most of its time recompiling old monoliths, not
the new effect slice. Link target proliferation has not delivered equivalent
semantic or compile-time modularity.

Recommended refactor sequence:

1. extract canonical restore/attestation from transition orchestration;
2. split state-machine transitions from SQLite encoding;
3. generate repeated CMake target/test/sanitizer declarations;
4. maintain an affected-authority preset for iteration;
5. keep one complete legacy registry before release;
6. measure include and link fanout; and
7. preserve O(history) owners as differential oracles rather than optimizing
   them in place.

### Evidence growth

Before rev0878 evidence, `REVISION_EVIDENCE/` contains more than 4,500 files and
about 41 MB. Compression does not eliminate hash, extraction, navigation, and
review cost. New evidence remains compact: parent hashes, source delta, current
projection, audit summaries, focused logs, and validation hashes. Bulk historical
logs should move to a content-addressed store with externally trusted signatures.

## What has gone severely wrong or remains dangerous

### Corrected in rev0878

- **Stale projection could authorize a visible file.** Closed with the exact
  writer-serializing projection guard and independent-writer runtime proof.
- **Oversized File work could consume endless leases.** Closed for declarative
  wire/payload limits by checking before lease mutation.
- **File orchestration could have downgraded live authority to public context.**
  Closed by same-capability composition and private friend access.
- **Package verification could omit restart reconciliation.** Closed by mandatory
  revision-scoped verifier inventory.

### Still severe

- **The shipped product does not use this path.** Assurance can grow while users
  still execute the older stack.
- **Root path text is not stable root authority.** A rebound directory can change
  where a later valid effect lands.
- **Create-new is not synchronization.** Updates and deletion require explicit
  projection/effect semantics, not blind replacement.
- **Staging can be used for storage denial.** Aggregate bounds lack fair-share,
  expiry, and reclaim authority.
- **Receipts are not archival signatures.** Structural hashes and a past TLS
  channel do not give offline third-party verification.
- **Full-history restore is not production-scale.** The current path is an oracle
  and crash scaffold.
- **The name overstates privacy.** Endpoint and traffic metadata remain visible;
  no adversary model supports an anonymity claim.

## Speculative architecture

### 1. Root-bound single-peer executable

Create `anonsync_replica_service` around the newer owners. Configure one folder,
one pinned peer, one retained root capability, one TLS 1.3 framed connection, and
one immutable File operation. Inject process exit at every sender transaction,
frame prefix/body, stage, admission, guard, file write, rename, file fsync,
directory fsync, effect mark, receipt, and settlement frontier.

### 2. Immutable object store plus mutable path projection

Store payload once under content identity. Let visible path records name object
ID, operation ID, prior projection generation, and conflict policy. This is a
better basis for update convergence than overwriting a destination whose current
identity is unknown.

### 3. Signed receiver effect log

Append terminal transitions to a receiver-owned signed log. A receipt should name
log position, exact causal/effect cutpoints, actor key epoch, and signature.
Membership revocation and recovery must define how old signatures remain
interpretable.

### 4. Indexed owner with oracle differential testing

Build a separate incremental owner with bounded indexes and chunk/Merkle
attestation. Generate histories, crash schedules, policy changes, corruption,
and retries; require exact equivalence to the current O(history) owners for
canonical evidence, projection, outbox/effect state, and cutpoints.

### 5. Tombstone and compaction authority

Define delete effects, conflict preservation, causal stability, offline/revoked
replica policy, checkpoints, object reclamation, and full-resync behavior before
introducing destructive namespace operations.

### 6. Privacy statement before privacy mechanisms

Specify local-host trust, peer knowledge, discovery observers, relay knowledge,
certificate exposure, endpoint timing/volume, storage compromise, and traffic
correlation. Only then evaluate private discovery, padding, batching, relay
indirection, or group key protocols. Payload encryption alone is not anonymity.

## Validation authority

Final compiler, sanitizer, stress, complete-registry, active-projection,
manifest, lineage, and package-verifier results are recorded in
`RELEASE_GATE.json` and `REVISION_EVIDENCE/rev0878/`. This document is a design
and audit narrative, not a substitute for those machine-readable records.

## Deliberate nonclaims

Rev0878 does not claim:

- use of the new path by the shipped executable;
- normal replacement/update convergence;
- tombstone or deletion effects;
- stable root identity across calls or restart;
- exactly-once behavior against a malicious or privileged local writer;
- staging fairness, expiry, or garbage collection;
- independently signed or offline-verifiable effect receipts;
- complete membership/key lifecycle;
- complete retry/backoff/dead-letter policy;
- network event-loop behavior or hostile-client cancellation;
- production-scale incremental ownership;
- anti-entropy, causal stability, compaction, or old-replica rejoin;
- Windows parent-directory durability;
- anonymity, unlinkability, or metadata hiding;
- externally trusted signed provenance;
- full-project Clang, sanitizer, or ThreadSanitizer coverage; or
- formal proof.

Within those limits, rev0878 closes a real stale-authority race and establishes
the first merged path where a live authenticated request can produce a bounded,
private, crash-reconciled visible file and an exact terminal sender settlement.
