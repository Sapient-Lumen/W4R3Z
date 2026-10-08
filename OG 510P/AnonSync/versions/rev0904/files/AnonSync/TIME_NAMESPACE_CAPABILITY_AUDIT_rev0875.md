# AnonSync rev0875 — truthful time-namespace capability, durable unknown quarantine, and mission-gap audit

## Executive finding

AnonSync's heart is not file copying. It is **authority accounting under crash,
duplication, reordering, resource pressure, and partial trust**. Exact canonical
evidence is supposed to be the only source from which identity, causality,
projection, dispatch, retry, receipt, and visible effects may derive. Everything
else—digests, clocks, summaries, indexes, counters, leases, schedulers, and build
reports—is subordinate evidence and must fail closed rather than silently minting
fact.

Rev0874 materially improved that local authority model, but its release claim hid
a real portability defect. In this cloudtainer, Linux reports a 6.12 kernel while
`/proc/thread-self/ns/time` is absent. The rev0874 runtime interpreted the kernel
release as proof that time-namespace identity must exist and threw before the
clock owner could durably publish what was actually observed. The parent archive
therefore produced **175/176**, not its recorded **176/176**, in this environment.

That is now corrected. Kernel generation is treated only as a feature-generation
hint. Only a successful observation of the calling thread's namespace handle is
classified as `Bound`. A missing or permission-hidden handle becomes explicit
`IdentityUnavailable` evidence. The Linux source emits a source ID that names the
unavailable identity, reports synchronization `Unknown`, and lets the existing
owner durably quarantine the observation as `synchronization-unknown`. Ordinary
liveness work remains blocked. Nothing is relabeled supported, synchronized, or
safe.

The deeper finding is more important than the clock bug: AnonSync currently has
two weakly connected products.

1. The shipped `anonsync_core` executable follows an older, feature-rich domain,
   peer-ingress, replay-ledger, local-transport, and runner stack.
2. The newer causal replica, receipt-bound outbox, owned clock, and exact SQLite
   owner form a highly tested correctness oracle that has no production caller.

The newer path is architecturally stronger but lives almost entirely in tests and
structural audits. Rev0875 adds a two-database composition test that proves one
canonical operation can cross independent SQLite cutpoints, survive ambiguous
sender settlement, retry after expiry, be accepted as an exact duplicate by the
receiver, settle with the fresh receipt, and reject the stale receipt. That is a
useful first vertical seam. It is **not** authenticated transport, payload
materialization, filesystem publication, or a production execution path.

The highest-leverage next work is therefore not another isolated invariant. It is
to make one narrow executable sender→receiver→effect path consume the newer owner
without weakening it.

## Heart of the mission

AnonSync is best understood as a chain of authority transitions:

1. **Observation authority.** Input bytes, local filesystem facts, peer messages,
   membership state, resource state, and time observations must be bounded,
   typed, and attributable to a specific observer and cutpoint.
2. **Canonical identity.** One exact canonical operation representation must mint
   one immutable operation ID. Semantically similar but byte-different forms
   cannot share identity unless a versioned canonicalizer explicitly says so.
3. **Causal authority.** Immediate predecessor evidence owns causality. Vector
   summaries, Bloom filters, indexes, checkpoints, and counters may locate or
   accelerate proof but cannot replace exact parent evidence.
4. **Actor and membership authority.** An operation must bind to an authorized
   actor/key epoch and a rule for rotation, revocation, recovery, old-epoch
   acceptance, and device removal.
5. **Durable publication.** Operation bytes, parent edges, payload commitments,
   projection decisions, dispatch intent, clock evidence, receiver intent, and
   effect status must cross crash cutpoints atomically or through explicitly
   recoverable staged states.
6. **Deterministic projection.** Evidence must remain separable from active and
   visible state so trust changes, dependency arrival, conflict rules, and policy
   replacement can be recomputed without inventing history.
7. **Bounded dissemination.** CPU, bytes, identities, dependencies, attempts,
   leases, storage, retries, wakeups, and repair work need explicit ceilings and
   deterministic admission/backpressure behavior.
