# Explicit store-set bootstrap and manifest authority audit, rev0898

**Assessment date:** 2026-07-25  
**Scope:** C++ product-spine bootstrap, deployment configuration authority,
SQLite and payload-store creation policy, exact JSON admission, process-level
failure behavior, source-audit maintenance, build-graph cost, primary-source
research, and explicitly labeled design speculation.

## Executive judgment

The heart of AnonSync is not file transfer, a database, or even replication in
isolation. It is:

> **durable, bounded causal convergence in which authority is explicit,
> evidence-bound, recoverable, and never fabricated by observation.**

Exact authorized history and live owned capabilities decide what may exist,
move, retry, settle, or become visible. Paths, clocks, handles, summaries,
indexes, process exits, and configuration files are evidence only while they
remain subordinate to the exact authority that created them.

Rev0897 corrected a severe database-open inversion: status, send, and clock
commands could no longer turn a missing or unrelated SQLite path into apparent
genesis. That correction was incomplete at the product boundary. Normal work
commands still carried pieces of bootstrap authority, and the durable payload
store still had no explicit open disposition. Merely pointing `status`,
`enqueue-file`, or `send-one` at an empty payload directory could publish the
folder identity marker and thereby manufacture a durable namespace. Meanwhile,
`enqueue-file`, `membership-publish`, and receiver startup still accepted a
collection of independently mixable paths and could create some of them.

The first manifest design examined during this revision was also insufficient.
It described a store set, but commands could still reconstruct their authority
from raw `--replica-db`, `--payload-root`, `--folder`, and actor arguments. A
manifest that can be bypassed is documentation, not an operational capability.
That design was rejected rather than shipped.

Rev0898 makes `anonsync_replica init` the sole product-spine bootstrap frontier.
It validates and encodes one immutable deployment manifest before store
mutation, prepares the create-new manifest pathname, initializes the selected
stores, and publishes the manifest last. Every operational command accepts the
manifest as its only local store-set configuration source, verifies its exact
canonical bytes and self-digest before opening a store, derives all paths and
local identity from it, and uses existing-only database and payload opens.

This is a meaningful authority correction, but it is not a cross-resource
transaction and it is not yet a complete deployment identity. The manifest
binds configuration and a committed operational cutpoint. It does **not** yet
prove that every selected store was born as part of the same deployment, and it
does not solve interrupted-bootstrap inspection or recovery. Those are the two
highest-priority remaining gaps.

## The corrected authority inversion

### Before rev0898

The product had several independent ways to create durable authority:

1. `enqueue-file` could initialize a missing replica database.
2. `membership-publish` could initialize membership and anchor databases.
3. `serve-one` could initialize receiver and effect databases after preflight.
4. payload-store construction could create the folder identity marker when it
   saw an otherwise admissible directory.
5. each command accepted folder, actor, payload ceiling, and store paths
   independently, so a caller could accidentally compose stores from different
   deployments.

The fact that creation was explicit at some C++ call sites did not make it
operator-explicit as a product operation. A work command still combined two
conceptually different capabilities: “perform this bounded operation” and
“mint whatever durable stores are missing.” This is dangerous because typo
paths, stale service configuration, and partial command lines can become valid
new state rather than a refusal.

### After rev0898

The product surface now has one creation-capable command:

```text
anonsync_replica init --manifest ... --replica-db ... --folder ... \
  --local-device ... --local-epoch ... [selected store options]
```

All normal commands require `--manifest` and reject the old local-identity and
store-path options:

```text
status
clock-observe
clock-recover
enqueue-file
membership-publish
send-one
serve-one
```

This is not merely a command-line cleanup. The C++ call graph enforces two
separate policies:

- every operational SQLite open is `DatabaseOpenDisposition::ExistingOnly`;
- every operational payload open is
  `SyncReplicaFilePayloadStoreOpenDisposition::ExistingOnly`.

Only `init` passes `CreateIfMissing`. The payload disposition is deliberately
non-defaulted, so new call sites cannot silently inherit creation authority.

## Bootstrap cutpoint

`init` has three conceptual phases.

### 1. Admission before mutation

The command first constructs the complete `SyncReplicaDeploymentManifest` and
validates:

- absolute, lexically normalized paths;
- paired effect database/files root and membership database/anchor database;
- lowercase portable folder and device identifiers;
- positive actor epoch within the exact interoperable JSON integer range;
- payload ceiling in `[1, 67108864]`;
- no exact duplicate file paths;
- no lexical overlap between payload and effect roots; and
- no selected database or manifest file lexically inside either selected root.

