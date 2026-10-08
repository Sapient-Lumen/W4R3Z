# Product clock recovery and database-target audit, rev0897

**Assessment date:** 2026-07-25  
**Scope:** C++ owner and CLI implementation, process-level behavior, SQLite
connection ownership, product bootstrap ordering, registered source audits,
current primary-source research, and clearly labeled speculation.

## Executive judgment

AnonSync's heart remains **authority-preserving convergence**. Exact authorized
history and live owned capabilities decide what may exist, move, retry, settle,
or become visible. A clock, path string, database handle, status field, retry
counter, or process exit is useful only while it remains subordinate to the
exact authority that created it.

Rev0896 exposed durable condition but left one central operational contradiction:
the product could report that its outbox clock was quarantined, while the exact
recovery primitive existed only in the C++ owner. A deployed process could
therefore diagnose the block but could not repair it without private code or
manual database intervention. Rev0897 closes that gap with an explicit
writer-serialized probe and generation-fenced recovery command.

The audit then found a more severe product-boundary defect. Every CLI database
open inherited `SQLITE_OPEN_CREATE`, including status, send, and clock paths. A
mistyped filename could manufacture an empty authority store and make the error
look like valid genesis. Merely removing `CREATE` was not sufficient: a
pre-existing zero-byte placeholder could still be initialized by an owner, and
the unconditional `PRAGMA journal_mode=WAL` could persistently rewrite an
unrelated SQLite database before exact schema attestation rejected it.

Correcting those paths exposed another defect: SQLite usually returns a
diagnostic `sqlite3*` even when opening fails, but the product immediately
adopted it into AnonSync's strict connection-owner slot. In the cloudtainer
failure case, destruction interpreted the unadopted failed handle as an
apparently live transaction and used the owner fail-stop exit instead of the
normal command diagnostic. The revised frontier keeps every candidate in a
distinct exception-safe acquisition owner, closes failed or read-only handles
before adoption, refuses empty existing targets, observes rather than rewrites
their persistent journal mode, and only transfers a proved writable connection
into the strict owner.

This revision is therefore both a product increment and an authority audit:
clock recovery becomes invokable, observation stops creating truth, failed
handles stop acquiring ownership, and receiver bootstrap moves behind all
non-creating prerequisites.

## The mission invariant

The relevant invariant is narrower than “the database is durable” or “the
clock is monotonic”:

> A liveness or storage observation may change authority only inside the exact
> owner transaction that proves the current durable cutpoint, and a resource
> handle may enter an owner only after the acquisition result proves the
> capability the owner claims to possess.

For the outbox clock, this means:

1. sample only after `BEGIN IMMEDIATE` owns the SQLite writer serialization
   point;
2. restore and attest the exact current replica/clock state before deciding;
3. publish an accepted or quarantined observation by exact comparison against
   the previous durable clock row;
4. re-read the staged complete cutpoint before commit;
5. keep quarantine sticky during ordinary observations;
6. require recovery to name the exact current observation generation; and
7. never let a probe claim, renew, release, settle, or otherwise spend outbox
   attempt authority.

For database acquisition, this means:

1. every call site declares whether missing-file creation is authorized;
2. observational and dispatch commands require an existing, nonempty target
   already carrying the reviewed persistent WAL profile;
3. a failed `sqlite3_open_v2` result remains an unowned diagnostic handle;
4. a successful `SQLITE_OPEN_READWRITE` call is not enough, because SQLite may
   fall back to read-only;
5. only a non-null, writable `main` connection may cross into
   `SyncSqliteDbHandleSlot`; and
6. rejected candidates remain owned across diagnostic/allocation exceptions;
7. existing-only opens never change journal mode before exact owner
   attestation; and
8. commands that may create state must prove all non-creating prerequisites
   first wherever ordering can reduce orphan bootstrap.

## What changed in C++

### One clock-only owner transaction

`SyncReplicaSqliteOwner::observe_outbox_clock_or_throw()` is now public. It:

1. opens a typed `BEGIN IMMEDIATE` transaction;
2. re-proves writer authority;
3. restores the complete durable replica and clock state;
4. asks the injected clock source for one observation;
5. invokes the shared clock publication helper;
6. re-attests the complete staged cutpoint through the independent restore path;
   and
7. commits and returns the exact observation result.

The return value distinguishes `Accepted`, `Quarantined`, and
`AlreadyQuarantined`, includes the complete durable clock state, reports whether
the clock row changed, and carries a usable epoch only for an accepted
observation. Quarantine is a successful observation result, not a successful
clock. That distinction lets an operator or future supervisor learn the exact
block without weakening the normal work paths, which still commit the
quarantine and then reject the attempted lease transition.