8. **Receiver effect authority.** A terminal receipt should attest one exact,
   idempotent, crash-consistent receiver effect—not merely message arrival.
9. **Privacy authority.** The name "AnonSync" must not imply anonymity until the
   adversary, metadata surface, discovery system, relay behavior, traffic shape,
   cover strategy, and unlinkability goals are stated and tested.

The compact mission invariant remains:

> Given the same authorized canonical evidence and trust state, replicas derive
> the same state; no untrusted input, crash cutpoint, duplicate, missing
> dependency, resource claim, stale receipt, schema mutation, clock movement,
> retry response, migration shortcut, or local pressure decision silently gains
> authority.

This is a strong mission. It is internally coherent and substantially more
ambitious than ordinary synchronization. The project should preserve it.

## The rev0874 regression

### Observed failure

The uploaded rev0874 archive configured and built cleanly with GCC 14 in this
cloudtainer. One complete CTest invocation registered 176 tests and passed 175.
The failing test was `anonsync_sync_replica_outbox_clock_test` after 42 checks.
Its system-source smoke path reported that the calling thread's time-namespace
identity was unavailable on a kernel it believed supported time namespaces.

The relevant environment facts were:

- Linux release `6.12.13`;
- `/proc/self/ns` and `/proc/thread-self/ns` exposed no `time` or
  `time_for_children` entries; and
- `/proc/sys/user/max_time_namespaces` existed, but that tunable is not proof that
  this kernel configuration and procfs view expose a usable namespace identity.

Rev0874's code did this:

1. `stat("/proc/thread-self/ns/time")`;
2. on `ENOENT`, parse the kernel major/minor;
3. if generation was 5.6 or later, throw because the handle was considered
   mandatory; otherwise synthesize a pre-feature fallback identity.

The invalid inference was step 3. Mainline version history is not a runtime
capability proof. Linux time namespaces require optional `CONFIG_TIME_NS`, and a
restricted procfs view may prevent a process from observing namespace handles.
The safe statement is only: **this process did or did not observe the exact
calling-thread namespace identity**.

### Why throwing was the wrong fail-closed behavior

Fail-closed does not mean "throw as early as possible." The authority owner had a
stronger behavior available: preserve the exact observation, classify its
quality as unknown, publish durable quarantine, and refuse to mint lease or retry
liveness. Throwing before that transition lost the evidence explaining why the
system stopped. It also made the behavior environment-dependent in a way the
release gate did not disclose.

The repaired boundary distinguishes:

- `Bound`: `stat` succeeded and produced a nonzero inode;
- `AbsentBeforeMainlineFeature`: `ENOENT` on a pre-5.6 generation hint;
- `IdentityUnavailable`: `ENOENT` on a 5.6+ generation or `EACCES`/`EPERM`;
- `FatalError`: unexpected probe failures such as `EIO`.

Only `Bound` permits the Linux source to report kernel synchronization quality as
`Synchronized` or `Unsynchronized`. Both unavailable cases report
`Synchronization::Unknown`. The pre-5.6 distinction survives in the source ID for
diagnostics, but it does not grant more authority. This is intentionally
conservative because backports, custom kernels, and procfs policy make version
alone non-authoritative.

### Durable anomaly semantics

Rev0874 collapsed both "the kernel reported unsynchronized" and "we could not
establish the required capability/identity" into one `Unsynchronized` anomaly.
Rev0875 adds `SynchronizationUnknown` as a new additive anomaly code and canonical
name `synchronization-unknown`. Existing anomaly numeric values remain unchanged,
and the existing versioned state codec remains readable.

The distinction matters operationally:

- `unsynchronized` means a relevant source positively reported a discipline
  failure;
- `synchronization-unknown` means the system lacks enough capability evidence to
  make that claim either way.

Both quarantine and block time-authorized work. They should lead to different
operator diagnostics and remediation.

### Deterministic proof added

The clock runtime now tests a matrix independent of the host:

- successful probe → `Bound`;
- Linux 5.5 + `ENOENT` → `AbsentBeforeMainlineFeature`;
- Linux 5.6 and 6.12 + `ENOENT` → `IdentityUnavailable`;
- `EACCES` and `EPERM` → `IdentityUnavailable`;
- `EIO` → `FatalError`.

The cloudtainer smoke path now requires any unavailable namespace identity to
produce `Unknown`, then proves that the pure state machine and SQLite owner
persist exact rejected observation bytes, digest, anomaly, high-water state, and
sticky restart quarantine without advancing operation or outbox authority.

## The assurance-process defect

The regression was not only a platform edge case. The rev0874 audit explicitly
listed more nuanced platform-capability handling as unfinished, yet
`RELEASE_GATE.json` recorded an unconditional 176/176 result and the narrative
suggested the Linux source had a settled capability model. The assurance system
proved token presence and one prior environment, not the semantic proposition
being advertised.

Three process changes follow:

1. **Release results must be environment-qualified.** A checked-in test count is
   historical evidence from one run, not a universal portability theorem.
2. **Named open risks must affect gates.** When an audit identifies capability
   handling as unfinished, a deterministic negative test or an explicit caveat
   belongs in the same release.
3. **Lexical audits are hygiene, not semantic proof.** The rev0874 clock source
   audit passed because expected strings and call ordering existed. It could not
   detect the invalid inference from kernel generation to configured/observable
   capability. Rev0875 keeps the lexical audit but adds a typed classifier and
   runtime matrix.

## First cross-database delivery seam

Rev0875 adds a deterministic integration test around two independent
`SyncReplicaSqliteOwner` databases. The test performs this sequence:

1. create equivalent sender and receiver replica folders in separate SQLite
   files;
2. create one canonical sender operation and durable outbox intent addressed to
   the receiver;
3. claim attempt 1 and retain its receipt-bound lease identity;
4. durably accept the operation at the receiver and obtain terminal receiver
   evidence;
5. close both owners before sender settlement, modeling a crash after receiver
   commit but before the sender knows the result;
6. reopen both databases and prove retry before lease expiry is blocked;
7. claim at the exact expiry boundary, requiring a fresh claim ID and attempt 2;
8. send the same canonical operation again and require the receiver to return an
   exact duplicate outcome without rewriting its operation evidence;
9. settle the sender with the fresh attempt-2 receipt;
10. prove sender and receiver canonical digests converge; and
11. replay the stale attempt-1 receipt and prove it cannot mutate the settled
    cutpoint.

This is the first test in the recent causal-owner line that resembles an actual
end-to-end ambiguity frontier. It validates the desired at-least-once transport +
idempotent receiver + receipt-fenced sender pattern at the database owner level.
It does not yet include bytes on a socket, peer authentication, payload chunks,
filesystem effects, or cryptographic terminal receipts.

## The major architectural split

`SyncReplicaSqliteOwner` is defined and linked into its own static library and its
runtime/audit tests. A repository-wide production search finds no caller in
`src/`, `include/`, or `anonsync_core`. The `ANONSYNC_CORE_SOURCES` list instead
contains the older sync domain, peer ingress, replay ledger, local transport,
operator CLI, reporting, and runner sources. CMake even enforces that many newer
"invariant-owned" sources remain outside the monolithic core.

That separation was useful for focused testing and for extracting authority
boundaries from a very large legacy core. It has now become an integration debt:
the strongest current replica and outbox semantics are not the semantics of the
shipped executable.

This creates several risks:

- **False completion pressure.** Passing hundreds of owner checks can feel like
  product progress while no user-facing path consumes the owner.
- **Semantic divergence.** The old stack and new owner can evolve different
  operation identity, retry, time, receipt, and projection rules.
- **Duplicated trust boundaries.** Local transport, peer ingress, and causal
  simulation may each define subtly different authentication and duplicate
  handling.
- **Migration ambiguity.** There is no declared path from an existing legacy
  store to the new owner or a rule for which store is authoritative during a
  transition.
