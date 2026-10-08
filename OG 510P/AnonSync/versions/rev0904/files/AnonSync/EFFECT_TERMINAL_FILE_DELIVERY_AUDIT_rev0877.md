# AnonSync rev0877 — effect-terminal immutable-file delivery, restart reconciliation, and cube audit

## Executive finding

AnonSync's heart is **authority accounting under crash, partial trust,
duplication, reordering, resource pressure, and ambiguous response**. It is not
fundamentally a file copier. The project is trying to make every identity,
causal edge, projection decision, dispatch attempt, retained payload, receiver
admission, visible effect, retry, and sender settlement attributable to exact
bounded evidence and an explicit durable transition.

Rev0876 established authenticated operation-evidence delivery, but its terminal
receipt stopped at receiver retention. That was honest and useful, yet it left
the most user-visible authority gap open: the sender could know an operation was
retained without knowing that the exact bytes were durably published at the
canonical destination.

Rev0877 builds the first production-source **effect-terminal** slice for one
operation class:

`durable File outbox intent → claim/attempt identity → canonical operation plus`
`exact payload → authenticated channel binding → durable payload stage → causal`
`admission → active-primary projection → immutable create-new namespace effect →`
`file durability → directory durability → receiver effect cutpoint → terminal`
`receipt → exact sender settlement`

This is the first revision in the newer causal-owner line that reaches a visible
file. It is still deliberately narrow. It does not implement ordinary file
updates, deletion, a stable root capability, hostile-peer staging quotas,
content-addressed storage, signed offline receipts, or a shipped service.

The most important engineering result is not the new message type. It is the
explicit treatment of the filesystem and SQLite as **independent durable
systems**. Rev0877 does not pretend a rename and a database commit are one atomic
transaction. It instead uses immutable no-replace publication, exact restart
reconciliation, durable state monotonicity, and retry idempotency.

## Mission invariant

The project remains coherent when expressed as one invariant:

> Given the same authorized canonical evidence and trust state, independent
> replicas must derive the same state; no untrusted bytes, missing dependency,
> stale receipt, clock movement, duplicate, crash frontier, schema mutation,
> namespace race, resource-pressure decision, retry response, or summary may
> silently manufacture authority.

That invariant implies several design rules visible in rev0877:

- operation identity is derived from canonical bytes, not a path or mutable row;
- payload bytes are checked against the operation's size and content digest;
- payload retention, causal admission, projection, filesystem publication, and
  sender settlement are different authority transitions;
- a frame digest is structural identity, not peer authentication;
- a TLS session authenticates a live exchange, not an archival receipt forever;
- byte equality is not enough to claim a private immutable filesystem effect;
- an ambiguous syscall result is reconciled, not guessed;
- a sender receipt is terminal only when the receiver effect state and exact
  durable file agree; and
- any contradiction after a durable `Published` row fails closed rather than
  silently repairing the file from potentially stale policy.

## What rev0877 adds

### Separate receiver effect ownership

`SyncReplicaFileEffectSqliteOwner` owns receiver payload/effect state in a
separate SQLite database. The separation is intentional. The causal owner
answers “is this operation exact, retained, authorized, dependency-complete, and
active?” The effect owner answers “do I retain the exact payload and has the
exact immutable destination effect been durably observed?”

Its strict schema persists:

- folder and normalized root-path text;
- all canonical operation decoding limits;
- maximum effect count, per-payload bytes, and aggregate retained payload bytes;
- state generation and aggregate counters;
- canonical operation bytes and exact payload bytes;
- redundant path, content digest, size, state, and transition generations;
- structural effect ID and publication digest;
- effect-set digest and complete cutpoint digest; and
- a state index for operational lookup.

Every open, snapshot, stage, and publication transition reads the exact
`sqlite_schema`, reconstructs every operation from canonical bytes, recomputes
payload hashes, effect IDs, aggregate counters, state history, set digest, and
cutpoint digest, and rejects disagreement.

This owner is intentionally an O(history) correctness oracle. That is valuable
for migrations, repair, fuzzing, and differential testing. It is not a scalable
production design for large folders.

### Durable staging before causal admission

The receiver stages the exact payload before it asks the causal owner to admit
the operation. This prevents a dangerous state where evidence is accepted and a
receipt is constructed although the receiver never retained the bytes required
to realize the effect.

