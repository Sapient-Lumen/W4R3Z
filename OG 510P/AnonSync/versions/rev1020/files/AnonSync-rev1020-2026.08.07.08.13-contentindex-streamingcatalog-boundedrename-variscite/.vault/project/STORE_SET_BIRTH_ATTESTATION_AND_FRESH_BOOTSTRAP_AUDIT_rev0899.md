# Store-set birth attestation and fresh-bootstrap audit — rev0899

## Executive conclusion

The heart of AnonSync is **durable bounded causal convergence in which authority
is explicit, evidence-bound, recoverable, and never fabricated by observation**.
The system is not primarily a copier, a transport wrapper, or a database. Its
central obligation is that every visible effect, retry, lease, clock decision,
membership claim, and convergence result can be traced to exact authorized
evidence and a live owner whose authority has not silently widened.

Rev0898 made one canonical deployment manifest the sole product configuration
capability and published it last. That was necessary, but it left a severe
composition defect: the manifest described a set of stores, while the stores did
not prove that they were born as that set. A canonical self-digested manifest
could therefore be constructed around independently valid resources. A same-role
SQLite database with compatible owner-level folder/actor state, or a payload
root carrying only the older folder marker, could be substituted behind a new
manifest. The manifest would be internally correct while the deployment it
purported to commit had never existed.

Rev0899 corrects that defect for fresh product deployments. Bootstrap now mints a
random 256-bit deployment ID, computes the exact manifest digest before store
creation, persists the same deployment identity inside every selected SQLite
role and the product payload lease anchor, gives each SQLite role a distinct
header-level application-ID fence, refuses adoption of pre-existing product
namespaces, and requires exact store-internal attestation before any operational
owner is constructed. The manifest remains the publish-last commit marker, but
it is no longer the only witness of composition.

This is an integrity and accidental-recomposition boundary, not a defense
against a hostile process that can rewrite every file as the deployment user. A
same-UID or privileged attacker can recompute unkeyed digests and rewrite the
manifest, binding rows, and payload marker. Rev0899 does not claim otherwise.

## 1. Mission model

AnonSync's mission can be stated as five coupled requirements.

1. **Exact evidence outranks summaries.** Hashes, counts, indexes, status JSON,
   cache entries, and process exit codes are accelerators or observations. They
   cannot invent history or authorize a transition that exact durable evidence
   does not support.
2. **Authority is capability-shaped and bounded.** A path string, database name,
   network address, or configuration field is not itself authority. Mutation is
   performed by a narrow owner that proves identity, role, policy, and cutpoint
   immediately before crossing the mutation frontier.
3. **Crash recovery preserves truth.** Interruption may leave work pending or
   ambiguous, but it must not convert "possibly happened" into "did not happen"
   or silently adopt unrelated durable state.
4. **Equivalent authorized histories converge.** Independent replicas must
   derive the same active and visible state from equivalent evidence, trust, and
   cutpoints, despite retries, reordering, duplicate delivery, and restarts.
5. **Observation never bootstraps authority.** Status, health, inspection, send,
   receive, and recovery paths may attest existing owners; they must not create a
   database, marker, identity, lease namespace, or membership merely because a
   path happened to be empty.

The product spine is now materially closer to those requirements. It is still a
bounded command surface rather than a complete continuously operating sync
product, and the privacy implied by the project name remains a separate,
unimplemented threat-model obligation.

## 2. The severe defect in rev0898

### 2.1 Configuration attestation was not common-birth attestation

Rev0898's manifest was exact, bounded, canonical, self-digested, path-bound, and
mandatory. These properties proved that the process read the intended document
and that the document selected one unambiguous path set. They did not prove that
those resources shared one initialization event.

A self-digest detects accidental byte corruption and noncanonical encoding; it
is not a signature. Anyone able to write the manifest can recompute it. Before
rev0899, each SQLite owner independently attested only its role schema and
role-specific semantic state. The payload root's v2 identity marker bound a
folder but not the product deployment. Consequently, an operator mistake,
restoration mistake, copied directory, automation bug, or malicious local writer
could assemble a canonical manifest over stores that were individually healthy
but collectively unrelated.

That failure is dangerous because owner-level checks can all pass. The defect is
not an obvious missing file or malformed schema. It is a false claim about the
provenance of a composed authority set.

### 2.2 Why path binding alone was insufficient