The previous lease-specific publication code was refactored into
`publish_outbox_clock_observation_or_throw`. Both the probe and work paths now
share the pure state-machine decision, exact row update, and writer-authority
reproof. This matters more than reducing duplication: it prevents the CLI from
becoming a second implementation of clock acceptance or quarantine semantics.

### Product commands

`anonsync_replica clock-observe` accepts the same replica identity and optional
paired operator-trusted clock profile as `send-one`. It writes one flat JSON
record containing:

- selected clock profile;
- observation outcome and changed bit;
- health and anomaly;
- durable high-water epoch;
- observation and recovery generations; and
- presence of accepted and rejected observations.

A newly published quarantine returns command status zero because the command
successfully performed and reported an observation. Automation must inspect the
JSON health/outcome instead of treating “could sample” as “clock is healthy.”

`anonsync_replica clock-recover` requires a nonzero
`--expected-observation-generation`. It invokes the existing owner recovery,
which rejects healthy state, stale generations, unsynchronized observations,
excessive uncertainty, and any observation below the durable high-water epoch.
A successful recovery increments both the observation generation and recovery
generation, clears rejected/anomaly state, and binds the current observation as
a fresh cumulative-drift anchor.

The process proof executes the full sequence in separate product invocations:

1. publish an initial healthy observation under one named operator authority;
2. publish a second observation under a different authority ID;
3. verify durable `source-changed` quarantine;
4. confirm status reports the same generation and anomaly;
5. recover using exactly that generation and the final authority ID;
6. reject a repeated recovery because the clock is no longer quarantined; and
7. proceed through the existing mutual-TLS send/receive/receipt path.

### Explicit database-open disposition

Every product call to `open_database_or_throw` now supplies one of:

- `ExistingOnly`; or
- `CreateIfMissing`.

There is no default. The open helper adds `SQLITE_OPEN_CREATE` only for the
second disposition. Current call-site policy is:

| Command/surface | Store | Disposition |
|---|---|---|
| `status` | replica, optional effect, membership, anchor | existing only |
| `clock-observe` | replica | existing only |
| `clock-recover` | replica | existing only |
| `send-one` | replica | existing only |
| `enqueue-file` | replica | create if missing |
| `membership-publish` | membership, anchor | create if missing |
| `serve-one` | membership, anchor | existing only |
| `serve-one` | receiver replica, effect | create if missing |

The last three creation cases are state-minting/genesis paths, not observation
paths. They remain residual bootstrap authority and are discussed below.

`ExistingOnly` means more than “the pathname exists.” Before any owner can
initialize or migrate state, the shared open frontier requires a persistent
non-internal schema object and reads `PRAGMA main.journal_mode`. Empty files are
rejected as requiring explicit bootstrap, and any existing target not already
in WAL mode is rejected without executing the persistent journal-mode setter.
Creation-capable opens execute `PRAGMA journal_mode=WAL` only when the target
has no persistent schema, then read the mode back because assignment success
alone does not prove that SQLite selected WAL. A nonempty target must already
carry WAL even when the command has bootstrap authority; `CreateIfMissing` is
not permission to rewrite an arbitrary existing database.

### Failed handle and writable-capability fence

SQLite's official C API documentation states that a database connection handle
is usually returned even when an open error occurs, that the handle should be
closed whether or not open succeeded, and that `SQLITE_OPEN_READWRITE` can fall
back to read-only. Those details are directly relevant to an owner type whose
destructor treats an apparently active transaction as a process-integrity
failure.

Rev0897 therefore keeps the raw candidate inside a distinct
`UnadoptedSqliteConnection` acquisition owner, outside `SyncSqliteDb`, until all
of these are true:

1. `sqlite3_open_v2` returned `SQLITE_OK`;
2. the candidate is non-null; and
3. `sqlite3_db_readonly(candidate, "main")` proves writable main-database
   authority.

The candidate owner also covers exceptions while building diagnostics or
allocating the strict owner's generation state; no raw handle is temporarily
unowned between `sqlite3_open_v2` and transfer. Every explicit rejection path
closes first and then throws the command diagnostic. Only the proved candidate
is released through the strict slot's `out()` frontier. The process test
requires the normal exit code 1, no stdout, the expected SQLite diagnostic, and
absence of main/WAL/SHM files. This would fail if the old exit-86 owner fail-stop
reappeared.

Two additional negative process cases pin the distinction between pathname and
authority. A zero-byte existing file remains zero bytes and gains no WAL/SHM
sidecars. A real unrelated SQLite database begins in DELETE journal mode; after
`status` rejects it for the wrong persistent profile, the complete database
file SHA-256 remains identical and no WAL/SHM sidecars exist. The same database
is then supplied to creation-capable `membership-publish`: it remains
byte-identical and the paired anchor path is not created. Bootstrap authority
therefore applies only to a missing/schema-empty target, not to an arbitrary
nonempty SQLite store.

