# Offline database recovery and deployment-singleton audit — rev0981

## Product reason

Rev0980 introduced an exact database recovery epoch but left it only as a C++
owner method. An operator replacing or restoring a replica database had no
shipping command that could inspect the current lineage, advance it under an
exact expectation, or prove that the retained service was stopped. That made
the documented recovery requirement aspirational rather than executable.

The adjacent lifecycle audit found a second production defect. The retained
`run` service owned the deployment singleton, but `anonsync_sync once` did not.
A one-shot synchronization process could therefore open the same deployment's
SQLite, payload, catalog, filesystem, and network owners beside the retained
service. SQLite and filesystem fences limit some individual races, but two
shipping schedulers over one share were never a supported composition.

## Operator-visible recovery ceremony

Rev0981 adds two exact offline commands:

```text
anonsync_sync database-recovery-inspect --manifest ABSOLUTE_JSON
anonsync_sync database-recovery-advance --manifest ABSOLUTE_JSON \
  --expected v1:INCARNATION:EPOCH:CUTPOINT
```

Inspection acquires the deployment singleton before opening the primary replica
database. It then opens that exact existing database through the descriptor-
rooted read-only VFS, attests the deployment binding, requires current schema
v7, and uses the established read-only snapshot loader. It emits one canonical
expectation token. It cannot create, initialize, migrate, checkpoint, or write
the selected database family.

Advance acquires the same deployment singleton and first repeats the exact
forensic read-only observation. A malformed or stale incarnation, epoch, or
cutpoint is rejected while no writable SQLite connection exists. Only an exact
preflight result permits the read-only handle to close and the existing
operational primary database to open for writing. The short-lived
`SyncReplicaSqliteOwner` then calls the rev0980 recovery transition and
independently re-proves the same token under `BEGIN IMMEDIATE`; the preflight is
never mutation authority. A successful transition advances recovery epoch and
state generation once; preserves every causal, evidence, visible, outbox,
clock, policy, limit, and historical-pin fact; and publishes one successor
cutpoint.

The command name is the operator assertion that a restore or replacement has
completed. The response says so explicitly, but the program does not inspect,
copy, replace, or validate database files. The ceremony must be run only after
the operator's recovery action and while the retained service is stopped.

## Stale rejection before writable open

The adjacent audit found a load-bearing authority-order defect in the first
rev0981 implementation. `database-recovery-advance` acquired the deployment
singleton correctly, but then opened writable SQLite and constructed the
mutable owner before comparing the operator's token. A stale request made no
logical database change, yet merely opening the WAL family could perform
recovery, create or update sidecars, checkpoint, migrate, or otherwise alter
bytes before the command reported rejection.

The final ceremony owner retains no database handle. It performs these stages:

1. acquire the deployment singleton;
2. open the attested primary database through the existing-only forensic VFS;
3. load the exact current incarnation, epoch, state generation, and complete
   cutpoint;
4. reject a stale token and return while no writable handle has existed;
5. close the forensic handle;
6. open the attested writable primary database; and
7. re-prove the token under the existing `BEGIN IMMEDIATE` transition before
   committing one successor epoch.

This two-stage structure is intentional. The read-only preflight prevents
known-stale authority from causing writer-side effects. The transaction reproof
prevents a low-level writer outside the deployment singleton from racing the
interval between observation and mutation.

The process regression fingerprints the exact SQLite family—membership,
permission mode, size, and SHA-256—before and after malformed input, three
canonical stale-token variants, and reuse of the consumed exact token. Every
rejection preserves that family byte-for-byte.

## Read-only WAL ordering correction

The first implementation selected the read-only rooted VFS but performed a
persistent-schema query before selecting connection-local exclusive locking.
For a WAL database without an existing writable shared-memory domain, that
first page read attempted to join or create `-shm` and failed through the
read-only VFS.

The corrected shared operational-database wrapper now applies, in order:

1. exact descriptor-rooted read-only open;
2. exact open-handle/path re-attestation;
3. bounded busy timeout;
4. connection-local `locking_mode=EXCLUSIVE`;
5. the hardened query-only/defensive read profile; and only then
6. persistent-schema and journal-mode reads.

SQLite therefore builds its WAL index in private heap memory before any page
read, while the rooted VFS independently denies main-file and sidecar mutation.
The focused process test fingerprints every existing SQLite family member by
path, mode, size, and SHA-256 across inspection.

## Shared targeting refactor

The manifest-to-primary-database targeting and deployment-binding proof had
been embedded inside `SyncReplicaFolderProcessOwner`. Rev0981 extracts one
writer seam and one read-only counterpart:

- `open_attested_sync_replica_primary_database_or_throw`; and
- `open_attested_sync_replica_primary_database_read_only_or_throw`.

The retained folder owner and offline recovery commands now share the same
canonical database path and role-binding logic. The read-only disposition is a
first-class `SyncReplicaOperationalDatabaseOpenDisposition`; it is not a
writer-backed owner used in an observation-shaped command.

## One deployment, one shipping process owner

`anonsync_sync once` now reads the manifest and acquires
`SyncReplicaPeerServiceSingletonOwner` before parsing route, TLS, peer, or
folder-pass options and before opening any other product authority. The
retained service, one-shot synchronization, inspection, and recovery advance
therefore collide at the same deployment identifier.

This is deliberately earlier than ordinary argument-dependent authority. A
real-process regression invokes an intentionally incomplete `once --manifest`
while the service is live and still receives the exact ownership failure; it
cannot reach route parsing merely because required network arguments were
omitted. Offline inspection is rejected at the same cutpoint.