The rev0898 manifest included every selected absolute path and refused a copied
manifest whose embedded path no longer matched the opened path. But a path names
where an object is expected; it does not permanently identify the object at that
path. Files can be restored, exchanged, rebound through mount namespaces, or
replaced between checks. A canonical path set therefore needs store-carried
identity in addition to document-carried intent.

### 2.3 Why compatible folder and actor values were insufficient

Folder and actor identity are semantic inputs used by several owners. They are
not unique deployment birth certificates. Two independently initialized
installations can intentionally use the same folder and actor values. Treating
that compatibility as common provenance would collapse configuration agreement
into identity.

## 3. Implemented correction

### 3.1 One dependency-light deployment identity

`src/sync_replica_deployment_identity.hpp/.cpp` now owns the exact value shared
by the manifest, SQLite stores, and product payload root:

- a 64-character lowercase deployment ID representing 32 random bytes;
- the exact SHA-256 digest of the canonical deployment manifest;
- the canonical absolute manifest path;
- the folder ID; and
- the local actor device ID and epoch.

The ID is generated with OpenSSL `RAND_bytes`, its return value is checked, and
OpenSSL's error queue is surfaced on failure. A second hand-rolled random source
was deliberately not introduced. The validation owner also prevents each store
adapter from silently inventing different path, actor, digest, or length rules.

The deployment ID distinguishes two fresh deployments whose paths, folder,
actor, limits, and profile are otherwise identical. The manifest digest binds
all exact configuration bytes. Both are required because neither property
substitutes for the other.

### 3.2 Deployment manifest v2

The deployment manifest is now
`anonsync-replica-deployment-manifest-v2`. Its self-digest domain was advanced,
and its exact schema grew from 22 to 26 fields. It commits:

- `deployment_id`;
- `sqlite_application_id_policy: role-specific-v1`;
- `store_internal_deployment_binding: required-v1`; and
- `bootstrap_store_adoption_policy: fresh-only-v1`.

Digest computation is now an explicit API. Bootstrap can populate the exact
manifest digest before any database or payload authority is created, then pass
that digest into every store binding. Encoding rejects a pre-populated digest
that conflicts with the canonical unsigned document. Decoding still enforces
strict UTF-8, strict JSON, duplicate-key rejection, exact field closure,
canonical re-encoding, opened-path equality, the 16 KiB read ceiling, and the
self-digest.

The manifest is still published last. That publication means normal operations
may begin; it does not claim one filesystem-level transaction across all
resources.

### 3.3 Exact SQLite role and deployment binding

`src/sync_replica_deployment_binding.hpp/.cpp` introduces one pre-owner gate for
all four product SQLite roles:

- replica: `0x41535201`;
- file effect: `0x41535202`;
- TLS membership: `0x41535203`; and
- TLS membership anchor: `0x41535204`.

These values occupy SQLite's signed 32-bit `application_id` header field and
provide an early wrong-role classifier. They are intentionally documented as
internal role fences, not globally registered `file(1)` identifiers and not
sufficient proof by themselves.

Every database also receives exactly one STRICT singleton table named
`anonsync_store_set_binding`. The durable row binds:

- format generation;
- deployment ID;
- manifest digest and manifest path;
- store role and database path;
- folder ID;
- local device ID and epoch;
- expected SQLite application ID; and
- a domain-separated, length-framed SHA-256 digest over all authority fields.

Initialization runs under an immediate SQLite transaction, requires both the
main and temporary binding namespaces to be absent, requires the prior
application ID to be zero, writes the header and exact table/row, proves the
staged state, commits, then proves it again through a fresh read transaction.
Operational attestation checks all of the following before returning the opened
database to a role owner:

1. SQLite reports an absolute, already lexically normalized main-database
   filename exactly equal to the manifest-selected path.
2. The header application ID matches the selected role.
3. the main `sqlite_schema` contains exactly the expected STRICT table text;
4. the temporary schema contains no shadow with the binding name;
5. exactly one row exists; and
6. every row field and the independently recomputed binding digest match the
   deployment identity and role.

`src/anonsync_replica.cpp` centralizes this in
`open_bound_operational_database_or_throw`. Status, clock observation/recovery,
enqueue, membership publication, sending, and receiving cannot construct any
SQLite role owner before this gate succeeds.

### 3.4 Fresh-only bootstrap across the selected namespace