### Receiver bootstrap ordering

Before this audit, `serve-one` created receiver replica and effect databases
before loading TLS credentials, binding the listener, or opening the existing
membership and anchor stores. A wrong membership path or invalid TLS input could
therefore leave empty authority files behind.

The command now orders work as follows:

1. load and validate the server TLS context;
2. bind/listen and derive the listener capability;
3. open existing membership and anchor stores;
4. derive current anchored membership authority;
5. only then create/open receiver replica and effect stores; and
6. enter the one-session server owner.

A negative process proof supplies valid TLS/listener inputs but missing
membership paths, then verifies that none of the membership, anchor, receiver,
or effect database families exists after failure.

## Audit and proof added

`tools/audit_anonsync_replica_database_open_policy.py` pins the reviewed source
shape:

- one centralized `sqlite3_open_v2` call;
- explicit disposition at every call site;
- conditional and narrow `SQLITE_OPEN_CREATE` use;
- exception-safe failed/read-only closure before strict adoption;
- nonempty-schema and pre-existing-WAL requirements for existing-only opens;
- WAL assignment/readback only for schema-empty bootstrap targets;
- no-create status, clock, and sender paths;
- explicit creation only in state-minting paths;
- receiver preflight ordering; and
- corresponding process-level negative tests.

It is intentionally labeled lexical hygiene, not semantic proof. The runtime
proofs establish concrete behavior for missing paths, zero-byte placeholders,
one wrong-profile SQLite database, and receiver preflight; the owner test
establishes clock-only state transitions. They do not prove every
filesystem/VFS behavior, arbitrary valid-looking wrong databases, or malicious
same-UID interference.

The focused owner test now proves that explicit observation and recovery leave
replica evidence, policy, operations, projection, and outbox authority
unchanged. It covers:

- first accepted observation;
- idempotent identical observation;
- durable boottime-rollback quarantine;
- sticky already-quarantined behavior;
- stale recovery-generation rejection with exact rollback;
- successful exact-generation recovery; and
- repeated-recovery rejection.

## What had gone severely wrong

### 1. Observation could manufacture authority

The most serious conceptual error was not a missing flag; it was a wrong
capability default. A helper used by every command always included
`SQLITE_OPEN_CREATE`. Status, send, and clock operations thereby held genesis
authority even though their command semantics did not. A typo could turn
“observe the intended store” into “create a different empty store and observe
that.” In a system built around exact identity, that is an authority inversion.

The fix is explicit call-site disposition plus post-open capability proof, not
an `exists()` check followed by open. A separate `exists()` check would be
race-prone, would still treat a zero-byte placeholder as authority, and would
leave creation hidden inside the helper.

### 2. Failed acquisition crossed the ownership frontier

The old code passed the strict owner's output slot directly to
`sqlite3_open_v2`. That is conventional RAII for APIs that either return a valid
object or leave null. SQLite's contract is different: it usually returns a
handle even on error so callers can read diagnostics, and that handle must be
closed. The result was a diagnostic resource being mislabeled as an adopted
connection. Strict destruction then did exactly what it was designed to do for
owned transaction corruption, but at the wrong frontier.

This is a useful general lesson for the cube: **strict RAII types cannot repair
an acquisition API whose failure product has different semantics from the
owned success type.** Keep the candidate in a distinct acquisition type until
all success capabilities are proved, then transfer once. Leaving it as a naked
raw pointer is still insufficient because diagnostic string construction or
owner-state allocation can throw before the explicit close/transfer point.

### 3. Bootstrap happened before prerequisites

`serve-one` was optimized for straightforward construction order, not for
failure economics. Creating durable state first made later configuration errors
persistent litter. Reordering cannot make multiple independent SQLite stores
atomic, but it eliminates the avoidable class where no receiver state was ever
needed because TLS, binding, or trust inputs were invalid.

## Waste that remains

### Implicit product bootstrap

`enqueue-file`, `membership-publish`, and receiver genesis still authorize
creation based on command choice alone. That is better than every command
creating, but a typo in one of these state-minting commands can still create a
new store. `membership-publish` and receiver bootstrap also span two independent
SQLite files, so one successful creation followed by a second failure can leave
a partial store set.

**Recommended correction:** add an explicit `init`/`bootstrap` command that
creates all related stores, writes a deployment/store-set manifest binding
folder ID, local actor, store role, database identity, and initial cutpoint, and
refuses existing or partially initialized paths unless an exact recovery mode is
selected. Normal enqueue, membership publication, and serve commands should
then become existing-only. This is the highest-value database-target follow-up.