It then encodes the exact manifest, calculates its domain-separated SHA-256
self-digest, proves that the encoded document fits the reader's 16 KiB ceiling,
and reparses the exact writer output with the strict UTF-8 JSON parser. That
last check matters on POSIX: a filesystem path may contain arbitrary non-NUL
bytes, while the operational reader accepts only strict UTF-8 JSON. Without
writer-side admission, `init` could create every store and publish a manifest
that no later command could read.

The immutable final manifest name is prepared with create-new semantics before
any selected store is opened. Preparation retains the destination-parent
authority and proves the final entry absent, but creates no temporary or final
file at that point.

### 2. Individually durable store initialization

`init` opens or initializes the selected authorities through their existing
owners:

- the causal replica SQLite owner;
- the durable file-payload store;
- the receiver file-effect SQLite owner; and
- the membership plus independent anchor SQLite owners and coordinator.

This preserves each owner's schema, connection-profile, path-family, and
reconstruction checks. `init` does not bypass those owners with raw SQL or
marker writes.

### 3. Manifest publication last

Only after all selected owners have restored successfully does the prepared
immutable JSON publication create and durably publish the manifest. Its absence
therefore means the store set never reached the product's committed operational
cutpoint.

The manifest truthfully contains:

```json
"manifest_is_store_set_commit_marker": true,
"cross_resource_atomicity": false
```

That distinction is essential. A crash before publication can leave one or more
valid stores. A crash during final publication can also require filesystem-level
reconciliation according to the atomic-publication outcome. The manifest is a
last-published commit marker, not a rollback mechanism for earlier stores.

## Manifest as an operational capability

The deployment manifest has an exact 22-field schema. It binds:

- its own absolute opened pathname;
- profile and selected-resource count;
- folder and local actor;
- payload ceiling;
- replica, payload, effect, files, membership, and anchor paths;
- required WAL profile;
- existing-only operational database policy;
- existing-only operational payload policy;
- deployment-manifest-only configuration policy;
- required-manifest and commit-marker declarations;
- explicit denial of cross-resource atomicity; and
- a domain-separated SHA-256 digest of the unsigned canonical document.

The reader performs a bounded, final-component-no-symlink regular-file read and
then rejects:

- malformed JSON or UTF-8;
- duplicate keys;
- missing or unknown fields;
- unsupported formats or policies;
- noncanonical paths;
- copied bytes whose embedded `manifest_path` does not equal the opened name;
- profile or resource-count contradictions;
- malformed digest text;
- whitespace, field-order, escape, number, or other byte-level
  noncanonicality; and
- any self-digest conflict.

The reader re-encodes the parsed value and requires byte-for-byte equality with
the opened file. The manifest digest is included in every operational JSON
result, allowing logs and a future supervisor to name the exact configuration
cutpoint used for that operation.

The self-digest is an integrity and identity mechanism, not a signature. A
writer already authorized to replace the deployment's files can construct a
new valid manifest. Rev0898 makes the local product fail closed against
accidental copying, mixing, corruption, and unsupported policy; it does not
claim defense against a hostile same-UID or privileged writer.

## Durable payload-store correction

The payload store previously had one constructor behavior: reconcile the
identity marker, and if it was missing, validate the namespace and publish it.
That was useful for bootstrap but wrong for status and dispatch. Observation of
an empty typo directory could mint a durable folder identity even after all
SQLite opens had been fenced.

`SyncReplicaFilePayloadStoreOpenDisposition` now has two explicit values:

- `ExistingOnly`; and
- `CreateIfMissing`.

With `ExistingOnly`, an absent identity marker fails before namespace adoption
or publication. With `CreateIfMissing`, the existing bootstrap behavior remains
fail-closed: the entire pre-existing digest namespace is scanned and validated
before the marker may be created. Tests cover empty directories, valid
pre-existing payload adoption, unknown and malformed entries, link rejection,
budget overflow, and the absence of marker mutation on failed operational
opens.

This closes an important conceptual hole: a read or work path can no longer
create either a SQLite authority or a payload namespace authority.

## JSON parser extraction and refactor