Before the first store mutation, `init` now requires:

- the deployment manifest to be absent;
- every selected SQLite main file to be absent;
- every selected `-journal`, `-wal`, and `-shm` sidecar to be absent;
- the selected product payload root to be empty; and
- the selected delivery/files root to be empty.

This prevents a missing main file from being treated as fresh while an orphan
WAL or shared-memory sidecar remains, and prevents bootstrap from legitimizing
pre-existing payload or delivered-file bytes. The complete selected namespace
is preflighted before the first database is opened for creation, avoiding a
known failure mode in which an early resource is created before a later
collision is discovered.

Each bootstrapped database gets its store-set binding before its role-specific
owner is constructed. This ordering makes the narrow binding gate the first
persistent application schema, rather than trying to retrofit provenance after
role initialization.

Fresh-only is deliberately conservative. Rev0899 does not migrate or adopt
rev0898 deployments. Existing deployments need an explicit offline migration or
re-initialization protocol; silently stamping a deployment ID onto pre-existing
stores would recreate the provenance fabrication this revision is meant to
remove.

### 3.5 Product payload marker v3

The standalone payload-store v2 API remains available for lower-level tests and
non-product composition. Product construction now uses
`.anonsync-payload-store-identity-v3`, whose exact payload binds the deployment
ID, manifest digest and path, folder, local actor, and writer-lease protocol.
The payload snapshot digest also binds the selected marker basename and exact
marker digest, so changing identity generations cannot preserve an apparently
identical snapshot authority.

Product bootstrap refuses adoption when any payload or transient entry already
exists. Existing-only operation requires the exact v3 marker and cannot mint it.
The implementation rejects a root carrying another current identity generation
rather than treating that marker as an unknown ordinary file.

### 3.6 Output provenance

Every product command result now includes both `deployment_id` and
`deployment_manifest_digest`. These values are not authorization tokens, but
they let operators and process-level tests correlate an observation with the
exact committed deployment and configuration bytes.

## 4. Audit and refactor findings

### 4.1 Independent proof was added to the process test

The first process-test revision merely queried the binding rows and compared
selected fields. That would have allowed a correlated implementation/test bug in
the digest framing to go unnoticed. The proof was strengthened so Python
independently reconstructs canonical manifest bytes and independently computes
the SQLite binding digest. This is materially stronger than asking the C++ code
to verify output it produced itself.

The executable proof now includes:

- two independent deployments and nonrepeating deployment IDs;
- exact manifest v2 policy and self-digest verification;
- all four role application IDs and binding rows;
- exact product payload v3 marker verification;
- pre-seeded payload-root rejection without mutation;
- orphan `-wal` rejection without creating any selected store;
- pre-seeded files-root rejection without mutation;
- canonical manifest forgery with a new deployment ID and recomputed self-digest;
- same-role replica database substitution;
- cross-role database substitution;
- foreign product payload-root substitution;
- copied and same-path-tampered manifests;
- missing/detached stores and raw option mixing;
- durable clock quarantine and generation-fenced recovery; and
- real mutual TLS delivery, exact filesystem publication, authenticated receipt,
  and terminal sender settlement.

The canonical-forgery case is the decisive regression test. It proves the new
store-carried binding rejects a manifest that is perfectly canonical and
self-consistent but claims a deployment birth the database never witnessed.

### 4.2 Source audits were corrected rather than bypassed

Three lexical audits initially described the older open architecture. They were
updated to recognize the bound-open frontier and v3 payload marker without
weakening their exact inventories:

- database open policy: 16/16;
- bootstrap authority: 19/19; and
- payload-store source audit: 33/33.

A new deployment-binding audit checks 20/20 invariants, including the random ID,
manifest policy, distinct role headers, exact singleton schema, framed digest,
opened filename, temporary-shadow rejection, transactional initialization,
post-commit reproof, pre-owner ordering, whole-namespace freshness, v3 marker,
non-adoption, compiled attacks, process attacks, and normal build registration.

These scripts are tripwires, not formal semantic proofs. Their value is that a
future refactor cannot casually reintroduce an unbound open or creation path
without changing a reviewed inventory and the registered test graph.

### 4.3 Role-schema composition was kept explicit

The file-effect owner's exact allowed schema inventory now includes the common
binding table. The common binding implementation was not duplicated into each
role owner. This keeps provenance policy in one leaf while preserving each
owner's exact schema closure.

