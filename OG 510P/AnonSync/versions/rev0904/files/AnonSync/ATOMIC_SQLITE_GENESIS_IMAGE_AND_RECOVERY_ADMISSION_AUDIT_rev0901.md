# Atomic SQLite genesis image and recovery-admission audit — rev0901

## Executive conclusion

AnonSync's heart remains **durable bounded causal convergence in which authority
is explicit, evidence-bound, recoverable, and never fabricated by
observation**. It is not ordinary file copying, and despite the project name it
is not yet an anonymity system. Its strongest design idea is more fundamental:
files, paths, clocks, summaries, retries, process exits, manifests, and database
rows are observations until an exact reviewed cutpoint turns them into bounded
authority.

Rev0900 made interrupted deployment initialization recoverable by publishing an
immutable record containing the byte-exact future deployment manifest before
store mutation. It also documented the largest remaining defect accurately:
SQLite could expose the selected main-file pathname before deployment binding
and role schema had crossed a durable transaction. A crash in that interval
could strand an empty or partially initialized main file. Fresh `init` correctly
refused to adopt it, while `init-resume` correctly rejected it as unbound. The
result was safe but operationally dead-ended.

Rev0901 removes that visible partial-birth interval. Each selected SQLite role is
constructed to complete genesis in a private, filename-free in-memory database.
The exact deployment binding and complete role schema are committed there, the
resulting standalone SQLite main image is serialized and sealed, and only then
is the selected pathname published with immutable create-new/no-replace
semantics. Restart sees either no main file or a complete bound image. It never
needs to infer that an empty file was “probably ours.”

The revision also makes recovery admission explicit. A present rollback-mode
candidate must be a complete SQLite image with no sidecar family. A present WAL
candidate may retain WAL state but may not coexist with a rollback journal. All
present SQLite stores prove exact record-selected identity on retained handles
before any WAL promotion, role-owner construction, or missing-store creation.
This ordering prevents a later foreign or contaminated resource from being
noticed only after an earlier missing store has already been minted.

This is a material correction, not a complete transaction system. Publication
is atomic for one main-file directory entry under the reviewed filesystem
assumptions; the selected store set is still composed of separate databases and
roots. There is no cross-store commit, hostile-writer signature, descriptor-
rooted deployment capability, or automatic forensic quarantine. The product is
still a bounded command spine rather than a supervised synchronization daemon.

## The severe failure that was corrected

The earlier named-database bootstrap sequence was approximately:

1. prove the selected main pathname and sidecars absent;
2. call SQLite with create authority on the selected pathname;
3. initialize the deployment-binding table and application ID;
4. construct the role schema and genesis row set;
5. move the database into the operational WAL profile;
6. publish the final deployment manifest later.

SQLite creates the main file before the first schema transaction is durably
complete. Process death, power loss, storage failure, or an injected exception
between steps 2 and 4 can therefore leave a visible regular file whose bytes do
not prove deployment identity or role genesis. The recovery record names the
intended deployment, but permitting that record to adopt an unbound file would
manufacture authority from proximity. Rejecting it is correct, but without a
quarantine/replace protocol the namespace is stranded.

The defect was especially important because it sat below otherwise strong
store-set binding. A database can have exact role headers, schema, and binding
checks after initialization and still have an unsafe *birth* transition before
those checks exist. Runtime attestation does not retroactively make the earlier
publication cutpoint atomic.

Rev0901 changes the transition to:

1. open a private `:memory:` SQLite main database;
2. prove the connection is filename-free and schema-empty;
3. initialize the exact deployment binding for the future durable pathname;
4. initialize and inspect the complete role genesis on that same connection;
5. serialize the exact standalone main database into bounded resident bytes;
6. reprove the selected main and `-journal`/`-wal`/`-shm` namespace absent;
7. write, synchronize, and publish those bytes create-new without replacing an
   existing final entry;
8. open the exact published image without create authority;
9. attest deployment identity and role before operational promotion;
10. reconcile exact main-file and parent-directory durability;
11. promote the rollback image to WAL, configure the reviewed operational
    profile, and re-attest the binding.

