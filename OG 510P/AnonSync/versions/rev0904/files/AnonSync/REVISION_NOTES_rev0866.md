# Revision notes: AnonSync rev0866

## Mission increment

Rev0866 converts the principal limitation documented in rev0865 into executable
C++ semantics. A vector-clock summary is no longer enough to make an operation
active. Every operation now commits to its exact immediate predecessor hashes,
and the model separates retained immutable evidence from the active state
projected from that evidence.

The result is an arrival-order-independent reference owner for missing history,
same-dot forks, invalid causal envelopes, and transitive quarantine. Receiving
the same canonical evidence set yields the same active, pending, quarantined,
head, visible-path, and digest results regardless of delivery order.

This revision remains a bounded in-memory oracle. It does not claim production
persistence, authenticated actor authority, Byzantine resistance, real remote
transport, compact anti-entropy, payload materialization, or privacy.

## Principal C++ additions and refactors

1. Added canonical operation envelope v2 in
   `src/sync_replica_operation_codec.cpp`. The fixed binary encoding binds every
   semantic field, the dotted event, sorted vector context, and sorted exact
   predecessor IDs. Operation identity is SHA-256 of the canonical bytes.
2. Added a strict decoder that bounds total bytes and collection counts before
   allocation, rejects truncation/trailing bytes/noncanonical structure, derives
   the ID from exact input, revalidates semantics, and requires byte-for-byte
   canonical re-encoding.
3. Added `SyncReplicaEvidenceProjection`, a pure projector over immutable
   evidence. It classifies every envelope as active, pending missing dependency,
   same-dot fork, invalid dependent, invalid causal envelope, or dependency
   cycle.
4. Made same-dot fork handling arrival independent. Both conflicting envelopes
   are retained and neither is selected; a late fork revokes a previously active
   branch and quarantines descendants.
5. Made missing predecessors nonauthoritative. Pending evidence does not enter
   visible state, active digests, observed context, causal heads, or the parent
   set of local writes. Exact missing IDs are exposed for future dependency pull.
6. Enforced exact causal-envelope equality: the declared vector must equal the
   union of immediate parent closures, and the parent set must be a minimal
   causal antichain.
7. Replaced depth-dependent fixed-point rescans with a dependency worklist.
   Replaced pairwise parent-minimality scans with a per-actor top-two distinct
   parent coverage aggregate, then differentially checked it against a slow
   O(P^2) oracle.
8. Split payload ownership from projection indexes. Active envelopes are no
   longer copied into a second map; one immutable evidence store owns payloads,
   while active state contains IDs only.
9. Extended durable state with every retained evidence envelope and the exact
   local operation ID authorized at each local counter. Restore revalidates and
   reprojects rather than trusting persisted classifications.
10. Made local actor-epoch reuse fail closed. A late fork, missing authorized
    local ID, unauthorized local-namespace envelope, or inactive authorized
    local operation blocks further minting until explicit epoch rotation.
11. Refactored local publication to pre-reserve authority-vector capacity and
    stage one operation ID before evidence insertion, removing an O(local
    history) clone while preserving rollback around all allocating work.
12. Updated the network simulator to exchange all retained evidence, not only
    active operations, and added evidence-set convergence checks.

## Audit defects found during implementation

The final design differs materially from the first draft because focused audit
and sanitizer work exposed several hidden costs and semantic errors:

- The initial projector repeatedly rescanned unresolved nodes once per causal
  depth. A reverse-delivered chain made construction quadratic. A parent/child
  worklist now resolves each known edge once per projection.
- The initial projector revalidated and rehashed every previously admitted
  envelope on every insertion. Validation now remains at admission and restore
  trust boundaries; the pure projector consumes already-validated evidence.
- The initial model copied every active envelope, including all strings and
  vectors, into a second projection map. Active state is now an ID index over
  the one immutable evidence store.
- The first minimal-head check compared every parent pair. The optimized
  top-two-coverage algorithm removes that quadratic parent scan and is checked
  against an independent slow oracle.
- A node with one quarantined parent and one absent parent was first classified
  pending. That hid transitive quarantine and caused anti-entropy to request an
  irrelevant hash forever. Quarantine now dominates absence, and dependency
  requests include only evidence that can still activate.
- Local publication initially copied the complete local authorization sequence
  to obtain a strong guarantee. The final path stages only capacity and one ID,
  avoiding repeated O(local history) work.
- The new graph test initially lacked sanitizer link flags. CMake sanitizer
  target registration now instruments both compile and executable link
  commands. Its intentionally heavy graph corpus has a dedicated 60-second
  CTest timeout so sanitizer builds do not force a weaker ordinary test.
- A dedicated global-allocation fault injector now sweeps every throwing
  allocation point in local minting and remote admission. It proved exact
  durable-state rollback at 182 local and 160 remote cutpoints.

## Executable semantics

### Canonical identity

An operation contains folder ID, canonical relative path, file or tombstone
value, content digest and size for files, one actor/epoch/counter dot, a sorted
vector-clock context, and sorted immediate predecessor operation IDs. The
operation ID commits to the complete canonical envelope.

### Evidence admission

A well-formed remote envelope is retained before projection. Exact duplicates
are idempotent. The configured evidence limit includes active, pending, and
quarantined operations because all three consume attacker-influenced memory.
Admission is strongly exception-safe: a temporary evidence node is erased if
projection or derived-index construction throws.

### Projection

Same-dot forks quarantine every branch. Nodes with missing parents remain
pending unless already-known facts make activation impossible. Quarantine
propagates through exact edges and takes precedence over unresolved unrelated
hashes. A node activates only when every exact parent is active, its vector is
exactly justified by those parents, and no parent is causally redundant.