### 4.4 Full validation result

After the final implementation and audit changes:

- the complete GCC 14 Debug build finished;
- bundled SQLite is 3.53.3;
- all 219 registered tests passed in 18.30 seconds with eight workers;
- the focused product/authority lane passed 9/9;
- the direct executable process proof passed; and
- all four source-audit sets passed: 16/16, 19/19, 20/20, and 33/33.

## 5. Primary-source research and implications

Research was rechecked on 2026-07-25 against implementation-owner documentation.
The conclusions below distinguish sourced behavior from AnonSync design
speculation.

### 5.1 SQLite application ID is an early classifier, not authority

SQLite documents `PRAGMA application_id` as the signed 32-bit big-endian value at
offset 68 in the database header, intended to identify an application file
format:

- https://sqlite.org/pragma.html#pragma_application_id
- https://www.sqlite.org/fileformat.html#the_application_id

Implication: it is useful for rejecting an obvious wrong-role file before
running owner schema restoration. It is not collision-resistant, secret,
role-authenticating, or a substitute for the exact binding row and schema. The
rev0899 architecture uses it only in that supplementary role.

### 5.2 WAL does not provide store-set atomicity

SQLite's WAL documentation and ATTACH documentation state that transactions are
atomic per database but not across multiple attached databases as a set when
WAL is used:

- https://www.sqlite.org/wal.html
- https://sqlite.org/lang_attach.html
- https://www.sqlite.org/tempfiles.html

The temporary-files documentation explains that the rollback-journal
super-journal mechanism does not cover WAL, so after a power loss some database
files in a multi-file operation may roll forward while others roll back.

Implication: combining the four role databases with ATTACH would not make
AnonSync bootstrap or future cross-store transitions crash-atomic under the
current WAL policy. A real solution needs an explicit coordinator/recovery
protocol, one consolidated database, or a different journal-mode and durability
tradeoff—not an assumption inferred from SQL transaction syntax.

### 5.3 WAL sidecars are persistent authority-bearing state

SQLite explicitly warns that the WAL is part of a database's persistent state
and must remain with the main file when copied or moved. Read-only WAL access may
also require existing or creatable WAL/SHM sidecars. This supports rev0899's
choice to treat `-wal` and `-shm` names as part of fresh-bootstrap exclusion and
supports the remaining concern that status through a normal WAL connection is
not necessarily side-effect-free.

SQLite's WAL page, updated 2026-04-13, also documents a rare WAL-reset race fixed
in 3.51.3 and later. AnonSync's bundled SQLite 3.53.3 is newer than that fix.
However, SQLite 3.53.4 was released on 2026-07-24 and explicitly fixes problems
present in 3.53.0 through 3.53.3. The official release identifies source ID
`bf7c7f30031888f4e796e429ab3978879485813aaca6f641c7b33e4e09459bcc`,
publishes SHA3-256
`67f423e9ebbbdc473cbc4772c872ee6b89f31fde4ed0279a5c25d5f65c043a16`
for `sqlite3.c`, and publishes SHA3-256
`628a44cfe82c66aed1ccbbe85a562d2e33ebe64b3288981ed76285612227934e`
for the 3.53.4 amalgamation archive:

- https://sqlite.org/releaselog/3_53_4.html
- https://sqlite.org/download.html

Implication: the rev0899 store-binding code is tested against a known pinned
runtime, but the runtime is no longer the newest patch release. This revision
does not silently replace a nearly ten-megabyte reviewed dependency at packaging
time. A follow-up should import the exact official archive, prove both published
SHA3 values and local SHA-256 pins, rebuild the whole graph, and rerun the SQLite
boundary, crash, process, and full registered lanes. Until then, dependency
freshness is an explicit release caveat rather than an implied claim.

### 5.4 Durability depends on the platform honoring flush semantics

SQLite's atomic-commit documentation explains its assumptions about `fsync` /
flush, atomic deletion, filesystem behavior, and the inability to defend against
a rogue process rewriting an ordinary database file:

- https://www.sqlite.org/atomiccommit.html

Implication: AnonSync's crash-consistency claims remain conditional on the VFS,
filesystem, kernel, storage controller, and mount semantics satisfying those
assumptions. The release does not claim universal power-loss behavior on unusual
or broken storage stacks.

### 5.5 OpenSSL CSPRNG behavior supports fail-closed identity generation