The selected pathname is now absent until step 7, and the bytes introduced at
that step already contain the complete binding and role genesis. A crash before
publication leaves no selected main file. A crash after publication leaves a
self-contained rollback-mode image suitable for exact restart admission.

## Implementation review

### Private complete-image construction

`open_detached_bootstrap_database_or_throw` opens an SQLite `:memory:` database
with read-write/create, full-mutex, private-cache, and memory flags. It requires
that `sqlite3_db_filename(..., "main")` is an empty string, rejects any existing
persistent schema, and installs only connection-local bootstrap policy:
`temp_store=MEMORY`, foreign keys enabled, and untrusted schema disabled.

A five-second busy timeout previously survived from named multi-process database
opens. It was removed from this private path. There is one connection, no
filesystem lock, and no legitimate contender. Retaining the timeout would not
improve safety; it would only preserve a misleading implication that lock
contention was part of detached genesis.

The exact future database path is still part of the deployment-binding digest.
`initialize_sync_replica_sqlite_deployment_binding_in_detached_image_or_throw`
therefore separates *where the image is being built* from *which durable path
the image is authorized for*. It uses the same application ID, exact STRICT
singleton schema, row fields, framed digest, staged proof, and post-commit proof
as named initialization, but replaces the named-file check with a detached-image
profile.

A late audit found that an empty SQLite filename alone was too weak. SQLite also
uses an empty filename for anonymous disk-backed temporary databases opened with
an empty pathname. Those databases normally report rollback `delete` journaling,
whereas the product's private `:memory:` image reports `memory`. The primitive
now requires all of the following before binding:

- the main filename is empty;
- the main database is writable;
- `PRAGMA main.journal_mode` is exactly `memory`;
- both persistent and temporary user schema are empty.

Compiled tests construct a real anonymous temporary database with an empty
filename and prove it is rejected. They also prove that a prepopulated in-memory
database cannot acquire deployment identity after unrelated schema already
exists. This hardening lives in the primitive itself rather than relying only on
one caller to open the expected kind of connection.

### Complete role genesis before visibility

The shared `create_sealed_bootstrap_database_or_throw` helper initializes the
binding first, then constructs the selected role owner against the detached
connection:

- replica state;
- file-effect state;
- TLS membership policy state;
- TLS membership anchor state.

Each role snapshot is checked against its exact bootstrap-genesis predicate.
Only after that predicate succeeds does the helper capture a sealed SQLite
snapshot. This means the published image already contains both the common
store-set identity and the role-specific genesis contract.

TLS membership owners previously required a named durable backend because their
connection binding retains a path-family guard and checks persistent journal
policy. Rev0901 adds an explicit
`SyncReplicaTlsPolicySqliteBackendDisposition` with two values:

- `DurableNamed` for ordinary operational authority;
- `DetachedBootstrapImage` for private genesis construction.

The detached disposition accepts a filename-free writable memory-journal
connection for schema construction and snapshot reads. It is deliberately
nonoperational: membership publication and anchor advancement throw before
spending authority. Tests prove those write transitions remain unavailable.
The disposition is carried by the owner rather than inferred repeatedly from an
empty filename.

### Exact sealed image and create-new publication

`SealedSqliteSnapshot::capture_database` uses SQLite serialization to obtain the
same byte sequence that an in-memory database would write as an on-disk main
file. The existing seal already binds exact resident bytes, size and page
ceilings, process incarnation, and unchanged-state checks. Rev0901 adds a
create-new publication form that delegates to the project's immutable atomic
file publisher instead of the replacement-capable restore path.

The publisher writes private staging content, synchronizes it, installs the
final directory entry without replacing an existing destination, and
synchronizes the parent directory. The seal is reverified both before and after
publication. Unit coverage proves exact digest preservation, no SQLite sidecar
manufacture, duplicate publication refusal, and preservation of the already
published file after the failed duplicate attempt.

The earlier resource inventory remains a planning observation only. Immediately
before publication, the helper reproves the selected main pathname plus all
three sidecar names absent. A racing main or sidecar is not combined with the
sealed bytes. The final create-new transition independently refuses replacement
of a late main file.