- **Assurance inversion.** The test island is more rigorously specified than the
  product path, so expensive proof effort does not yet reduce the dominant
  deployment risk.

The corrective move is not to merge all files back into one library. It is to
create a small executable/application service whose only durable replica authority
is `SyncReplicaSqliteOwner`, then adapt transport and effect boundaries around
that owner.

## What is missing

### P0: one executable authenticated vertical slice

The next milestone should be a deliberately narrow one-folder, two-process path:

`observe local intent → canonical operation → sender outbox → authenticated
frame → receiver durable idempotency → staged payload/effect → atomic visible
publication → terminal receipt → sender settlement`

The slice should initially support one operation kind and one payload strategy.
It should bind at least:

- protocol/version and canonical framing;
- sender actor/device ID and key epoch;
- receiver/folder destination identity;
- immutable operation ID and exact canonical bytes;
- immediate parent IDs;
- payload digest, length, and bounded spool handle;
- claim ID, attempt number, lease/retry generation, and expiry observation;
- receiver accept/duplicate/conflict outcome;
- exact effect intent and final publication identity;
- terminal receipt covering operation, effect result, receiver identity, and
  protocol transcript/channel binding; and
- sender settlement conditional on the exact current claim.

A loopback or Unix-domain transport is acceptable for the first product slice if
it still uses the same authenticated frame and crash boundaries intended for a
remote connection. The purpose is composition, not network reach.

### P1: receiver-side effect owner

The repository already contains atomic file publication, bounded regular-file,
payload-store, and effect-intent components. They need one receiver transaction
or recoverable state machine that says exactly when:

- payload bytes are complete and verified;
- a temp object is owned by this operation/effect intent;
- the target path and conflict rule are frozen;
- rename/publication has occurred;
- directory durability has been attempted and classified;
- restart discovers pre-publication, post-publication/pre-receipt, and cleanup
  states; and
- duplicate delivery returns the same terminal evidence without repeating a
  non-idempotent effect.

"Exactly once" should remain a nonclaim. The implementable target is
at-least-once delivery with idempotent, evidence-bound receiver effects.

### P1: authenticated transport and membership/key lifecycle

Do not invent a bespoke cryptographic handshake. TLS 1.3 with explicit device
certificate pinning or a well-reviewed Noise pattern can supply pairwise
authenticated encryption. The application still must bind the protocol
transcript to folder membership, device/key epoch, operation framing, and receipt
signatures/MACs.

Membership remains underspecified. A deployable design needs:

- root or recovery authority;
- device enrollment proof;
- monotonic membership epochs;
- rotation and revocation semantics;
- treatment of operations signed under old but previously valid epochs;
- compromise recovery and rollback prevention; and
- a rule for offline devices that miss revocations.

MLS is designed for dynamic group authenticated key exchange and may become
relevant if one folder has many independently changing members. It is likely too
large a dependency for the first pairwise vertical slice. It also does not solve
application-level durable delivery, effect idempotency, or denial by a delivery
service.

### P1: complete retry policy

The outbox has strong receipt and lease ownership, but not a production retry
system. Add typed outcomes such as:

- local pre-send/transient;
- DNS/connect/TLS/authentication;
- protocol/version rejection;
- remote resource pressure with optional bounded retry hint;
- receiver durable duplicate/accepted/conflict;
- terminal authorization or membership rejection;
- payload-integrity failure;
- operator-correctable poison; and
- permanent dead-letter.

Each class should define bounded exponential backoff, jitter source, maximum
attempt count/age, wake-index entry, durable reason evidence, and operator replay
authority. Remote retry hints must be clamped by local policy and cannot grant
unbounded storage or wake work.

### P1: incremental production owner beside the O(history) oracle

`SyncReplicaSqliteOwner` intentionally restores and re-attests complete retained
history before every write. This is excellent as a reference oracle, migration
validator, repair authority, and adversarial test surface. It is not a viable
hot path for large histories.

Do not optimize it in place. Add an indexed owner that maintains:

- operation and parent indexes;
- unresolved-dependency queues;
- actor/key epoch indexes;
- outbox due-time and destination indexes;
- receiver effect indexes;
- projection generations and compact checksums; and
- bounded verification windows plus periodic/full repair.

Then run every generated operation/crash/retry scenario against both owners and
require canonical state equivalence. The slow owner should remain the oracle.

### P2: causal stability, compaction, and rejoin

The project has retained evidence budgeting but not a complete rule for deleting
causal history. A safe compaction design needs explicit membership knowledge,
acknowledged stability frontiers, treatment of revoked/offline replicas,
checkpoint authenticity, tombstone lifetime, and a full-resync/rejoin rule.
Summaries cannot become authority merely because old evidence was expensive.

### P2: a real privacy threat model

Payload encryption is not anonymity. A direct sync connection exposes timing,
volume, endpoints, protocol fingerprint, and often stable device identity. Relays
can hide direct addressing from peers in some topologies but learn connection
metadata themselves. Discovery services may link device identity and network
location.

Before the name becomes a claim, choose an adversary and goals:

- content confidentiality only;
- peer identity confidentiality from passive observers;
- IP unlinkability between peers;
- relay-oblivious routing;
- resistance to timing/volume correlation;
- sender anonymity within a group; or
- deniability.

Stronger goals require some combination of rendezvous indirection, rotating
pseudonyms, mix/relay paths, batching, padding, cover traffic, delayed delivery,
and careful key-distribution metadata. Those choices directly conflict with low
latency, low bandwidth, deterministic retry timing, and resource bounds. The
tradeoff must be explicit.

## Severe or wasteful patterns

### 1. Cumulative evidence has become a product inside the product

Before rev0875 evidence is added, `REVISION_EVIDENCE/` contains roughly 4,473
files, 40 MB, and more than 900,000 text lines. The entire uploaded ZIP is about
14 MB because text compresses well, but extraction, hashing, review, manifest
construction, and repository navigation all pay the full file-count and byte
cost. Many historical revisions copy logs, registry dumps, verification reports,
and source patches that are useful once but do not belong in every future source
handoff.

Over time, move bulk evidence to a content-addressed external artifact store with
signed provenance. Keep in-tree:

- current revision design/audit records;
- a compact parent hash and lineage statement;
- active implementation projection;
- exact manifest;
- concise validation summary and essential failing/passing outputs; and
- durable architecture decisions.

Do not delete historical authority casually. Migrate it, hash it, sign its index,
and retain retrieval instructions. Rev0875 intentionally starts an evidence diet:
its own revision evidence is compact rather than copying another large registry
and build-log corpus.

### 2. Link-time granularity exceeds semantic granularity

CMake currently declares 66 libraries, 89 executables, 179 literal `add_test`
calls, and a roughly 335-step clean build graph. This appears highly modular, but
several semantic centers remain giant translation units:

- `src/sync_domain.cpp`: about 15,000 lines / 1.1 MB;
- `src/sync_domain_selftests.cpp`: about 9,600 lines / 0.8 MB;
- `src/sqlite_replay_ledger.cpp`: about 4,500 lines;
- `src/sync_replica_sqlite_owner.cpp`: about 3,500 lines; and
- `include/anonsync_core.hpp`: about 3,500 lines.

The result is many target edges and test binaries around a few compilation
monoliths. A small owner-clock change still pays substantial unrelated compile
and link cost in the full gate.

Correct this gradually:

- split giant units by true authority boundary and ownership, not arbitrary line
  count;
- create CMake helper functions or a declarative test registry for repetitive
  target wiring;
- separate fast per-change authority suites from a full legacy regression gate;
- use dependency-aware CI lanes so unrelated monoliths are not rebuilt for every
  leaf change; and
- keep a periodic/full gate so selective testing does not become accidental
  undercoverage.

### 3. Lexical source audits overstate assurance