The cost is equally explicit: a structurally valid, authenticated operation that
is later quarantined or remains dependency-pending can consume effect capacity.
Without per-peer quotas, retention expiry, and garbage collection, a hostile or
misconfigured peer can fill staging storage. Rev0877 limits aggregate bytes but
does not yet provide fair-share or reclaim policy.

A safer production evolution is likely:

1. bounded temporary ingress validation;
2. peer/folder quota reservation;
3. exact durable stage;
4. causal admission and policy classification;
5. promotion into retained object/effect authority; and
6. expiry or dead-letter authority for nonpromoted stages.

### Immutable create-new publication

The first effect policy is intentionally simple: one operation may create one
previously absent canonical path. It never replaces an existing entry.

This makes crash reconciliation tractable:

- absent means publication may be attempted;
- exact durable file means publication already succeeded or another exact
  writer won;
- any other existing entry is a destination conflict and is preserved.

Normal synchronization requires updates and deletion, so this is not a product-
complete file policy. It is a correctness scaffold for effect ownership.

### Canonical file delivery protocol

`SyncReplicaFileDeliveryProtocol` wraps the rev0876 evidence request with exact
payload bytes. Version 1 rejects tombstones. The receipt binds:

- folder and sender/receiver actor epochs;
- operation ID;
- claim ID and dispatch attempt;
- request frame digest;
- authenticated channel binding;
- one explicit disposition;
- the inner evidence receipt where evidence admission occurred;
- structural effect ID;
- receiver effect generation; and
- receiver effect cutpoint digest.

Only `Published` and `AlreadyPublished` are effect-terminal. The remaining
states are deliberately nonterminal:

- `EffectCapacityBlocked` — payload staging did not acquire authority;
- `EvidenceCapacityBlocked` — payload was staged but causal retention could not
  be admitted;
- `EvidencePending` — dependencies are missing;
- `EvidenceQuarantined` — trust/policy validation rejects active authority;
- `ProjectionBlocked` — retained evidence does not own the active path; and
- `DestinationConflict` — active evidence exists but create-new filesystem
  policy cannot realize it without replacing an entry.

The public request/receipt digest now equals the canonical frame seal. An early
draft hashed that seal again, producing two identities for the same bytes
without adding authentication. The double hash was removed.

### File-only outbox claim filtering

The general outbox may contain file and tombstone operations. A file service
that claims the next arbitrary intent can lease a tombstone and then discover it
has no deletion protocol, consuming liveness authority on work it cannot finish.

`claim_next_outbox_or_throw()` now accepts an optional exact operation-kind
filter. It resolves each candidate against canonical evidence and skips
mismatches. Existing callers remain source-compatible. The file delivery
service asks only for `SyncReplicaValueKind::File`, leaving tombstone intents
live for a future deletion owner.

## Filesystem authority audit

### Why exact bytes were insufficient

The first reconciliation draft accepted a stable regular file with exact bytes.
That was too weak for a project whose eventual mission includes privacy:

- a byte-identical file with mode 0644 leaks content to other local users;
- a hard-linked file has another namespace identity that can outlive or mutate
  outside the intended destination policy;
- a file owned by another UID is not a writer-owned private effect even if its
  current bytes match; and
- creation mode alone is affected by `umask`, so requesting 0600 does not prove
  the final mode remained exactly 0600 under all caller environments.

Rev0877 requires same-owner UID, exact mode 0600, and link count one. The
publisher calls `fchmod` on the exact writer-owned inode before publication, then
revalidates that inode.

The Linux `open(2)` documentation states that a newly created file is owned by
the process effective UID and that the effective mode is modified by the
process `umask`. It also states that `O_NOFOLLOW` protects the trailing component
only, which is why AnonSync opens and validates every parent component rather
than relying on one final `open()` flag:

- https://man7.org/linux/man-pages/man2/open.2.html

### File durability is not directory durability

A successful file `fsync` does not necessarily make the containing directory
entry durable. Linux explicitly requires an `fsync` on the directory descriptor
for that boundary:

- https://man7.org/linux/man-pages/man2/fsync.2.html

The reconciliation result `ExactAndDirectorySynced` therefore means:

1. resolve the parent path component-by-component without following symlinks;
2. inspect the final entry with `AT_SYMLINK_NOFOLLOW`;
3. open it with `O_NOFOLLOW`;
4. prove stable file identity and bounded exact bytes;
5. prove same owner, mode 0600, and link count one;
6. synchronize the file;
7. synchronize the exact parent directory; and
8. re-prove both file and parent identities afterward.

An I/O or identity failure throws. It is not collapsed into “absent” or
“conflict,” because either label could grant incorrect retry authority.

### Atomic no-replace namespace transition

Linux `renameat2(..., RENAME_NOREPLACE)` atomically refuses to overwrite an
existing destination, but support depends on the underlying filesystem. The
implementation treats unsupported or ambiguous behavior as failure and relies
on exact reconciliation rather than assuming a failed call implies no rename:

- https://man7.org/linux/man-pages/man2/rename.2.html

The same manual page warns that on NFS an operation may be completed by the
server and still appear failed after retransmission. That reinforces the design:
return codes are observations, not complete effect authority; reconciliation is
required after ambiguity.

### Windows boundary

The current Windows implementation can inspect exact bytes and flush a file
handle but does not prove the parent-directory durability semantics required by
this state machine. It throws instead of returning
`ExactAndDirectorySynced`. This is a deliberate fail-closed portability boundary,
not a claim that Windows cannot support such a protocol with platform-specific
work.

### Root identity remains weak

The effect owner persists an absolute lexically normalized root path as text.
Each publication uses no-symlink traversal, but the owner does not retain or
persist a stable directory identity/capability across calls. A local actor can
replace the root pathname with another same-type directory between operations
and redirect future effects.

This is the highest-priority filesystem authority gap. Plausible corrections:

- retain an open root directory descriptor for the owner lifetime and resolve
  every canonical path relative to it;
- persist root device/inode plus a root epoch and fail closed on reopen mismatch;
- use an administrator-authorized root-rebind transition rather than silently
  accepting a same-text replacement; or
- put immutable objects in an owner-controlled object directory and make
  visible paths a separately versioned projection.

A process-lifetime descriptor alone does not solve restart; a persisted identity
alone does not prevent replacement after reopen. The complete design needs both
runtime capability and restart epoch policy.

## SQLite authority audit

### Exact generation history

The first schema bounded generations and required them not to exceed the meta
state generation, but that allowed histories with duplicate or missing
transition numbers. Such a database could preserve aggregate counts while no
longer representing the exact writer transition sequence.

Restore now gathers every stage and publication generation, requires the number
of transitions to equal `state_generation`, sorts them, and requires exact
values `1..state_generation`. A publication generation must be strictly later
than its own stage generation. Duplicate, gap, equal stage/publication, or
impossible aggregate histories fail closed.

This is a useful general rule for the cube: where a generation is claimed to be
an append-only transition count, prove the retained events form the exact
history the writer emits. Merely bounding each value is not enough.

### One database writer does not create a cross-database transaction

SQLite documents that only one write transaction can exist at a time per
database and that `BEGIN IMMEDIATE` begins a write transaction immediately or
returns `SQLITE_BUSY` if another writer is active:

- https://sqlite.org/lang_transaction.html
- https://sqlite.org/isolation.html

This serializes each owner database. It does not create one atomic transaction
across the causal database, effect database, filesystem, and sender database.
Rev0877 treats the seams as a distributed state machine:

- payload stage can precede causal admission;
- filesystem publication can precede effect database publication;
- receiver terminal publication can precede sender settlement; and
- every later step is retryable from durable earlier state.

### Post-commit proof race

The effect owner originally performed an exact filesystem proof, opened
`BEGIN IMMEDIATE`, and then marked the row `Published`. That proof preceded the
independent database commit. A local mutation during the commit window could
produce a durable `Published` row and a terminal response based on stale
namespace evidence.

Rev0877 re-proves the exact immutable file after committing the publication mark.
A final review found the same class in a less obvious branch: if another owner
committed `Published` after this caller's pre-transaction proof, the caller
returned `AlreadyPublished` immediately after observing the row. That branch now
also commits its read/write transaction and performs a fresh post-commit
reconciliation before returning terminal status.

This does not prevent mutation after the final proof. It closes stale evidence
inside the implemented terminal transition under the nonmalicious-local-writer
trust model.

### Storage assumptions remain below SQLite

SQLite's atomic commit documentation explicitly depends on operating-system and
storage behavior, including working flush primitives and faithful reads/writes:

- https://www.sqlite.org/atomiccommit.html

AnonSync's database cutpoint claims inherit those assumptions. The tests model
process crashes and deliberate database corruption, not arbitrary lying
hardware, malicious kernels, or storage devices that acknowledge flushes
without persistence.

## Crash matrix

| Frontier | Durable state possibly present | Retry behavior | Sender terminal? |
|---|---|---|---|
| Before effect stage | no effect row | stage exact payload | no |
| After effect stage, before evidence admission | staged payload | duplicate stage, retry admission | no |
| Evidence pending | staged payload + pending evidence | retry after parent arrival | no |
| Evidence quarantined | staged payload + quarantined evidence | remains nonterminal pending policy | no |
| Projection blocked | staged payload + retained nonprimary evidence | remains nonterminal | no |
| Before rename | staged payload + active evidence | publish absent destination | no |
| After rename, before directory sync | new namespace entry, ambiguous durability | exact reconcile and sync | no until proof |
| After durable file, before effect DB mark | exact private file + staged row | reconcile then mark Published | no until mark/proof |
| After effect DB mark, before response | Published row + exact file | post-commit proof, AlreadyPublished | yes |
| After terminal response, before sender settlement | receiver terminal, sender intent live | fresh claim after expiry; duplicate effect | only after receipt apply |
| Conflicting destination | existing preserved entry + staged effect | explicit policy/operator action | no |
| File removed after Published | Published row contradicts namespace | fail closed | no new receipt |
| File permissions widened/hard-linked after Published | Published row contradicts private identity | fail closed | no new receipt |

The model is at-least-once request delivery plus idempotent immutable effect,
not a global exactly-once transaction. Under the stated local trust boundary,
retries converge without replacing an existing destination.

## Service composition findings

### Materialize only an unambiguous active primary

Causal retention is not equivalent to visible authority. The service invokes the
existing evidence owner, then materializes only when projection says this exact
operation is the unambiguous active primary for its canonical path. Pending,
quarantined, and projection-blocked operations remain staged and nonterminal.

### Capacity ordering

Effect capacity is checked before causal admission. This prevents the receiver
from emitting evidence authority for a file it refuses to retain payload for.
The `EffectCapacityBlocked` receipt therefore has no inner evidence receipt, no
effect ID, and no nonzero effect generation. Other dispositions retain their
exact evidence result.

### Create-new update limitation

Two valid file operations for the same canonical path cannot both be realized by
create-new publication. The first exact file wins. A later active operation sees
an existing nonmatching destination, returns `DestinationConflict`, and leaves
the sender intent live.

This behavior is safe but not convergent for ordinary mutable files. A future
model should not simply switch to blind replacement. Better candidates include:

- content-addressed immutable object publication followed by a small atomic
  projection pointer;
- versioned destination generations with an exact previous-generation
  precondition;
- receiver effect intents that retain both old and new object identities until
  projection commit; and
- explicit conflict preservation rather than overwriting unrecognized local
  content.

### Tombstones require their own effect protocol

Deletion is not “a zero-byte file.” A correct tombstone effect must define:

- what exact prior entry identity may be removed;
- whether unrecognized local content is preserved as conflict evidence;
- how unlink and parent-directory durability are reconciled after crash;
- how a missing destination is classified on first delivery versus retry;
- how deletion authority survives path/root epoch changes; and
- what terminal receipt proves.

Filtering tombstones out of the file claimant is therefore the correct current
behavior.

## Runtime evidence

The new focused tests contribute:

- 29 atomic reconciliation checks;
- 35 file-effect SQLite owner checks;
- 4,477 file-delivery protocol checks; and
- 55 composed file-delivery service checks.

Together with the rev0876 evidence protocol, causal owner, delivery service, and
TLS tests, the focused authority slice contains 7,479 checks.

The protocol suite performs canonical round trips and rejects every truncation,
every single-byte mutation, and trailing data. It tests cross-request receipt
binding, terminality rules, capacity receipts without laundered inner authority,
and joint frame/operation/payload limit coherence.

The effect owner suite covers restart, exact duplicate staging, aggregate
capacity, ambiguous post-rename recovery, destination conflict, missing or
contradictory published files, payload tamper, metadata tamper, schema tamper,
cutpoint tamper, duplicate/gapped/equal generations, and impossible state counts.