This does not eliminate every namespace race. A process with directory-write
power can still replace ancestor or final entries between path-based checks and
subsequent opens. That requires descriptor-rooted capability work discussed
below. The correction here is narrower and still valuable: AnonSync itself no
longer creates a visible empty or half-initialized SQLite main file.

### Recovery candidate classification before SQLite authority

A present main file is not opened immediately. The bootstrap candidate preflight
first reads it through the bounded, non-symlink, single-link regular-file reader
and requires at least a complete 100-byte SQLite header with exact
`SQLite format 3\0` magic.

Header read/write versions classify the candidate:

- `1/1` is a self-contained rollback-mode image. `-journal`, `-wal`, and `-shm`
  must all be absent before SQLite is allowed to interpret the namespace.
- `2/2` is a WAL-mode image. A rollback journal is forbidden; WAL and SHM are
  permitted because they can be part of committed logical state.
- mixed or unsupported versions are rejected.

This distinction prevents a fabricated or stale sidecar from being silently
recovered, deleted, or merged into the canonical sealed genesis image merely by
opening it. For WAL candidates, sidecars remain part of the exact SQLite state
and are interpreted by SQLite under its own checks; they are not treated as
optional debris.

The open uses read-write, full-mutex, private-cache, and no-follow where
available, but never `SQLITE_OPEN_CREATE`. It proves writability, retains
exclusive locking mode, requires persistent schema, and permits only `delete`
or `wal` journal modes at the bootstrap boundary. Exact deployment binding is
attested before the handle is returned.

### Identity-first retained-handle recovery

`init-resume` intentionally has three present-store phases:

1. inventory and identity-attest every present SQLite and payload store;
2. durability-reconcile and promote retained SQLite candidates to the
   operational profile;
3. construct role owners on those same retained handles and classify genesis.

All present SQLite handles remain live across those phases. This avoids a
pathname reopen between identity proof and role-state proof and retains SQLite
locking against ordinary cooperating writers. A copied foreign effect database,
for example, is rejected before a missing replica database can be created.

For rollback-mode images, promotion pins a read transaction, reads the exact main
file, and uses immutable-file reconciliation to prove the visible bytes and
parent directory have reached the accepted durable cutpoint. Only then is the
connection promoted to WAL. The operational profile requires WAL, synchronous
FULL, a one-page automatic checkpoint threshold, foreign keys enabled, and
untrusted schema disabled. Binding is re-attested after promotion.

The exact locking claim is limited. SQLite shared/exclusive locking constrains
ordinary processes that use compatible SQLite/VFS locking. It does not stop a
rogue writer, raw block modification, broken network filesystem, alternate
locking implementation, or an actor that replaces directory entries behind the
open handle. The code and documentation keep that nonclaim explicit.

### Missing-store creation remains genesis-gated

After all present resources have been identity-attested, promoted, and
role-inspected, recovery counts missing stores. If anything is missing, every
present role and the files root must still be at bootstrap genesis. Otherwise
recomposition is refused.

Only missing stores are created, using the same private complete-image path as
fresh initialization. Existing candidate handles are released only after the
recomposition decision is final, before a second complete operational
attestation. The final manifest is published only after the full store set is
identity- and role-attested, the membership pair has been reconciled, and the
bootstrap record is re-read unchanged.

A committed final manifest remains a different authority state. Committed
`init-resume` compares exact final bytes with the record and requires a complete
identity-bound store set. It does not initialize role schema, reconcile
membership, or create missing authority stores.

## Crash and admission matrix