The repository has about 60 tool files and more than 27,000 tool lines, with many
Python audits based on `read_text`, substring checks, and regular expressions.
These are good at detecting missing files, retired names, obvious call ordering,
and release packaging drift. They are poor at proving type flow, control flow,
error semantics, and runtime capability behavior.

The failed rev0874 test is the clearest example: all expected clock tokens were
present, but the kernel-version inference was wrong.

Keep lexical audits as cheap guardrails. For important semantics, prefer:

- typed enums and total switches;
- pure deterministic classifiers;
- negative runtime matrices;
- property/state-machine generation;
- differential oracle testing;
- CMake File API or compile database analysis instead of CMake text matching;
- compiler AST/static-analysis queries where proportionate; and
- a much smaller number of load-bearing release assertions.

### 4. The new oracle is disconnected from the product

This is the largest waste risk. More hardening of an uncalled owner can increase
assurance locally while leaving the actual executable unchanged. Until the
production vertical slice exists, every new causal-owner revision should answer:
"Which executable path now consumes this invariant?" A test-only answer can be
valid for exploration, but it should be labeled as such and time-bounded.

### 5. Full-history verification can become ritual instead of leverage

Re-attesting full history is valuable because it catches tamper, migration, and
partial-restore defects. Repeating it for every hot-path operation at scale would
turn correctness into self-denial. Preserve it as oracle and repair mode; build a
separate incremental mode with periodic proof and differential testing.

### 6. Release provenance is self-reported

`MANIFEST.sha256`, active projections, and in-archive release gates detect
accidental mismatch and make claims inspectable. They are not externally trusted
provenance because the same workspace can rewrite source, outputs, manifest, and
claim JSON. Over time, produce attestations in an isolated builder/control plane
and sign them with keys unavailable to the build job. Content-address build cache
entries by the transitive input closure, not only source filename or source hash.

## Research findings and implications

### Linux time namespaces

The Linux manual states that time namespaces require the optional
`CONFIG_TIME_NS` kernel configuration and do not virtualize `CLOCK_REALTIME`.
They virtualize boot-relative clocks for use cases such as migration and
checkpoint/restore. `CLOCK_BOOTTIME` is monotonic-like but includes suspend,
which fits local lease aging better than `CLOCK_MONOTONIC` when sleep should
consume a lease.

Implication: AnonSync is correct to bind boot-relative evidence and calling-thread
namespace identity, but it must treat handle observability as a capability fact.
Kernel release alone cannot prove configuration or visibility. The current
`adjtimex`/realtime + boottime design remains local host evidence, not
cryptographic UTC.

Sources:

- https://man7.org/linux/man-pages/man7/time_namespaces.7.html
- https://man7.org/linux/man-pages/man2/clock_getres.2.html

### SQLite writer serialization

SQLite documents that successful `BEGIN IMMEDIATE` starts a write transaction
and blocks other writers. This supports the rev0874 decision to sample liveness
after acquiring the writer transaction when that sample authorizes a database
transition.

Implication: the local serialization argument is sound for one SQLite database,
provided all relevant mutations use the same writer authority and restore/verify
rules. It is not a distributed transaction across sender and receiver databases;
the rev0875 ambiguous-settlement test correctly uses idempotency and retry rather
than pretending atomic cross-database commit.

Source:

- https://sqlite.org/isolation.html

### Noise, TLS, and transcript binding

Noise specifies DH-based handshake patterns that derive encrypted transport
states and retain a handshake hash usable for channel binding. TLS 1.3 with
certificate/public-key pinning is another mature pairwise option. Either can
protect a connection, but AnonSync must still bind its own device/folder/key epoch,
operation identity, and terminal receipt semantics to the authenticated channel.

Source:

- https://noiseprotocol.org/noise.html

### Lessons from Syncthing

Syncthing protects device-to-device traffic with TLS and device certificate
fingerprints, yet its own security documentation is explicit that network
observers or relays can learn protocol/device metadata. Its untrusted-device
mode separates metadata exchange from requested block transfer and encrypts
names/block lists for the untrusted store.