### Status is not a read-only contract

`status` does not create missing files or initialize an empty existing file,
but it still opens writable owners and may exercise exact legacy-schema
migration behavior on an existing nonempty database. That preserves one schema
authority, yet it means “status” is not guaranteed to be a byte-for-byte
read-only operation.

**Recommended correction:** first add an immutable exported snapshot API from
each owner; then consider a versioned read-only status path that refuses any
migration and reports `upgrade-required`. Do not implement raw read-only SQL in
the CLI, because that would duplicate private schema authority.

### No durable supervisor policy

The commands now expose enough state to distinguish no work, clock quarantine,
and recoverable clock state, but there is no durable loop deciding when to
observe, when to ask an operator for recovery, how to back off, or how to shut
down. Automatic recovery would be unsafe without a policy source: a source/boot
change may be normal deployment churn or evidence of an invalid time domain.

**Recommended correction:** build a bounded supervisor state machine with an
append-only operational intent/receipt log. It should never recover merely
because time passed. Recovery should require an explicit policy capability that
names the current quarantine generation, acceptable clock profile, and reason.

### Build and evidence overhead

This source increment touches a small product boundary, but a full release still
pays for hundreds of targets and a large historical evidence corpus. Lexical
audits are valuable as tripwires but add maintenance cost and can confuse source
shape with semantics.

**Recommended correction:** keep runtime/process proofs as the primary claim,
consolidate overlapping source audits, move large historical raw logs outside
the distributable archive by digest, and restructure CMake around cohesive
components rather than both giant translation units and one-file micro-libraries.

### Privacy remains a name, not a property

Clock recovery and database targeting improve integrity and operability. They do
not hide endpoints, peer graph, folder interest, path names, payload sizes,
timing, or traffic shape. Mutual TLS with SPKI/actor authorization is not
anonymity.

**Recommended correction:** define the privacy threat model before choosing a
mechanism. Keep private-interest negotiation and routing outside the causal
kernel, then admit only an immutable capability-derived projection into the
existing authority paths.

## Current research observations

Primary sources checked during this revision:

- SQLite C API, opening a connection:
  `https://www.sqlite.org/c3ref/open.html`
- SQLite download page:
  `https://sqlite.org/download.html`
- SQLite project home/latest release:
  `https://sqlite.org/`

The API documentation directly supports the failed-handle correction: a handle
is usually returned on open error and must be closed, and read-write open may
fall back to read-only. The official project pages reported SQLite 3.53.4 as the
latest release, dated 2026-07-24. The download page listed
`sqlite-amalgamation-3530400.zip` with SHA3-256
`628a44cfe82c66aed1ccbbe85a562d2e33ebe64b3288981ed76285612227934e`.

This cloudtainer could inspect the official metadata but could not acquire and
independently verify the ZIP bytes through the available download paths. The
source tree therefore remains pinned to its verified bundled SQLite 3.53.3.
Rev0897 does not claim a 3.53.4 migration. Substituting unverified bytes merely
to report a newer version would contradict the mission.

## Recommended next sequence

1. **Explicit store-set bootstrap.** Remove remaining implicit creation from
   normal product commands and bind all store roles in a deployment manifest.
2. **Bounded supervisor.** Use status, clock observation, exact recovery,
   payload availability, and membership condition to drive one restart-safe
   transition at a time.
3. **Read-only/versioned condition API.** Separate observation from migration
   while preserving owners as the only schema authority.
4. **Causal directory/tombstone/rename semantics.** The current file-only leaf
   path is insufficient for a synchronization product and still requires parent
   directories to preexist.
5. **Reachability and garbage collection.** Retained payloads and evidence need
   exact liveness roots before any deletion is authorized.
6. **Indexed acceleration with oracle comparison.** Add scalable lookup only
   behind retained full-scan equivalence proofs.
7. **Verified SQLite 3.53.4 acquisition.** Upgrade only after exact official
   source bytes and hashes can be sealed in the same release process.
8. **Privacy threat model and capability overlap.** Do not attach anonymity
   claims to authenticated transport alone.

## Nonclaims

Rev0897 does not claim automatic trustworthy time recovery, clock attestation,
multi-store atomic bootstrap, a daemon, discovery, NAT traversal, directory or
tombstone convergence, chunking/resume, reachability/GC, at-rest encryption,
malicious same-UID resistance, a read-only status contract, anonymity,
unlinkability, endpoint hiding, or traffic-analysis resistance. It claims a
smaller and testable improvement: exact clock health and recovery are now
product operations, and database acquisition no longer silently gains creation
or ownership authority on observational and failure paths.