The service suite covers binary payload publication, tampering, wrong channel,
terminal settlement, duplicate effect receipt, same-path update conflict,
missing-dependency promotion, three-owner restart after lost response, exact
lease expiry, fresh claim identity, stale receipt fencing, effect-capacity-before-
evidence ordering, and file-only claimant behavior in the presence of a live
tombstone intent.

Final cloudtainer validation is recorded in `RELEASE_GATE.json` and
`REVISION_EVIDENCE/rev0877/`:

- 183/183 registered tests in one CTest invocation;
- 54/54 audit-named registered tests;
- 7,479/7,479 GCC 14 Debug focused checks;
- 7,479/7,479 Clang 17 Release C++ `-Werror` focused checks;
- 7,479/7,479 GCC 14 ASan/UBSan focused checks with leak detection and bundled
  SQLite instrumentation;
- 20/20 repeated runs each for causal owner, effect owner, and file service,
  totaling 5,580 checks; and
- 145/145 focused source-audit checks.

The all-target Debug build initially ran at two-way parallelism and reached the
cloud tool's command time limit after 100 of 284 reported steps. Resuming at
higher safe parallelism completed the remaining graph, and a final rebuild was
no-work. This is not a source failure, but it is evidence that target
proliferation and large compilation units impose real iteration cost.

## Audit/refactor of the cube

### Lexical CMake audit false positives

The bounded regular-file audit used broad substring ranges. Adding neighboring
rev0877 targets caused it to infer links from text that belonged to another
CMake invocation. This failed the complete registry despite correct runtime
behavior.

The audit now extracts the exact body of a named CMake command/target before
checking source ownership and dependencies. This is still lexical analysis, but
it is scoped to the syntactic unit it intends to inspect.

### Atomic audit strengthened rather than relaxed

The atomic audit failure was not suppressed. It was updated to require the new
semantics:

- binary create-new and reconciliation APIs;
- exact same-owner mode-0600 single-link identity;
- explicit `fchmod` normalization;
- stable bounded reads;
- file and directory synchronization;
- post-sync identity proofs;
- umask, mode-widening, hard-link, symlink, and ambiguity tests;
- Windows fail-closed behavior;
- focused no-core dependency guards;
- sanitizer and CTest registration; and
- package verifier requirements.

### Build graph remains structurally expensive

The CMake file now contains 73 literal `add_library`, 96 literal
`add_executable`, and 186 literal `add_test` occurrences. Meanwhile:

- `src/sync_domain.cpp` is about 15,167 lines;
- `src/sync_domain_selftests.cpp` is about 9,601 lines;
- `src/sqlite_replay_ledger.cpp` is about 4,529 lines;
- `src/sync_peer_ingress_lifecycle.cpp` is about 3,846 lines; and
- `src/sync_replica_sqlite_owner.cpp` is about 3,569 lines.

This is partial link-time modularity without equivalent semantic or compile-time
modularity. Recommended correction:

1. define authority-owner modules with small typed interfaces;
2. split implementation by state transition, serialization, restoration, and
   storage boundary rather than by ever-growing test target;
3. replace repeated target/test/sanitizer wiring with declarative CMake helpers;
4. create an affected-authority preset for rapid iteration;
5. retain one complete registry gate before sealing; and
6. measure compile-time dependency fanout to prioritize cuts.

### Evidence growth

This working tree's historical `REVISION_EVIDENCE/` exceeds 4,500 files and is
roughly 40 MB extracted. Compression helps archive transfer but does not remove
hashing, extraction, navigation, review, or future handoff cost.

A better evidence architecture would keep in-tree:

- current active projection;
- parent archive hash and compact lineage;
- current source patch;
- concise validation summary;
- source-audit reports; and
- hashes/URIs for bulk logs.

Bulk build logs and historical stress corpora should move to a content-addressed
store with externally trusted signatures. The current package remains self-
contained because that external system does not yet exist.

## What is still missing

### Shipped product integration

No production caller in `anonsync_core` uses
`SyncReplicaFileDeliveryService`. The newer causal/effect path remains a
carefully tested library island. This is still the largest delivery risk: proof
can improve while user-visible behavior remains on the older stack.

The next executable should be intentionally narrow:

- one configured folder;
- one pinned peer;
- one File operation type;
- TLS 1.3 authenticated framed transport;
- bounded request queue;
- causal and effect SQLite owners;
- stable root capability;
- terminal receipt response; and
- explicit metrics for pending, quarantined, conflict, capacity, and retry.

