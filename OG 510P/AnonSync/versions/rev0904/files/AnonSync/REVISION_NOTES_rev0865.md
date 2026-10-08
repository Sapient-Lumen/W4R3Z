# Revision notes: AnonSync rev0865

## Mission increment

Rev0865 turns the highest-priority recommendation from rev0864 into executable
C++: a pure causal replica oracle plus a deterministic network fault harness.
The point is not to declare the product convergent. The point is to give future
production code a concrete semantic reference that can distinguish causality,
unique event identity, concurrency, equivocation, preservation, crash state,
and bounded anti-entropy.

The heart of AnonSync is an **evidence-authorized convergence engine**. A local
observation should become authority only after its exact bytes, identity,
causal predecessor set, lifetime, resource budget, and durable cutpoint are
bound. Independent replicas must then derive the same visible result from the
same accepted immutable update set despite duplication, delay, reordering,
partitions, crashes, and concurrent writes. A deterministic tie-break alone is
not convergence if the system has already lost the identity of the writes being
tied.

## Principal C++ additions

1. Added `SyncReplicaModel`, an immutable dotted-operation reference model.
   Each operation binds folder, canonical path, file or tombstone value,
   content evidence, one `(device_id, epoch, counter)` dot, a sorted causal
   context, and a canonical SHA-256 operation identity.
2. Enforced a single-writer actor epoch. A local dot must be exactly the next
   counter after the actor's observed context. An incoming operation cannot
   mint in the local actor epoch, depend on an unowned future local event, or
   reuse an accepted dot for different semantic bytes.
3. Added failure-atomic remote admission, duplicate idempotence, pairwise cycle
   rejection, transitive-context checks, deterministic durable export/restore,
   operation-set digests, and visible-state digests independent of local replica
   identity.
4. Added a multi-value path projection. Causally superseded operations disappear
   from the visible set; concurrent maxima remain visible. The existing
   production conflict policy chooses one deterministic primary, while every
   visible nonprimary file is explicitly retained as a preservation candidate.
5. Added `SyncReplicaNetworkSimulator`, a deterministic in-memory harness for
   broadcasts, explicit anti-entropy, duplication, loss, reorder, directional
   and bidirectional partitions, crash/restart, and durable snapshots.
6. Made local mutation publication atomic in the harness: candidate model,
   broadcast batch, message identifiers, semantic-byte charges, and durable
   snapshot are staged before a no-throw live/durable commit. Queue failure does
   not consume a local dot.
7. Bounded the network independently by both pending-message count and stable
   semantic bytes. Count, identifier space, and semantic bytes are preflighted
   before mesh-sized `reserve` or operation copies, then rechecked at atomic
   queue publication.
8. Added a deterministic four-node, 720-step chaos corpus with partitions,
   message drops, duplicates, reverse-order delivery, crashes, restarts, 88
   generated operations, healing, and repeated full-mesh anti-entropy.

## Planner audit and correction

The production manifest planner previously treated equal version vectors with
different version digests as an ordinary conflict. That is unsafe. Equal causal
history says the peers claim the same event frontier; different bytes beneath
that exact frontier indicate missing event identity, counter reuse, state
corruption, or replica equivocation. Deterministic tie-breaking in that case
launders an identity failure into an apparently valid write winner.

Rev0865 therefore makes equal-lineage divergence fail closed with an explicit
repair-required error. The planner also builds into a private candidate and
publishes only after final shape validation. A multi-entry regression proves
that a late identity failure discards an already-built prefix instead of
leaking partial executable authority through the output parameter.

## Resource and exception-safety audit findings

Several defects were found while implementing the simulator rather than after
it was complete:

- The first local-mutation path could commit model history and then throw while
  enqueueing its broadcast. Publication is now staged before a no-throw commit.
- A message-count ceiling alone did not bound memory because every queued
  message owns a complete causal context. A stable semantic-byte budget now
  limits that second dimension.