The singleton is deployment-identity authority, not a global database-path
lock. Durable deployment binding remains independently attested after open.
Owner-controlled corruption or fabrication of a manifest is outside the claim
that one valid retained deployment cannot run two shipping owners.

## Commit return and authority-bearing route audit

The adjacent cutpoint audit found one avoidable ambiguous-success path inside
the SQLite owner. The first retained implementation committed the recovery
epoch and then aggregate-initialized the returned owning strings. A host
allocation failure in that copy could throw after durable success. The final
implementation constructs the complete
`SyncReplicaSqliteDatabaseRecoveryEpochResult` before the staged cutpoint is
committed and statically requires that moving the result is `noexcept`. An
ordinary owner return can therefore no longer convert a committed transition
into an allocation exception.

This does not make terminal output a durable receipt. Process death, a closed
output pipe, or a failure in command-side rendering can still occur after
SQLite commits. When completion is uncertain, the safe procedure is to run
`database-recovery-inspect` again and compare the current epoch and cutpoint;
blindly replaying the old token is intentionally stale after success.

The singleton ordering regression was also strengthened. Native-I2P route
parsing may open the configured private-destination file, so an incomplete
`once --manifest` invocation did not by itself prove that all route authority
was behind the singleton. The real service test now supplies an absent absolute
private-destination path while the retained process owns the deployment. It
must report exact deployment ownership rather than a file-open error.

## Narrow authority and runtime proof

The recovery commands report and the process oracle proves that they do not
observe or require:

- the payload store;
- the folder catalog;
- the rooted synchronized files;
- the effect, membership, or anchor stores; or
- any listener, connector, TLS session, or network route.

The test initializes a complete share, records ordinary status, moves the
payload root, files root, and folder catalog outside their configured names,
and performs the entire inspection/stale-token/exact-advance/reuse sequence.
It proves:

1. inspection changes no SQLite family member bytes, mode, size, or membership;
2. noncanonical expectations fail before writable authority and preserve the
   complete SQLite family byte-for-byte;
3. foreign incarnation, future epoch, and foreign cutpoint expectations are
   rejected before writable authority and preserve the complete SQLite family
   byte-for-byte;
4. exact advance increments epoch and state generation once and changes the
   cutpoint;
5. the old exact token is immediately stale; and
6. after unrelated stores are restored, every ordinary status field except
   replica state generation and complete cutpoint is byte-for-byte equivalent.

The database-open source audit now follows this shared production wrapper and
checks the pre-read WAL ordering, explicit read-only disposition, singleton
member order, stale-before-writer ordering, transactional reproof, pre-commit
result ownership, authority-bearing I2P route ordering, narrow response claims,
exact process oracle, and product-lane registration.

## What this proves

For one valid deployment manifest and current operational schema, an operator
can inspect and explicitly advance the in-database recovery epoch without
starting synchronization or touching unrelated share stores. A retained service
or one-shot sync process cannot overlap that valid deployment owner. Exact stale
expectations do not mutate causal authority.

## What this does not prove

The incarnation and recovery epoch remain inside the database they describe.
Restoring an exact older whole-database image restores its earlier incarnation,
epoch, cutpoint, and any token derived from them. Rev0981 therefore does not
provide external anti-rollback authority and cannot prove that the operator
actually restored the intended bytes.

The command also does not reset or delete durable retention-mark records. Any
future consumer of mark age must conservatively treat continuity uncertainty as
an age reset, even after the epoch is advanced, unless an external monotonic
anchor supplies stronger proof. No trusted time, quota policy, collection
quarantine, reclaim, rename, or unlink is added.

## Next safe edge

Make the recovery procedure installable and difficult to misuse: define the
supported backup/restore artifact, exact service-stop and database-family
replacement steps, post-replacement epoch advance, mark-age reset, and an
operator-visible verification checklist. Before destructive retention, choose
an external monotonic continuity anchor or retain the conservative rule that
unknown continuity revokes all accumulated grace.

## Validation

Exact rev0981 active source passed a fresh GCC 14.2 Debug graph (532/532 configured build edges), all 260/260 registered tests after final release-prose sealing, and an independent 41/41 product replay. The 105-check real-process recovery oracle proved descriptor-rooted read-only inspection, byte-for-byte SQLite-family preservation for malformed and stale expectations, exact one-step advancement, consumed-token rejection before writable open, narrow authority, and deployment-singleton ordering. The database-open policy audit passed 48/48 checks and the structural authority audit passed 385/385 checks. A fresh Clang 17 Debug product dependency graph completed 243/243 edges with AddressSanitizer and UndefinedBehaviorSanitizer; all 41/41 product tests passed serially with leak detection and halt-on-error. Aggregate authoritative-log inspection retained no compiler, linker, AddressSanitizer, UndefinedBehaviorSanitizer, runtime-error, or LeakSanitizer diagnostic. The exact rev0980 parent SHA-256 matched 0fc470ab43ce97374e1a562f9c2c275b18bbc6f4e3f8c27127711ed7b18ca40d and passed 41/41 wrapper-aware package checks. The binary-aware source patch reconstructed all 14/14 changed active files and the complete 574-file projection byte-for-byte and by mode. The final active implementation projection contains 574 files / 26,812,446 bytes with SHA-256 d399a8ad3f077bf3467752e4355933be71117cdfff0f4cd789cd0cfd445f1b16. Validation was rerun from the reconstructed exact source after the cloudtainer removed prior unsealed worktrees; all vanished, interrupted, stale-cache, and source-divergent results were excluded. The final wrapper directory and ZIP are publication-gated on 41/41 package checks, CRC integrity, canonical paths, absence of symlinks, and clean-extraction path/byte/type/mode equality.