### Stable root and mutable projection

The immediate next correctness work should bind root identity. The next product
work should separate immutable content objects from visible mutable paths. That
combination is more promising than extending direct create-new writes into blind
replace operations.

### Durable receipt authentication

A terminal receipt is authenticated while carried on the exact TLS channel.
Outside that session, the receipt frame has only a structural hash. A durable
archival receipt should be signed by a receiver device key or bound to a signed
append-only receiver effect log, with key epoch and revocation semantics.

### Staging lifecycle and hostile-peer fairness

The effect owner has aggregate bounds but no per-peer accounting, expiry,
reclamation, or dead-letter authority. Payload-before-admission is correct for
availability but can be abused for storage denial. Quota identity must be bound
to authenticated membership, not an untrusted message field.

### Indexed production owners

Both modern owners reconstruct all retained state on each operation. Keep these
implementations unchanged as reference oracles. Build a new incremental owner
with indexed counters, Merkle or chunked attestations, and bounded write paths.
Then differentially test both owners under generated histories, schema
corruption, process exits, disk-full simulation, and retry schedules.

### Complete synchronization semantics

Still absent:

- normal updates and rename semantics;
- tombstone/delete effects;
- conflict object retention;
- third-party gossip and anti-entropy;
- causal stability and compaction;
- tombstone collection and offline/revoked replica policy;
- membership enrollment, rotation, revocation, and recovery;
- retry classifier, backoff, jitter, dead-letter, and wake scheduling;
- service-level network quotas and cancellation;
- stable privacy/adversary model; and
- externally trusted build provenance.

## Speculative roadmap

### Milestone A: root-bound single-peer service

Create `anonsync_replica_service` using the newer owners and rev0876 TLS adapter.
Retain a root directory capability for process lifetime, persist root identity
and epoch, and fail closed on restart mismatch. Support only create-new files.
Inject process exits at every database, frame, write, rename, fsync, receipt, and
settlement frontier.

### Milestone B: immutable object store plus visible projection

Publish payloads under content-addressed object IDs. Make visible paths small
projection records that name object ID, operation ID, and prior projection
generation. This can support updates without overwriting an unrecognized object
and can make duplicate effects naturally idempotent.

### Milestone C: signed effect log

Append each terminal effect transition to a receiver-owned signed log. Receipts
name the log position, effect cutpoint, device key epoch, and signature. Sender
settlement can then be audited after the transport session.

### Milestone D: indexed owner differential proof

Implement an incremental database owner with indexes and cached attestations.
Use the current O(history) owners as test oracles. Generated scenarios must
produce identical canonical snapshots, projection, outbox/effect state, and
cutpoints.

### Milestone E: deletion and compaction

Define tombstone effect semantics before adding deletion. Add causal stability,
revoked/offline replica policy, checkpoints, object reclamation, and explicit
full-resync rules.

### Milestone F: privacy statement before anonymity claims

Specify observers, relays, endpoint knowledge, traffic timing/volume, device
identifiers, certificate exposure, storage compromise, and local-host trust.
Only then choose padding, batching, relay indirection, private discovery, or
group-key mechanisms. The name “AnonSync” should remain an aspiration, not a
claim implied by payload encryption alone.

## Deliberate nonclaims

Rev0877 does not claim:

- use of the new effect path by the shipped executable;
- normal file replacement/update convergence;
- tombstone or deletion effects;
- exactly-once behavior against a malicious or privileged local writer;
- a stable root directory identity across calls or restart;
- payload staging fairness, expiry, or garbage collection;
- independently signed or offline-verifiable effect receipts;
- complete membership/key lifecycle;
- complete retry/backoff/dead-letter policy;
- network event-loop behavior or hostile-client cancellation;
- production-scale incremental causal/effect ownership;
- anti-entropy, causal stability, compaction, or old-replica rejoin;
- Windows parent-directory durability;
- anonymity, unlinkability, or metadata hiding;
- externally trusted signed provenance;
- full-project Clang, sanitizer, or ThreadSanitizer coverage; or
- formal proof.

Within those limits, rev0877 closes the most important visible-effect gap in the
new causal path and does so without laundering ambiguous filesystem or database
observations into terminal sender authority.