- The first byte-budget implementation still constructed the entire
  anti-entropy batch before checking the budget. It could allocate the exact
  amplification it was intended to reject. Cardinality, identifier, and byte
  preflight now occur before mesh-sized allocation and payload copying.
- Bidirectional partition insertion could leave one direction installed if the
  second allocation threw. The first insertion is now rolled back on failure.
- The structural conflict audit encoded the old equal-lineage behavior. It was
  corrected to require fail-closed identity handling and failure-atomic plan
  publication rather than weakened or bypassed.

These corrections are deliberately embodied in runtime tests, not only source
text checks.

## What this proves

For coherent operations minted through the model, eventual delivery of the same
immutable operation set causes replicas to agree on both operation-set and
visible-state digests. The corpus exercises concurrent file versions, causal
successors, tombstone/file races, exact duplicates, reordered predecessors,
crash restoration, actor-epoch rotation, queue exhaustion, malformed durable
state, dot equivocation, cycles, and nontransitive contexts.

This is an executable **honest-operation convergence oracle**. It is useful as a
specification target for a future SQLite/network implementation and for
property-based differential tests.

## What this does not prove

Rev0865 does not establish Byzantine convergence. Two replicas that first admit
opposite same-dot forks may still retain different accepted sets because the
model rejects the second fork locally. Operation IDs are commitments, not
signatures. The model allows a causally coherent successor to arrive before its
missing predecessor; malformed or forged histories can therefore remain
arrival-order sensitive. Production needs shared immutable evidence,
deterministic validation/quarantine, and dependency reconstruction rather than
first-observed admission alone.

The oracle also makes no claim for SQLite transaction binding, payload/chunk
materialization, authenticated remote transport, peer enrollment or revocation,
key lifecycle, confidentiality, anonymity, metadata hiding, relay topology,
history compaction, tombstone garbage collection, causal stability, Merkle or
delta anti-entropy, hostile-input resilience, or production performance. Its
pairwise causality and visibility scans are intentionally simple and can be
quadratic. Folder-wide contexts also overstate dependencies across unrelated
paths.

## Highest-priority next integration

The next vertical slice should make the operation identity real across the
product boundary:

1. Define a canonical signed or otherwise authenticated operation envelope with
   dot, epoch, predecessor heads or hashes, payload digest, and membership/key
   epoch.
2. In one SQLite transaction, reserve the local counter, persist exact operation
   bytes and predecessors, update causal heads, and append an outbox record.
3. Reconstruct valid active state deterministically from the shared immutable
   update set; quarantine malformed forks and missing dependencies without
   making result selection depend on arrival order.
4. Exchange head/Merkle summaries over a real authenticated two-process
   transport and fetch missing operation nodes and payload chunks by immutable
   identity.
5. Differentially compare that implementation against `SyncReplicaModel` under
   the simulator's schedules, then extend the oracle for authenticated
   membership, fork evidence, compaction, and causal stability.

## Validation summary

- GCC 14.2, C++20, Debug, bundled SQLite 3.53.3: all-target graph passed.
- One uninterrupted CTest campaign passed **164/164**, including **49/49**
  registered structural audits.
- Final dependency closure is exactly `ninja: no work to do`.
- Focused GCC runtime passed **79** replica/network checks and **42** manifest
  conflict checks; the revised source audit passed **33/33**.
- Clang 17 with `-Werror` built the focused targets and integrated core; both
  focused executables passed.
- GCC 14 ASan+UBSan with leak detection and halt-on-error passed both focused
  executables; **5/5** selected compile commands and **2/2** link commands carry
  both sanitizer flags.
- Clang static analysis reported no diagnostics for the model, simulator, or
  focused test.
- The 11-file active patch replays exactly across all **319** active files with
  zero byte mismatch.
- The sealed rev0864 parent independently verifies **26/26** as a ZIP and
  **22/22** as a directory; archive SHA-256 is
  `816dfde3ca1d7916f6a62ce83c4bb915b5622414dd62817dca2fd04a2238eac8`.