### Local mutation

A local mutation observes the active graph only, names its exact active heads,
uses the next local dot, and must project active before publication. Pending or
quarantined remote evidence cannot contaminate the new local frontier. Any
unrecognized evidence in the local actor epoch or invalidation of an authorized
local operation closes minting authority for that epoch.

### Restore

Durable evidence is strictly sorted by operation ID. Restore validates canonical
bytes and folder binding, verifies the local ID sequence against exact actor
counters, reconstructs all classifications and heads, and recomputes local epoch
safety. Pending and fork evidence survive crashes.

### Visibility and convergence

Only active operations participate in multi-value path visibility and the
existing deterministic primary/preservation policy. The model exposes separate
active-operation, retained-evidence, and visible-state digests. The simulator
heals by disseminating all evidence, so replicas can converge not only on a
winner but on the facts that justify activation and quarantine.

## Focused validation surface

The new graph corpus exercises:

- canonical decode boundaries and allocation preflight;
- missing predecessor pending/late activation;
- all small-chain delivery permutations;
- opposite fork arrival orders and late revocation;
- quarantine propagation and quarantine-over-missing precedence;
- causal-envelope mismatch and redundant-parent rejection;
- local authority restore corruption;
- a 384-operation reverse chain;
- a 128-root fan-in merge; and
- 192 generated branching candidates checked against a slow differential
  minimality oracle.

The three focused executables contain 2,050 runtime assertions in total: 67
network/model checks, 1,288 graph/codec/projection checks, and 695 allocation
atomicity checks spanning 342 injected throwing-allocation cutpoints. They pass
under GCC, Clang 17 with `-Werror`, and GCC 14 ASan+UBSan with leak detection and
halt-on-error. Four focused production translation units produce no Clang
static-analyzer diagnostics. A release-harness audit also marked the
integration-scale sync-domain selftest `RUN_SERIAL`: it owns broad process,
SQLite, filesystem, and daemon fixtures and had stalled unrelated work under an
eight-way CTest schedule despite passing quickly alone. The complete release
registry then passes 166/166 in one parallel invocation.

The full release gate, exact test registry, source replay, sanitizer command
proof, package verification, and parent lineage are recorded under
`REVISION_EVIDENCE/rev0866/`.

## What this proves

Within the model's limits and unauthenticated evidence universe, the same set of
valid canonical envelopes produces the same deterministic evidence
classification and visible state independent of arrival order. Missing exact
history does not become active. Same-dot fork selection is not first-observed.
Late evidence can reclassify prior nodes, and crash restore recomputes the same
verdict. The optimized parent-minimality classifier agrees with an independent
slow oracle across the recorded generated corpus.

This is a stronger executable reference for a future SQLite/network
implementation.

## What this does not prove

Hashes do not authenticate actors. A hostile sender can fabricate a same-dot
fork and suppress honest history in this unauthenticated model. There is no
membership or trust CRDT, key enrollment/rotation/revocation, signed envelope,
production transaction, real transport, chunk protocol, incremental projector,
compaction, stable frontier, garbage collection, anonymity, confidentiality, or
metadata-hiding design.

The global projector is linear-ish per run in retained graph material, but the
model reruns it after every insertion; long construction workloads remain
superlinear. Full-set anti-entropy and durable export copy complete histories.
These are reference-oracle choices, not production performance claims.

The production manifest/database/wire paths still do not use this operation
envelope. Product convergence therefore remains unclaimed until one operation
is persisted, transported, restored, and materialized through a real vertical
slice and differentially compared with this owner.

## Online research synthesis

Official Git documentation reinforces the value of content-addressed exact
parent IDs and heads. Official Automerge documentation and source demonstrate
SHA-256 change identity, dependency hashes, complete history, and queuing of
changes that are not causally ready. Byzantine-CRDT literature supports
immutable evidence and deterministic reconstruction but also makes clear that
actor authorization and malicious behavior require an explicit fault model.
SQLite's official WAL documentation records a rare WAL-reset corruption bug in
3.7.0 through 3.51.2, fixed in 3.51.3 on 2026-03-13. This cube bundles 3.53.3,
so it is beyond that fix, but production still needs an asserted runtime/source
version and crash/concurrent-checkpoint testing for its selected journal mode.
Very recent June/July 2026 preprints on evidence/projection separation, trust
state, and Blocklace memory exhaustion are included as speculative leads, not
implementation authority. The memory-exhaustion work particularly reinforces
that evidence retention requires admission, dependency, byte, time, and storage
budgets even when the graph semantics converge.

Full URLs and cautions are recorded in
`REVISION_EVIDENCE/rev0866/RESEARCH.md` and
`CAUSAL_HASH_GRAPH_AUDIT_rev0866.md`.

## Highest-priority next integration

Implement one canonical authenticated operation through a real SQLite and
transport cutpoint:

1. sign or MAC the exact v2-style envelope under an actor/key and membership
   epoch;
2. atomically reserve the local dot, persist bytes/parents/signature, replace
   heads, and append outbox intent;
3. restore and deterministically project inbox/evidence without trusting cached
   active flags;
4. exchange heads and missing nodes over an authenticated two-process channel
   with count/wire/dependency/time budgets;
5. verify payload chunks and final filesystem publication against the operation
   ID and content digest; and
6. compare every crash/reorder/duplicate result with this pure projector.

After that slice is correct, add an incremental affected-subgraph projector and
trust-governance state, each differentially checked against a pure reference.