The manifest must be a narrow authority leaf. Initially, strict JSON parsing
lived privately inside `json_codec_crypto.cpp`, which is part of the broad core
codec aggregation. Reusing that implementation directly would have made a
16 KiB deployment document depend on unrelated crypto, policy, report, and
runtime machinery, or would have encouraged a second parser.

Rev0898 extracts the existing strict parser into:

- `include/anonsync_json_parser.hpp`; and
- `src/anonsync_json_parser.cpp`.

Both the broad runtime codec and the manifest codec now consume the same parser.
The parser rejects duplicate keys, malformed Unicode and raw UTF-8, non-finite
or malformed numbers, trailing content, unescaped controls, and nesting beyond
its owned ceiling. CMake keeps it as a dependency-light static leaf and source
inventories prevent it from being reabsorbed into the large core source list.

This refactor also exposed source-audit brittleness. The bounded-regular-file
audit intentionally inventories every production consumer. Adding the manifest
reader made that exact inventory fail while 216 runtime and structural tests
passed. The audit was updated—not bypassed—to include the manifest as an
intentional consumer, and its format advanced to v3. The final registry passes
217/217.

## Process proof

The process test is now a bootstrap and operational-authority proof, not only a
happy-path transport test. It launches real subprocesses and covers at least the
following cutpoints.

### Before any store may be created

- `status` without a manifest fails.
- `enqueue-file` without a manifest fails.
- a wrong-profile `init` aimed at an unrelated nonempty DELETE-mode SQLite file
  leaves its bytes unchanged and publishes no manifest;
- overlapping selected paths are rejected before mutation;
- a pre-existing manifest collision prevents fresh store creation; and
- malformed writer inputs, including over-ceiling and non-UTF-8 manifest
  encodings, fail in the encoder before bootstrap mutation.

### Manifest authority

- sender and receiver manifests have exact canonical bytes, mode, self-digest,
  profile, resource count, and policy fields;
- copied manifest bytes fail because the embedded path does not bind the opened
  name;
- same-path tampering fails before store access;
- raw path or local-identity options are rejected by operational grammar;
- a manifest paired with a detached or missing replica database does not
  recreate it;
- a valid sender manifest aimed at an empty replacement payload directory
  cannot mint a marker through status, enqueue, or send; and
- command/profile mismatches fail before unrelated stores are opened.

### Receiver ordering and transport

- detached membership authority prevents `serve-one` before receiver/effect
  access;
- anchored membership publication and update remain exact;
- enqueue, status, clock observation, quarantine, and generation-fenced
  recovery remain functional through the manifest-bound surface;
- a real mutual-TLS sender/receiver conversation publishes exact file bytes;
- the authenticated receipt settles the sender's durable attempt; and
- every operational result names the exact deployment-manifest digest.

## What has gone severely wrong, and what this revision corrected

### 1. Observation had genesis authority

The most serious recurring defect was an authority inversion: status, send, or
other ordinary operations could manufacture durable state from path strings.
Rev0897 fixed SQLite observation; rev0898 completes the product-spine correction
for all operational SQLite and payload opens.

### 2. Bootstrap authority was distributed across work commands

Creation policy was explicit in C++ but still distributed through commands whose
primary purpose was enqueueing, membership mutation, or serving. Rev0898 makes
bootstrap a named operator action and strips creation authority from ordinary
work.

### 3. The first manifest was descriptive rather than authoritative

A configuration file that commands may bypass or mix with raw path arguments
does not define a store set. The shipped design requires the manifest and removes
those independently mixable arguments from operational grammar.

### 4. The writer initially did not prove its reader contract

A canonical writer can still strand a deployment when it emits more bytes than
the reader accepts or copies filesystem bytes that violate the parser's Unicode
contract. Both conditions are now checked before any selected store is created.

### 5. Exact source audits can become stale through legitimate refactors

The full suite caught the new manifest reader as an unrecognized bounded-file
consumer. The right correction was to update the exact inventory and its
narrative, not weaken the audit to “some consumer exists.”

## What remains missing

### P0: store-internal deployment identity

The manifest binds a set of paths and configuration values, but the selected
stores do not all embed one immutable deployment/store-set identifier. A caller
can create a new canonical manifest over independently valid stores that happen
to accept the same folder and local actor. Existing schema-owner and path-family
checks catch many wrong-role and namespace errors, but they do not prove common
birth.

The next design should mint a random or collision-resistant `deployment_id`
during bootstrap and persist it in:

- a dedicated owner-attested row in every SQLite store;
- the payload identity marker;
- an effect-files-root identity marker; and
- the deployment manifest.

Every owner should require the exact identifier at construction and include it
in its durable cutpoint digest. This would turn the manifest from a path-bound
configuration capability into a store-internally attested composition
capability.

### P0: interrupted-init inspection and recovery

Publishing last makes noncommit visible, but it does not tell an operator which
stores were created before interruption, whether they are safe to resume, or
whether a concurrent initializer raced. A robust product needs an explicit
bootstrap state machine, for example:

```text
init prepare
init inspect
init resume
init abort
```

A small create-new bootstrap journal could name a generation, exact requested
configuration, per-store prepared/verified cutpoints, and final committed or
aborted outcome. The design must remain honest that SQLite databases and
filesystem roots cannot be rolled back as one transaction. “Abort” may mean
quarantine and operator-directed cleanup, not magical restoration.

### P1: descriptor-rooted namespace authority

The manifest reader refuses a symbolic link in the final component, and many
store owners have stronger path-family guards. The manifest and command sequence
still re-resolve path strings, so symbolic-link ancestors, bind mounts, mount
changes, and path rebinding between checks remain possible according to the
host threat model.

On Linux, a future service launcher should consider opening one trusted root and
resolving all descendants with `openat2(2)` policies such as
`RESOLVE_NO_SYMLINKS`, with carefully reviewed use of `RESOLVE_BENEATH`,
`RESOLVE_IN_ROOT`, and possibly `RESOLVE_NO_XDEV`. The application should retain
and pass directory descriptors instead of repeatedly treating absolute strings
as authority. Cross-platform equivalents need separate designs; Linux-only
semantics must not be generalized.

### P1: role-specific SQLite file identity

SQLite's file header provides `PRAGMA application_id`, intended to identify an
application file format. AnonSync should evaluate distinct nonzero application
IDs for replica, effect, membership, and anchor stores, combined with the
store-set identifier and current exact schema attestation. The header value
would be an early wrong-file rejection, not a replacement for schema ownership,
connection policy, or cryptographic/durable cutpoint checks.

### P1: status without write-capable WAL side effects

`status` no longer creates a missing database, but it still uses the owning
write-capable WAL connection because the owner reconstruction and profile checks
are designed around that authority. SQLite WAL uses `-wal` and `-shm` sidecars
and a status invocation can therefore participate in mutable runtime database
state. A future read-only operational export should be designed explicitly,
perhaps through a separately published bounded status document or a
read-transaction profile that proves it can satisfy all owner invariants without
claiming writer authority. Simply adding `immutable=1` would be unsafe for a
live WAL database and is not recommended here.

### P1: continuous supervised operation

The product remains a set of one-shot commands. It has no bounded scheduler,
restart policy, readiness protocol, backoff owner, peer discovery, or policy
engine for clock recovery. The deployment manifest is now a suitable capability
for a supervisor to consume, but the supervisor must not infer authority from
exit codes alone. It should read exact command results, retain manifest digest,
apply bounded retry policy, distinguish quarantine from empty work, and require
explicit operator/policy authority for recovery.

A service manager can own directories, process restart, and privilege
boundaries, while AnonSync continues to own causal and store authority.
`StateDirectory=`/`RuntimeDirectory=` and service restart/readiness semantics
are relevant deployment primitives, not substitutes for application-level
cutpoints.

### P1: cross-store commit protocol

SQLite documents that WAL is a same-host mechanism and that transactions over
multiple attached databases are not atomic as a set when WAL is involved. The
current separate owners are therefore correct not to claim cross-database
atomicity. Future operations that need one logical store-set transition require
an explicit coordinator/recovery journal or a redesigned single-database
schema. Attaching the files and calling one SQL transaction while retaining WAL
would not satisfy the claimed invariant.

### P2: build and test development lane

The final clean GCC 14 Debug closure scheduled 297 Ninja actions and registered
217 tests. That is valid release evidence, but it is expensive feedback for a
narrow product-spine change. The measurement does not by itself prove that a
specific target edge is wrong; the build was broad by design and some early
invocations were command-time-limited rather than compiler-failing.

A measured optimization program should separate:

1. a fast target-scoped product lane (`anonsync_replica`, manifest/payload
   tests, process proof, and authority audits);
2. an incremental integration lane;
3. the complete release registry; and
4. sanitizer/platform lanes.