| Restart observation | Admission decision | Authorized transition |
|---|---|---|
| No record, no final manifest, clean selected namespace | No recovery authority exists | Fresh `init` may begin after complete freshness proof. |
| Durable record, selected SQLite main absent with no orphan sidecars | Exact future deployment is known; role is missing | Genesis-gated resume may create one complete sealed image. |
| Crash before sealed-image publication | Selected pathname remains absent | Retry creates a fresh detached image; no partial main is adopted. |
| Complete sealed rollback main, no sidecars | Canonical private image is visible | Attest identity, reconcile file+directory durability, promote to WAL. |
| Rollback main plus any `-journal`, `-wal`, or `-shm` | Namespace is not the canonical sealed image | Refuse before SQLite open or final-manifest publication. |
| WAL main plus WAL/SHM state, no rollback journal | Existing SQLite logical state may be committed | Open, identity-attest, retain, and inspect through SQLite. |
| WAL main plus rollback journal | Conflicting recovery families | Refuse. |
| Valid SQLite file without exact deployment binding | Presence does not confer authority | Refuse; never replace or initialize it in place. |
| Correctly bound wrong-role or foreign-deployment database | Record-selected identity conflicts | Refuse before any missing store creation. |
| Present exact stores at genesis and another selected store missing | Partial deployment is still recomposable | Create only missing complete genesis resources. |
| Any present resource advanced and another store missing | Operational history has escaped the common genesis cutpoint | Refuse recomposition. |
| Complete exact-bound advanced set, final manifest absent | No authority store is missing | Republish exact final manifest from record without erasing state. |
| Final manifest exists but a store is missing | Committed deployment is incomplete | Refuse; committed replay never mints replacement authority. |
| Directory sync outcome was indeterminate but exact main is visible | Bytes alone are insufficient | Reconcile exact immutable file and parent before accepting durability. |

## Audit and refactor findings

### Stale lexical audits can invert assurance

Several source audits originally searched for old enum spellings or assumed
creation lived lexically inside `command_init`. As bootstrap authority moved
behind shared helpers, those checks began flagging safe refactors while missing
new semantic boundaries. Rev0901 rewrites the relevant tripwires around the
actual graph:

- no selected SQLite path is opened with create authority;
- all four roles use one sealed complete-image creator;
- detached initialization is distinct from named attestation;
- identity precedes promotion, role ownership, and creation;
- committed replay remains identity-only;
- create-new snapshot publication is exact and no-replace;
- the detached binding primitive requires true empty memory-image semantics.

The deployment-binding audit now has 26 named checks. It remains a lexical
tripwire, not a semantic proof. The value is in maintaining a closed inventory
of reviewed authority frontiers while compiled and process tests carry runtime
obligations.

### Duplicate policy was removed from the wrong layer

The detached in-memory database used the same five-second busy timeout as named
operational databases. That timeout cannot resolve contention where no second
connection or lockable file exists. It also made the private constructor look
more like durable authority than it was. Removing it reduces policy duplication
and makes the boundary legible: contention policy belongs to named shared
databases, not a private image builder.

### Empty filename was not a sufficient detached capability

The most important late audit finding was that SQLite's empty filename is not
unique to `:memory:` databases. Anonymous temporary disk-backed databases share
that observation. The correction is intentionally semantic rather than a new
string token: the primitive requires writable MEMORY-journal state and an empty
main/temp user schema before it will install deployment identity.

This illustrates the project's core mission in miniature. “The filename is
empty” is an observation. It becomes sufficient authority only when combined
with the exact profile needed by the transition being authorized.

### Build topology remains disproportionately expensive

The clean GCC 14 Debug graph scheduled roughly 430 Ninja actions, while the full
221-test registry completes in under twenty seconds. The source ownership leaves
are useful for review, but rebuild fan-out is too broad for iterative product
work in this cloudtainer.

The recommended correction sequence is evidence-driven:

1. publish and keep a small product/bootstrap/TLS authority test lane;
2. record per-header and per-library invalidation fan-out;
3. use a measured compiler launcher such as `ccache` or `sccache` when available;
4. split libraries whose public headers pull unrelated subsystems into every
   owner;
5. consider target-scoped unity builds only after include/ODR hygiene is already
   proved by a non-unity lane;
6. keep one clean full graph and one sanitizer lane as release gates.

Global unity builds or broad test suppression would trade visible latency for
hidden coupling and are not recommended.

## Primary-source research and implications

Research was rechecked on 2026-07-26 against SQLite's primary documentation.
The links below are implementation-owner sources, not secondary tutorials.

### Serialization supports complete detached images

- https://sqlite.org/c3ref/serialize.html