Implication: AnonSync can learn from the mature two-phase metadata/block pattern
and device pinning, but should also learn from the candor: encrypted content does
not equal anonymity. Stable identifiers, discovery, relays, timing, and volume
remain observable.

Sources:

- https://docs.syncthing.net/users/security.html
- https://docs.syncthing.net/specs/untrusted.html

### MLS for later group membership

MLS provides continuous authenticated group key exchange organized by groups and
epochs, assuming an authentication service and a largely untrusted delivery
service. It protects group content against a compromised delivery service, but
the delivery service can still delay, drop, or selectively suppress messages.

Implication: MLS may eventually help multi-device folder key evolution, forward
secrecy, and post-compromise security. It does not replace AnonSync's exact
operation causality, durable receiver effects, resource governance, or loss and
retry policy. A pairwise first slice is simpler.

Source:

- https://datatracker.ietf.org/doc/rfc9420/

### NTS and stronger time evidence

Network Time Security authenticates client/server NTP exchanges using an initial
TLS-based key exchange and authenticated NTP extension fields. It can reduce
unauthenticated network-time spoofing.

Implication: NTS is an optional future witness if the threat model needs stronger
network time. It still does not make remote time infallible, prevent delay attacks,
or supply cross-reboot monotonic continuity. Lease semantics should continue to
separate physical-time evidence from causal ordering and explicit operator
recovery.

Source:

- https://www.internetsociety.org/blog/2020/10/nts-rfc-published-new-standard-to-ensure-secure-time-on-the-internet/

### Signed build provenance

SLSA's current threat guidance emphasizes provenance generated and signed by a
trusted control plane, isolation between builds, and cache keys covering the
transitive input closure.

Implication: AnonSync's self-contained manifests are useful integrity metadata but
not a malicious-builder defense. External signed provenance should replace the
current growth pattern of recursively embedding large self-reported proof sets.

Source:

- https://slsa.dev/spec/v1.2/threats

## Speculation

The following are reasoned directions, not claims about implemented behavior.

1. **Keep the current owner forever, but demote it from hot path.** It can become
   the offline verifier, repair engine, migration oracle, and differential test
   reference for faster implementations.
2. **Make the first real deployment local and boring.** Two processes on one host
   with separate SQLite stores, authenticated loopback framing, bounded payload
   spool, and real atomic publication will expose more composition defects than
   another broad in-memory network model.
3. **Represent host features as a typed capability vector.** Time namespace,
   procfs handle visibility, `adjtimex`, directory fsync behavior, rename
   semantics, sparse files, reflinks, secure open flags, and filesystem type
   should be observed facts with `Present/Absent/Unavailable/Failed`, not inferred
   from OS labels.
4. **Generate crash-frontier tests from state-machine descriptions.** The project
   already hand-tests many cutpoints. A declarative transition model could
   enumerate pre/post-write, pre/post-fsync, pre/post-rename, pre/post-receipt, and
   restart states and run both oracle and incremental owners.
5. **Use cryptographic receipts only after effect semantics are exact.** Signing a
   vague "received" message would harden the wrong boundary. First define the
   receiver effect identity and terminal states; then sign/MAC that exact
   canonical receipt.
6. **Treat relays as a separate privacy and availability subsystem.** A relay
   protocol should not be quietly embedded in the causal core. It needs quotas,
   abuse handling, metadata claims, store-and-forward durability, and retry
   semantics of its own.
7. **Consider content-addressed payload chunks only after authority is fixed.**
   Deduplication and resumable transfer are attractive, but chunk hashes,
   encryption mode, cross-folder dedupe, and garbage collection can leak equality
   or create retention authority. Bind them to operation/folder policy.
8. **Move from "many audits" to an assurance hierarchy.** A small set of semantic
   conformance suites should own release authority; lexical audits, fuzzing,
   analyzers, and historical evidence should feed them rather than each becoming
   an equal release ritual.

## What changed in rev0875

Production C++:

- added `sync_replica_outbox_clock_linux_internal.hpp` with a pure, deterministic
  runtime probe classifier;