Developer-controlled CMake compiler launchers can integrate `ccache` or a
compatible cache when available. CMake unity builds can reduce compilation
units but carry one-definition-rule and translation-unit-interaction risk; they
should be an opt-in experiment, never silently enabled for the invariant-heavy
release lane. Ninja compile pools can cap memory pressure but do not reduce the
amount of work. Before changing the graph, capture `.ninja_log`, compiler trace,
and target dependency data so optimization addresses measured compile/link
cost rather than target-count aesthetics.

### P2 and beyond: product semantics and privacy

The deployment correction does not add:

- causal directories, tombstones, rename, or symlink semantics;
- reachability analysis or garbage collection;
- chunking, streaming, or resume;
- indexed production-scale restore/query paths;
- at-rest encryption or key lifecycle;
- discovery, NAT traversal, or multi-peer scheduling;
- private-interest overlap;
- unlinkability, endpoint hiding, or traffic-analysis resistance; or
- a formal proof or hostile same-UID/privileged-writer defense.

Mutual TLS authenticates the configured peer key and protects one transport
conversation. It does not make the system anonymous despite the project name.
A real privacy claim requires an explicit adversary model and network design.

## Recommended sequence

1. **Persist one deployment identifier in every selected authority.** Make owner
   construction require it and make every status/transport result bind it.
2. **Add bootstrap inspect/resume/quarantine semantics.** Prove exact generation
   and store cutpoints; do not promise rollback that the resources cannot
   provide.
3. **Move service operation to descriptor-rooted namespaces.** Start with Linux
   `openat2` experiments behind a platform-specific capability type.
4. **Add role-specific SQLite `application_id` values.** Treat them as an early
   format discriminator layered beneath exact schema and deployment checks.
5. **Build a bounded supervisor around the manifest.** Keep clock recovery and
   destructive/repair actions policy-explicit.
6. **Design the causal filesystem model before broadening file operations.** A
   daemon that retries incomplete semantics faster is not mission progress.
7. **Profile the build graph and add a documented fast lane.** Preserve the full
   release registry as the final gate.
8. **Write the privacy threat model before using anonymity language as a
   property claim.**

## Primary sources reviewed

Reviewed on 2026-07-25. These sources support the constraints and candidate
mechanisms above; they do not constitute endorsement of the speculative design.

- SQLite write-ahead logging, including same-host limitations, sidecars, and
  multi-database atomicity caveats: <https://www.sqlite.org/wal.html>
- SQLite `ATTACH DATABASE`, including the WAL multi-file transaction caveat:
  <https://sqlite.org/lang_attach.html>
- SQLite file format and `application_id` header field:
  <https://www.sqlite.org/fileformat.html>
- Linux `openat2(2)` resolution policies:
  <https://man7.org/linux/man-pages/man2/openat2.2.html>
- systemd execution directory and privilege/lifecycle facilities:
  <https://www.freedesktop.org/software/systemd/man/systemd.exec.html>
- systemd service restart and process-lifecycle semantics:
  <https://www.freedesktop.org/software/systemd/man/systemd.service.html>
- CMake developer-controlled unity builds and their ODR cautions:
  <https://cmake.org/cmake/help/latest/prop_tgt/UNITY_BUILD.html>
- CMake compiler-launcher integration for tools such as `ccache`:
  <https://cmake.org/cmake/help/latest/variable/CMAKE_LANG_COMPILER_LAUNCHER.html>
- CMake/Ninja compile job pools:
  <https://cmake.org/cmake/help/latest/prop_tgt/JOB_POOL_COMPILE.html>

## Validation summary

The final rev0898 source tree has been validated with:

- a complete GCC 14 Debug build with bundled SQLite;
- 217/217 registered CTest tests;
- the manifest codec unit test, including copied/tampered/noncanonical,
  over-ceiling, malformed UTF-8, overlap, symlink, exact-integer, and exact-byte
  cases;
- the real process-spine bootstrap, manifest, clock, mutual-TLS, publication,
  receipt, and settlement proof;
- the database-open policy audit;
- the bootstrap-authority audit; and
- the revised bounded-regular-file exact-consumer audit.

Passing these proofs establishes the implemented contracts on the tested Linux
cloudtainer and compiler configuration. It is not a formal proof, a
cross-platform runtime result, or evidence for unusual/network filesystem
semantics.