SQLite documents that serialization of an in-memory database is the same byte
sequence that would be written if the database were backed by a disk file. This
supports the selected design: initialize complete genesis privately, then seal
and publish the standalone main-image bytes. It does not by itself prove the
surrounding filesystem publication or durability protocol; those remain
AnonSync obligations.

### WAL state is a file family and is not cross-database atomic

- https://sqlite.org/wal.html
- https://sqlite.org/fileformat2.html
- https://sqlite.org/tempfiles.html

SQLite documents that WAL mode is persistent, that committed changes can live
in the `-wal` file before checkpointing, and that `-shm` supports the WAL index.
It also explicitly states that transactions involving multiple attached
databases are atomic per database but not across the set in WAL mode. These
facts support treating WAL/SHM as state rather than clutter and keeping the
cross-store atomicity nonclaim.

Header read/write versions at offsets 18 and 19 distinguish rollback format
`1/1` from WAL format `2/2`. Rev0901 uses that classification only as an early
admission fence; exact schema, binding, SQLite recovery, and role attestation
remain mandatory.

### SQLite durability depends on VFS and hardware behavior

- https://sqlite.org/atomiccommit.html
- https://sqlite.org/lockingv3.html

SQLite's atomic-commit documentation is explicit about assumptions concerning
filesystem locks, sector behavior, flush semantics, deletion, controllers, and
hardware. AnonSync's synchronous mode and file/directory reconciliation are
necessary policy but cannot prove a broken VFS, filesystem, device, or power
failure domain. The release therefore avoids claiming media-level proof.

### The bundled patch level is now behind

- https://sqlite.org/
- https://sqlite.org/releaselog/3_53_4.html
- https://sqlite.org/download.html

SQLite 3.53.4 was released on 2026-07-24, one day before this work began and two
days before sealing. The release specifically fixes problems present in
3.53.0–3.53.3. AnonSync currently bundles 3.53.3 with checked hashes. Updating a
transactional dependency while simultaneously changing bootstrap cutpoints
would confound evidence, so rev0901 records the gap instead of silently swapping
the amalgamation. The next dependency revision should update to 3.53.4 in
isolation, verify the upstream source ID and SHA3-256, rebuild every SQLite
consumer, run the full registry and sanitizer lane, and repeat crash/recovery
process tests.

## What is still missing

### Descriptor-rooted deployment authority

The highest-priority local authority gap is one live deployment-root capability
that spans path validation, file publication, SQLite open, sidecar family, and
owner lifetime. Current code rejects symlinks, checks normalized absolute paths,
uses path-family guards in sensitive owners, and consults SQLite movement checks
where available, but many transitions still re-resolve pathnames.

A hostile actor with write access to ancestor directories can race those
resolutions or replace a final directory entry while an old inode remains open.
A Linux implementation should investigate `openat2` resolution constraints and
`openat`/`renameat`/`linkat` operations relative to retained directory
file descriptors. Portable implementations need reviewed component walks and
clear platform-specific nonclaims. SQLite sidecar naming and VFS opens make this
larger than replacing `std::filesystem` calls mechanically.

### Forensic bootstrap inspector and quarantine

Recovery currently accepts exact candidates or fails closed. Operators still
lack a read-only command that exports:

- exact record and final-manifest bytes;
- candidate file identity and header classification;
- sidecar inventory and bounded digests;
- deployment-binding fields;
- role-genesis/advanced classification;
- the first failed authority predicate;
- a machine-readable recommendation to resume, quarantine, or abandon.

Quarantine must itself be durable and no-replace, must never rename a live WAL
family partially, and must not turn rejection into implicit adoption. This is a
better next step than teaching resume to repair arbitrary residue.

### Cross-store transition coordination

Replica, effect, membership, anchor, payload, and visible file state have
separate persistence mechanisms. The final manifest commits their common birth,
but later business transitions are not one transaction. A production system
needs either:

- an explicit durable coordinator with idempotent prepare/commit/recovery
  records and independently attestable participant cutpoints; or
- a redesign that consolidates state requiring atomic transition into one
  database while leaving large payload bytes content-addressed outside it.

Merely attaching databases under WAL does not provide set-wide atomicity.

### Hostile-writer authentication