OpenSSL documents `RAND_bytes` as a CSPRNG, normally auto-seeded from the
operating system on major platforms, with a return value that must be checked
because entropy failure moves the generator into an error state:

- https://docs.openssl.org/3.6/man3/RAND_bytes/

Rev0899 checks that return and rejects bootstrap on failure. The generated ID is
an unguessable uniqueness value, not a secret capability and not a signature.

## 6. What remains missing or materially dangerous

### 6.1 Interrupted bootstrap has no recovery state machine

The largest immediate gap is now operational rather than compositional. Init
preflights the whole namespace, creates and binds stores, validates owners, and
publishes the manifest last. A crash between those steps can leave one or more
correctly bound resources with no committed manifest. Fresh-only policy then
refuses to adopt them, which is safe but strands the directory.

The next design should add an explicit bootstrap journal with bounded states such
as:

`PREPARED -> RESOURCE_CREATED -> RESOURCE_BOUND -> RESOURCE_VALIDATED -> COMMITTED`

Each transition should carry the deployment ID, manifest digest, exact resource
inventory, and a monotonically increasing generation or exact state digest. An
`inspect-init` command should classify every selected path without mutation. A
`resume-init` command should proceed only when every observed resource exactly
matches the prepared identity and the next expected state. A quarantine/abort
path should move or remove only resources whose provenance is proven by that
journal. Merely deleting whatever occupies the configured paths would be an
authority violation.

A useful speculative design is a small descriptor-rooted bootstrap coordinator
file, published before resource creation and distinct from the final operational
manifest. It should be create-new, immutable by state generation, and recoverable
by exact CAS rather than rewritten in place. The final manifest remains the
operational commit marker; the coordinator explains noncommit.

### 6.2 Freshness checks are vulnerable to noncooperating-writer races

Whole-namespace preflight closes ordering mistakes but not check-to-create races.
A noncooperating process can create a sidecar, payload, or delivered file after
preflight and before the corresponding owner adopts its directory or file. The
payload store performs a stronger under-lease scan before publishing its marker,
but the complete deployment set has no common filesystem lease. The files-root
emptiness proof is especially weaker than the payload-root owner.

A descriptor-rooted deployment directory owner should hold live directory
handles, use create-new operations relative to those handles, and re-attest exact
inventory immediately before each mutation. On Linux, `openat2` resolution flags
such as beneath/in-root/no-symlink/no-magic-link are worth evaluating. A portable
component-walk owner is still needed for other platforms. None of these remove a
hostile same-UID writer unless access control or a cooperative lock protocol
excludes it.

### 6.3 Separate resources still lack one crash-atomic transaction

The manifest, four possible SQLite databases, payload marker, payload content,
and delivery root are distinct durability domains. Store-set birth attestation
proves common intended identity; it does not make their updates atomic. Future
operations that must change more than one database need explicit intent,
prepare, commit, and recovery evidence, with idempotent replay and a clear
visibility cutpoint.

A medium-term architectural question is whether the product should retain four
SQLite files. Separate files preserve owner isolation and narrow schemas, but
multiply open/recovery/checkpoint surfaces and complicate cross-store
coordination. A single database with independently attested schemas could reduce
atomicity complexity while widening the blast radius of one connection. This
tradeoff should be measured against actual cross-store transition frequency,
not decided cosmetically.

### 6.4 The binding is unkeyed

The manifest digest and store binding digest are SHA-256 integrity checks, not
message authentication codes. They catch corruption, wrong copies, stale
automation, and accidental recomposition. They do not stop a writer who controls
all deployment files.

If hostile local writers enter the threat model, the design needs a key rooted
outside the writable store set: an OS keystore, hardware-backed identity, signed
operator manifest, or capability delivered by a supervisor. Adding an HMAC key
inside the same writable directory would add complexity without changing the
attacker's power.

### 6.5 Path authority is not fully descriptor-rooted

Rev0899 proves canonical absolute strings, exact opened SQLite filenames, final
manifest no-follow behavior, directory identity, and several mount/inode
properties inside lower-level owners. It does not hold one ancestor directory
capability across every product path. Ancestor symlink replacement, bind-mount
rebinding, namespace transitions, and path races remain platform-dependent.

The long-term boundary should be a deployment-root capability from which every
selected resource is resolved. The manifest can retain portable relative names
and logical identity, while the live root owner proves actual filesystem
containment.