- removed the inference that Linux 5.6+ proves time-namespace capability;
- made missing/permission-hidden calling-thread namespace identity observable in
  source ID and digest;
- forced unbound identity to synchronization `Unknown`;
- added durable `SynchronizationUnknown` anomaly semantics without renumbering
  existing values; and
- preserved fail-closed behavior by routing unavailable capability through
  durable quarantine rather than pre-publication exception.

Tests and assurance:

- added deterministic time-namespace capability classification cases;
- made the system-source smoke test portable across restricted kernels/procfs;
- proved unknown capability persists exact quarantine through restart;
- added the two-independent-database ambiguous-settlement/duplicate-recovery
  composition test;
- expanded the clock structural audit to require these semantics; and
- made the release verifier require the rev0875 capability classifier and design
  record.

## Validation summary

The exact final results are recorded in `RELEASE_GATE.json` and
`REVISION_EVIDENCE/rev0875/validation/VALIDATION_SUMMARY.json`.

- GCC 14.2 Debug: the complete all-target graph built; the final dependency
  closure was no-work.
- One complete CTest invocation: 176/176 passed, including 54 audit-named tests.
- Focused Debug runtime: 53 clock + 37 lease + 198 owner = 288 checks.
- Owner stress: 20/20 iterations and 3,960/3,960 checks.
- Structural audits: 24 clock + 19 lease + 38 owner = 81/81.
- Clang 17 Release C++ `-Werror`: all three focused targets built and all 288
  checks passed. Bundled SQLite remained a GCC-compiled C dependency and emitted
  one warning outside the Clang C++ `-Werror` claim.
- GCC 14 ASan/UBSan Debug: all 288 focused checks passed with leak detection,
  halt-on-error, and bundled SQLite instrumentation.
- Active projection: 343 files, 18,954,230 bytes, SHA-256
  `520dd8904414e174ad2799aa09a2097b125835abb3d7a7265a57b659479016c2`.

Full-project Clang, full-project sanitizer, ThreadSanitizer, and formal proof are
not claimed. Directory and ZIP verifier results are generated after final manifest
and archive sealing and therefore remain external to the bytes they attest.

## Highest-leverage sequence

1. Build a production `anonsync_replica_service` around
   `SyncReplicaSqliteOwner`, supporting one operation and one bounded payload.
2. Connect two service instances through authenticated framed loopback/TCP and
   bind device/folder/key epoch to the transcript.
3. Add receiver durable effect ownership using existing bounded-file and atomic
   publication primitives.
4. Mint a canonical terminal effect receipt and settle the sender only against
   the exact live claim.
5. Inject crash at every sender, transport, receiver-database, payload, rename,
   fsync, receipt, and settlement frontier.
6. Add typed retry/dead-letter policy and due-time indexes.
7. Add an incremental owner and differential-test it against the full-history
   oracle.
8. Only then broaden operation kinds, payload chunking, remote discovery/relay,
   group membership, compaction, and privacy mechanisms.

## Deliberate nonclaims

Rev0875 does not claim:

- configured or observable time namespaces on every Linux 5.6+ kernel;
- authenticated physical time, UTC correctness, or cross-node clock agreement;
- malicious-host, privileged-local-writer, or procfs-tamper defense;
- automatic quarantine recovery or cross-reboot monotonic continuity;
- production use of `SyncReplicaSqliteOwner` by `anonsync_core`;
- authenticated sender/receiver transport;
- actor/membership/key lifecycle completion;
- payload or chunk materialization in the new causal path;
- receiver filesystem effect ownership or signed terminal receipts;
- exactly-once delivery or exactly-once filesystem effects;
- production-scale performance of the O(history) owner;
- complete retry classification, backoff, dead-letter, or wake scheduling;
- causal stability, compaction, tombstone collection, or safe old-device rejoin;
- anonymity, unlinkability, traffic-analysis resistance, or metadata hiding;
- externally trusted build provenance;
- full-project sanitizer, ThreadSanitizer, Windows, or formal verification
  coverage.