The deployment-binding digest is unkeyed. It detects corruption, copying, and
accidental recomposition, but an actor able to rewrite all selected stores and
the manifest can recompute it. A hostile-local-writer threat model requires a
key or signature rooted outside the writable store set, plus rotation,
revocation, rollback, and recovery semantics. That design should be separated
from transport TLS identities unless the lifecycle is deliberately unified.

### Read-only forensic status

`status` still opens write-capable operational SQLite owners, can create WAL/SHM
state, and is not a side-effect-free forensic observer. Production operations
need a bounded snapshot/export protocol that clearly distinguishes:

- live operational status with write-capable owner authority;
- quiesced consistent snapshot;
- crash-residue forensic inspection;
- untrusted raw namespace inventory.

One command should not blur those authority classes.

### Product synchronization semantics

The repository has substantial causal, storage, TLS, delivery, and crash-safety
components, but the product surface still lacks a long-running bounded
supervisor and complete filesystem semantics. Missing work includes recursive
observation, directory and rename identity, tombstones, permission/metadata
policy, chunked/resumable transfer, reachability and garbage collection,
backpressure across peers, scheduling, lifecycle management, and operator-
visible recovery.

### Privacy and anonymity

AnonSync currently provides mutual TLS and evidence-bound membership machinery,
not anonymity. There is no stated adversary model for peer identity, IP address,
timing, traffic volume, file-size leakage, directory shape, endpoint
compromise, metadata, or intersection attacks. Encryption at rest, metadata
minimization, padding, batching, cover traffic, relay design, key separation,
and deletion guarantees remain design work. Naming the project is not a
security property.

## Recommended next sequence

1. **Isolate the SQLite 3.53.4 dependency update.** Verify source identity,
   rebuild the entire SQLite graph, and rerun full/sanitized crash evidence.
2. **Design a descriptor-rooted deployment capability.** Start with a written
   authority model and one Linux prototype for main/sidecar publication and
   reopening; do not scatter ad hoc `openat` calls.
3. **Add a read-only bootstrap inspector.** Export exact machine-readable state
   without role migration, WAL promotion, or repair.
4. **Specify quarantine and abort cutpoints.** Preserve entire SQLite file
   families and exact record linkage; make every operation idempotent.
5. **Choose a cross-store coordination model.** Decide which transitions truly
   need set-wide atomicity before adding more stores.
6. **Build a bounded supervisor around the proven command spine.** Reuse exact
   owners and process tests rather than adding a second permissive path.
7. **Write the privacy/anonymity threat model before claiming that mission.**

## Validation and evidence

Rev0901 was validated in the cloudtainer with:

- GCC/G++ 14.2.0, CMake 3.31.6, and Ninja 1.12.1;
- an explicit Debug configuration;
- bundled SQLite 3.53.3 hash verification during configuration;
- a clean full build graph initially scheduling approximately 430 actions;
- complete GCC 14 Debug CTest registry: **221/221**, zero failures;
- twelve shipped-executable bootstrap/resume scenarios;
- separate GCC 14 ASan/UBSan focused lane: **4/4**, zero failures;
- deployment-binding source audit: **26/26**;
- exact create-new snapshot unit coverage;
- integrated TLS membership and anchor owner coverage;
- changed-text whitespace/newline checks and Python bytecode compilation;
- release-directory and ZIP verification after evidence sealing.

The sanitizer lane is focused, not the entire 221-test registry. No
ThreadSanitizer, formal model checker, power-cut hardware rig, hostile-kernel
proof, or multi-platform filesystem matrix is claimed.

## Bottom line

Rev0901 closes the known dead-end between SQLite pathname birth and durable
store identity without weakening fail-closed recovery. The key transition is
now “complete private image, then immutable publication,” not “create a name,
then hope initialization reaches its cutpoint.” Recovery admits exact candidates
before it creates anything new, and the detached construction APIs are narrower
than the observation “this database has no filename.”

The next largest gains will not come from adding more lexical checks. They will
come from descriptor-rooted namespace authority, explicit forensic/quarantine
workflows, an isolated SQLite patch update, and a deliberate cross-store and
privacy architecture.