### 6.6 Status is still not a forensic read-only operation

`status` opens the operational WAL owners through the same writable connection
profile. Even without application-level writes, SQLite may create or update
shared-memory state, perform recovery, or checkpoint on connection close. A
truly observational command should have a separately designed read-only or
immutable-snapshot path and must clearly report when exact WAL state cannot be
observed without write access. Simply adding `SQLITE_OPEN_READONLY` is not enough
because WAL sidecar and recovery semantics matter.

### 6.7 The product is not yet continuously useful

The executable can initialize, inspect, enqueue, publish membership, recover a
clock, send one delivery, and serve one delivery. It still lacks:

- a bounded durable supervisor and scheduler;
- peer discovery, rendezvous, and NAT traversal;
- causal directory creation, rename, tombstone, and symlink semantics;
- chunking, resumable transfer, and large-file streaming;
- reachability analysis, indexing, retention policy, and garbage collection;
- multi-device key lifecycle and revocation workflows;
- at-rest encryption and secret management; and
- a defensible anonymity/privacy threat model.

The next product step should follow the bootstrap recovery and path-capability
work. A daemon built before those boundaries would automate stranded partial
initialization and path races rather than solve them.

## 7. Cloudtainer waste and corrective direction

The full test registry is fast once built: 219 tests completed in 18.30 seconds.
Compilation is the expensive part. A CMake regeneration after a narrow product
change scheduled 426 compile/link actions across the fragmented graph. The first
command ceiling left 241 actions and the second left 162; the resumed build then
finished, and the final dependency closure reported no work. The graph contains
many small static libraries and test executables whose linkage fans out through
common invariant owners.

This is not evidence that ownership boundaries should be collapsed. The current
leaf libraries make authority review and source audits tractable. Global unity
builds or a monolithic target could hide dependency errors, macro collisions,
ODR mistakes, and accidental coupling. The waste should be attacked with
measurement:

1. Add an opt-in compiler launcher (`ccache` or `sccache`) and record hit/miss,
   cache-size, and cold/warm build evidence.
2. Add a documented product fast lane that builds `anonsync_replica` plus its
   direct unit/process/audit targets, while preserving the full graph as the
   release gate.
3. Emit a target dependency/fan-out report and identify headers that force broad
   recompilation.
4. Trial target-scoped unity builds only on stable implementation leaves with no
   macro or anonymous-namespace collision, and compare diagnostics and cache
   behavior.
5. Keep generated objects outside release archives and continue verifying the
   exact source-only package path policy.

The most likely near-term win is compiler caching plus a named fast lane, not a
source-architecture rewrite.

## 8. Recommended sequence

The recommended next sequence is:

1. implement exact inspect/resume/quarantine semantics for interrupted init;
2. introduce one descriptor-rooted deployment directory capability and tighten
   the files-root freshness frontier;
3. design a side-effect-aware status/export path;
4. decide, from transition data, whether cross-store coordination or database
   consolidation is the better atomicity strategy;
5. add a bounded supervisor with durable scheduling, retry budgets, shutdown
   cutpoints, and operator-visible blocked reasons;
6. implement causal filesystem semantics and payload lifecycle/GC; and
7. define the anonymity, metadata, key, and local-attacker threat model before
   making privacy claims.

## 9. Explicit nonclaims

Rev0899 does **not** claim:

- cross-resource or multi-database atomicity;
- safe automatic adoption or migration of rev0898 stores;
- automatic resume, rollback, quarantine, or cleanup after interrupted init;
- resistance to a hostile same-UID or privileged local writer;
- descriptor-rooted resistance to every ancestor, mount, or namespace race;
- side-effect-free read-only status;
- universal filesystem, VFS, kernel, storage-controller, or power-loss behavior;
- exactly-once network delivery;
- continuous production supervision;
- causal directory/rename/tombstone/symlink convergence;
- chunked/resumable large-file transfer, indexing, reachability, or GC;
- at-rest encryption; or
- anonymity, endpoint hiding, unlinkability, cover traffic, metadata
  minimization, private-interest overlap, or traffic-analysis resistance.

The revision's real claim is narrower and important: a fresh committed product
deployment can no longer be represented merely by a canonical manifest over
independently valid stores. Every selected persistent authority now has to attest
the same exact deployment birth and role before normal operation can begin.
