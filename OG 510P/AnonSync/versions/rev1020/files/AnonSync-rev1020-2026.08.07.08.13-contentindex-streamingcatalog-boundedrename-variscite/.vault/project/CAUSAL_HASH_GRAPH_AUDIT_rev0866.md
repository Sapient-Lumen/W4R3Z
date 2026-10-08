# Causal hash-graph audit: AnonSync rev0866

## Executive judgement

Rev0866 corrects the most dangerous semantic gap left by rev0865: the reference
model previously let a causal summary stand in for possession of the exact
history it summarized. A syntactically coherent successor could arrive while
one or more alleged predecessors were absent, enter accepted state, and then be
inherited by later local writes. At that point a vector clock had become
unearned authority. A later predecessor could reveal a fork or an impossible
causal shape only after visible state and new local history had already depended
on it.

The correction is a canonical, content-addressed predecessor graph plus a pure,
arrival-order-independent evidence projector. Every well-formed envelope is
retained as evidence; only envelopes whose exact parents are present, active,
minimal, and causally consistent enter active state. Missing parents remain
pending. Same-dot forks select neither branch. Invalid or fork-dependent
subgraphs are quarantined. Re-running the projector over the same immutable
evidence set yields the same classification regardless of delivery order.

This is a substantial improvement in executable semantics, not a production
sync protocol. Hashes bind bytes but do not prove who was authorized to mint
those bytes. The model still lacks signatures or MACs, membership governance,
SQLite transaction binding, real peer transport, payload materialization,
compact anti-entropy, incremental projection, compaction, and a privacy threat
model.

## The heart of the mission

AnonSync should be understood as an **evidence-authorized convergence engine**.
File copying is an effect at the edge of that engine, not its defining
property. The central invariant is:

> Exact, authorized, resource-bounded evidence must cross one durable cutpoint;
> equivalent evidence and trust state must then produce equivalent active state
> without depending on arrival order, process history, local orientation, or
> unaudited guesses about missing history.

That invariant has several inseparable parts:

1. **Identity.** One update has one canonical byte representation and one
   immutable identity. A vector, timestamp, filename, or winner policy is not a
   substitute for event identity.
2. **Causality.** An update names the exact immediate history it extends. A
   summary may accelerate comparisons, but it cannot prove that the named
   history exists or is valid.
3. **Authority.** The actor/key epoch and membership state must establish who
   was allowed to mint the update. Content addressing detects byte changes; it
   does not authenticate principals.
4. **Durability.** Counter reservation, exact envelope bytes, predecessor/head
   updates, payload commitments, and retry/outbox intent need one recoverable
   transactional cutpoint.
5. **Projection.** Retained evidence and active state are different products.
   Validation, quarantine, revocation, and conflict preservation must be pure
   functions of evidence plus trust state.
6. **Dissemination.** Peers exchange immutable nodes and payload chunks within
   count, byte, dependency, time, and retry budgets. Delivery order is an input
   schedule, not semantic authority.
7. **Privacy.** Anonymity and metadata protection require an explicit adversary
   model and protocol. They cannot be inferred from hashing, encryption at
   rest, or the project name.

The repository is already unusually rich in local authority wrappers, SQLite
lifetime controls, crash-state documents, bounded file handling, and source
structural audits. The mission now requires those pieces to be composed through
one real end-to-end operation path. Continuing to add isolated wrappers without
that vertical slice would recreate the assurance inversion identified in
rev0864: strong local claims surrounding a missing distributed core.

## Severe defect corrected: unearned causal authority

Rev0865 represented each operation with a dotted event and a vector-clock
context. It could reject obvious local inconsistencies, but it did not require
exact predecessor operations to be present before the operation influenced the
accepted frontier. This created four related hazards:

- a forged or incomplete successor could become visible while its alleged past
  was absent;
- a later local operation could observe that successor and permanently encode
  its unverified context;
- opposite arrival orders could admit opposite sides of a same-dot fork; and
- crash persistence could preserve the first-observed choice rather than the
  complete evidence needed for a deterministic verdict.

The core conceptual mistake was treating a compact causal summary as both
**knowledge** and **proof**. A vector answers “which actor counters does this
node claim to include?” It does not answer “which exact immutable nodes were
included, do I possess them, did they authenticate, and are they mutually
consistent?”

Rev0866 adds `predecessor_operation_ids` to the canonical operation envelope.
These IDs are strictly sorted, unique SHA-256 digests of the exact versioned
operation bytes. Local writes name the current active graph heads. A receiver
can now distinguish three facts that rev0865 conflated:

- the envelope claims a causal closure;
- the exact direct parent IDs are or are not present; and
- the present parent envelopes do or do not justify the claimed closure.

## Canonical operation envelope v2

`sync_replica_operation_codec.cpp` owns a fixed binary format with a versioned
magic string, big-endian 64-bit lengths and integers, one-byte value kind,
length-framed strings, sorted vector-clock entries, and sorted exact parent
hashes. The operation ID is SHA-256 of these bytes, excluding the ID field
itself.

The decoder is deliberately stricter than a normal convenience parser:

- total canonical bytes are bounded before parsing;
- untrusted collection counts are checked against configured limits;
- counts are also checked against the minimum bytes still available before
  `reserve`, preventing count fields from causing disproportionate allocation;
- truncation, trailing bytes, unknown kinds, malformed values, noncanonical
  clocks, noncanonical parent sets, and self-parent references fail closed;
- the derived digest is installed as `operation_id`;
- semantic validation is rerun; and
- re-encoding must reproduce the exact input bytes.

The final equality check prevents future decoder permissiveness from silently
creating multiple byte representations for one semantic value. It is expensive
but appropriate in this reference owner. A production wire path may optimize
only after proving equivalent canonicality and byte limits.

## Evidence is not active state

The model now owns each immutable envelope exactly once in `evidence_by_id_`.
Derived state is represented by operation-ID indexes:

- `active_operation_ids_`;
- `evidence_state_by_id_`; and
- `causal_head_operation_ids_`.

This separation matters semantically and operationally. Pending or quarantined
bytes must survive restart and anti-entropy because they may be necessary to
explain a fork, request a missing dependency, or keep an invalid branch from
being accepted later. At the same time, those bytes must not contribute to
visible paths, the active vector frontier, new local predecessor heads, or the
active operation-set digest.

The earlier draft copied every active envelope into a second map on every
projection. That duplicated strings, vectors, and payload commitments in memory
and turned each admission into an avoidable O(active payload bytes) copy. The
final implementation indexes active IDs over the immutable evidence store,
removing that whole copy layer.

## Deterministic evidence classification

The pure projector classifies every retained operation as one of:

- `Active`;
- `PendingMissingDependency`;
- `QuarantinedDotFork`;
- `QuarantinedDependency`;
- `QuarantinedCausalEnvelope`; or
- `QuarantinedDependencyCycle`.

### Same-dot forks

A dot is a single-writer event position. If two distinct canonical envelopes
claim the same `(device_id, epoch, counter)`, both are retained and neither is
active. This verdict is computed from the complete evidence map, so receiving
A then B produces the same result as B then A. A late fork can revoke an
operation that was previously active, and quarantine propagates through exact
dependency edges.

This is stronger than “reject the second arrival,” but it remains deliberately
conservative. Without authenticated actor keys, anyone able to inject a validly
shaped envelope can fabricate another actor's dot and suppress an honest branch.
Even with authentication, an authorized malicious actor can fork and poison its
descendants. Production therefore needs identity, membership, revocation, and
trust policy in addition to deterministic evidence handling.

### Missing dependencies

An operation with absent direct parents remains pending and does not enter the
active frontier. When the exact parents arrive, global reprojection can activate
it or quarantine it. The model exposes the absent IDs that still block evidence
which could become active, allowing a future dependency pull protocol to ask for
specific nodes rather than treating vector summaries as possession.

The projector also rejects irreversible defects early. A missing hash cannot
repair a context that already fails to dominate a known parent's closure, nor
can it make a known parent set minimal when one known parent already covers
another known parent's dot.

### Quarantine dominates absence

A second audit pass found a subtle classification error in the first draft. A
node with one known-quarantined parent and one absent parent was labeled pending.
That stopped transitive quarantine and caused `missing_predecessor_operation_ids`
to request a hash that could never make the node active. The final precedence is
fail-closed: once any exact parent is known unusable, the child is quarantined
regardless of other missing parents. Dependency requests are limited to pending
subgraphs with a remaining path to activation.

### Exact context and minimal heads

For an operation to activate, its declared vector context must exactly equal the
component-wise union of every direct parent's context plus each parent's own
dot. Its direct parent set must also be an antichain: no named parent may already
be in another named parent's causal closure.

The first correct implementation compared parents pairwise and risked
O(P^2) work for a P-parent merge. The final projector computes, per actor, the
highest coverage from two distinct parent indexes. For each candidate parent,
the best coverage supplied by any *other* parent determines redundancy. This
turns parent-minimality work into a pass over parent causal metadata rather than
a pairwise parent scan. A deterministic differential corpus compares the
optimized answer against a deliberately slow O(P^2) oracle.

## Dependency worklist rather than depth rescans

The first projector draft repeatedly rescanned unresolved evidence until a
fixed point. A reverse-ordered chain made that depth-dependent and quadratic.
The final implementation builds known parent-to-child edges and unresolved
parent counts, then classifies ready nodes from roots outward. This makes one
projection proportional to retained vertices, exact dependency edges, and the
causal metadata traversed for parent aggregation, plus ordered-container lookup
costs.

That does **not** make model construction linear overall. The reference model
still reprojects the entire retained set after every insertion. Building a long
history is therefore superlinear, and contexts themselves may grow with actor
breadth. This is acceptable for a bounded semantic oracle, not for production.
The next implementation should cache reverse edges, dot groups, causal
aggregates, and affected descendants, while differentially proving every
incremental result against this pure global projector.

## Failure atomicity and durable authority

Remote admission validates an exact envelope, temporarily inserts one evidence
node, computes a complete candidate projection, computes local epoch safety,
and only then swaps the derived indexes. Any exception erases the temporary map
node and leaves the prior model unchanged.

Local mutation has a stricter obligation because it consumes single-writer
counter authority. Rev0866 stages vector capacity and the exact local operation
ID before evidence insertion. Projection must classify the new envelope active,
and the complete local authority sequence must remain coherent. Only then are
the ID sequence, active indexes, heads, and counter published. The refactor
removes the earlier O(local history) authorization-vector clone while keeping
rollback around every allocating step.

Durable state now stores:

- every evidence envelope, strictly sorted by operation ID;
- the last local counter; and
- the exact operation ID authorized at each local counter.

Restore revalidates every canonical envelope, reconstructs the evidence map,
verifies the local ID-to-dot bindings, recomputes projection rather than trusting
persisted derived state, and recomputes whether the local actor epoch is safe to
mint. A late fork or unauthorized future dot in the local namespace survives
restart and closes that epoch. Rotation to a new epoch is explicit.

The in-memory durable assignment is still only a simulator cutpoint. It does
not prove atomic SQLite reservation, operation insertion, head replacement,
outbox publication, or payload/filesystem effects.

## Network and anti-entropy implications

The simulator now disseminates all retained evidence, not only active
operations. Otherwise a replica could converge on visible state while silently
losing the fork or malformed evidence that justifies why another branch is
inactive. Tests deliver successors before predecessors, crash while evidence is
pending, restart, deliver the missing roots, and verify activation and equal
evidence/active/visible digests after healing.

Full-history anti-entropy remains intentionally wasteful. It copies every
retained envelope to every destination and globally reprojects after each
delivery. Count and semantic-byte budgets prevent unbounded queue
amplification, but this is not a wire protocol. Production should exchange
content-addressed heads or graph summaries, request only missing nodes, stream
within negotiated limits, and persist inbox/outbox progress transactionally.

## Audit and test surface

The focused corpus covers the following boundaries:

- exact canonical round-trip, digest binding, truncation, trailing bytes,
  noncanonical parent sets, impossible collection counts, and byte ceilings;
- missing predecessor admission, absence from visible state, late activation,
  idempotence, and crash persistence;
- all delivery permutations for a small dependency chain;
- opposite same-dot fork arrival orders, late active-state revocation, retained
  fork evidence, and transitive quarantine;
- quarantine precedence over unrelated missing dependencies;
- malformed causal summaries and redundant direct parents;
- local namespace fork and future-dot reuse, restart persistence, and epoch
  rotation;
- a reverse-delivered 384-operation chain;
- a 128-root merge/fan-in case;
- 192 deterministic mixed branching candidates compared with the slow
  parent-minimality oracle; and
- exhaustive allocation-failure rollback across 182 local-mint and 160 remote-
  admission cutpoints; and
- the broader deterministic network chaos schedule inherited from rev0865.

The three focused binaries execute 2,050 checks and pass under GCC, Clang
`-Werror`, and GCC AddressSanitizer plus UndefinedBehaviorSanitizer. The four
changed/new production translation units produce no Clang static-analyzer
diagnostics. The graph stress test keeps its full corpus under a dedicated
60-second CTest timeout rather than reducing coverage for sanitizer speed. The
release evidence records exact commands and scopes; no full-project sanitizer
claim is made.

The full-registry audit also exposed a test-harness ownership defect. The large
sync-domain selftest owns process, SQLite, filesystem, socket, daemon, and
temporary-path fixtures but was allowed to overlap unrelated tests. Under an
eight-way CTest run it stalled while every isolated execution remained fast and
clean. Rev0866 marks that integration test `RUN_SERIAL`; this is a scheduling
authority declaration, not a relaxation of any assertion or timeout.

## What has gone severely wrong or wasteful in the cube

### 1. Assurance has often accumulated horizontally instead of vertically

The repository contains many careful ownership types and lexical audits, but
few product paths compose identity, storage, transport, recovery, and visible
filesystem effect. This creates a risk that line-count and audit-count growth
look like product maturity while the defining distributed invariant remains
unimplemented. The correction is not to discard the local hardening; it is to
select one operation and drive it through every layer with executable crash and
network tests.

### 2. Structural audits can fossilize semantic bugs

Rev0865 already found a source audit that required equal-lineage divergence to
be treated as an ordinary conflict. A lexical test had become authority for the
bug. Structural audits are useful for narrow ownership and registration
boundaries, but they should not define distributed semantics. Pure executable
models, differential tests, and state-machine invariants must remain primary.

### 3. Compact metadata has repeatedly been allowed to imply evidence

The production manifest still uses vector lineage and caller-provided scan
counters rather than immutable operation nodes. Rev0866 fixes the reference
model only. Until the production database and wire format persist exact
predecessor-bound envelopes, the product can still make decisions on summaries
whose supporting events are absent or ambiguous.

### 4. Reference implementation work exposed avoidable copying

The initial projection duplicated every active operation payload, repeatedly
revalidated already-admitted hashes, rescanned by graph depth, and compared
parent heads pairwise. Those costs were not just micro-optimizations: they made
adversarial breadth and reverse-order input disproportionately expensive. The
final reference owner removes the active payload copy, validates at trust
boundaries, uses a dependency worklist, and uses an aggregated minimality test.

### 5. The remaining model is still intentionally global and superlinear

Every insertion recomputes the whole projection; visible-path calculation scans
active history; full-mesh anti-entropy copies full evidence; and durable export
copies every envelope. Those choices keep semantics inspectable, but none should
quietly migrate into a daemon. Performance work should begin only with a
retained pure oracle and differential corpus, so optimization cannot change
fork, pending, quarantine, or preservation semantics.

### 6. Authentication and trust governance are the largest security vacuum

A SHA-256 ID commits bytes but does not establish actor authority. The current
fork rule is therefore a trivial denial-of-service target under hostile input.
A production design needs signed actor/key epochs or an equally explicit
authentication construction, folder membership state, key rotation, revocation,
recovery, and a deterministic rule for how trust changes reclassify retained
evidence. Recent governance-oriented CRDT research is suggestive, not a ready
answer.

### 7. The name still overclaims privacy

The cube has no demonstrated anonymous routing, unlinkable discovery,
metadata-minimizing membership protocol, traffic-analysis defense, cover
traffic, relay trust model, or global-passive-adversary analysis. A secure direct
peer vertical slice is the nearer prerequisite. Privacy work should then begin
with adversaries and observable metadata, not with a transport technology
chosen in advance.

## Online research and architectural implications

Research was reviewed on 2026-07-20. These sources inform design; they do not
prove AnonSync implements the cited systems.

### Git content-addressed parent objects

The official `git-commit-tree` documentation states that a commit can have any
number of parents, each `-p` names a parent object ID, and the commit
encapsulates all parent IDs. The current manual page is marked updated for Git
2.55.0 on 2026-06-29.

https://git-scm.com/docs/git-commit-tree

Implication: content-addressed exact parents and a set of heads are a
well-established way to represent history possession. Git does not supply CRDT
conflict semantics, actor authorization, or bounded peer anti-entropy, but its
object model reinforces the distinction between exact ancestry and a summary.

### Automerge change hashes, dependencies, and queued changes

The official Automerge binary-format specification describes changes with a
possibly empty predecessor set, identifies each change by SHA-256 of its binary
representation, and stores complete change history in a document. The official
Rust source maintains changes indexed by hash and queues changes that are not
causally ready until dependencies are present.

https://automerge.org/automerge-binary-format-spec/

https://automerge.org/automerge/src/automerge/automerge.rs.html

Implication: exact hash dependencies, heads, retained not-yet-applicable
changes, and graph-oriented missing-dependency discovery are practical CRDT
patterns. AnonSync's file/tombstone policy, single-writer epochs, quarantine,
resource model, and future trust layer remain its own design obligations.

### Byzantine CRDT direction

Martin Kleppmann's PaPoC 2022 material describes adapting CRDT principles for
Byzantine faults while retaining strong eventual consistency goals.

https://martin.kleppmann.com/2022/04/05/bft-crdt-papoc.html

Implication: immutable hash-linked operation evidence is relevant, but a hash
DAG is not by itself Byzantine safety. Authentication, allowed operations,
malicious omission, equivocation, and access-control changes must all be part of
the model.

### SQLite WAL durability posture

SQLite's official WAL documentation now records a rare WAL-reset data race that
could corrupt a database when multiple connections wrote or checkpointed at a
tightly constrained instant. It affected SQLite 3.7.0 through 3.51.2 and was
fixed in 3.51.3 on 2026-03-13.

https://sqlite.org/wal.html

https://sqlite.org/releaselog/3_51_3.html

AnonSync currently bundles SQLite 3.53.3 (`SQLITE_VERSION_NUMBER` 3053003), so
the checked-in amalgamation is newer than the fix. That is useful evidence, not
a complete durability claim: the production gate should assert the actual
linked runtime/source ID, keep database and WAL sidecars together, select and
document journal/synchronous/checkpoint policy, and inject crashes plus
concurrent writer/checkpointer schedules at the real operation transaction.

### Recent evidence/projection and trust-governance work

Two July 2026 preprints are especially aligned with the architecture exposed by
this audit:

- “Byzantine Accountability Without Consensus: Strong Eventual Consistency for
  Non-Associative, Stochastic, Robust Aggregation” discusses a converged
  evidence/data product and deterministic pure projection.
  https://arxiv.org/html/2607.10305v1
- “A Dual-CRDT Architecture for Decentralized Trust Governance and Evolution”
  explores separating trust governance state from application data and deriving
  state deterministically.
  https://arxiv.org/html/2607.06068v1

Implication: retaining evidence separately from active projection and treating
trust as replicated state are promising directions. Both papers are very recent
and should be treated as research leads, not settled standards or production
blueprints. Rev0866 implements neither consensus-free accountability nor a
trust CRDT.

Two additional June/July 2026 preprints sharpen the resource and trust warning:

- “Decoupling Trust in Byzantine CRDTs” studies post-compromise trust handling
  without discarding causal evidence.
  https://arxiv.org/abs/2606.31759
- “Memory-Exhaustion Attack on the Blocklace Byzantine-Repelling Conflict-Free
  Replicated Data Type” describes retained adversarial graph material as a
  memory-denial surface.
  https://arxiv.org/abs/2607.15185

Implication: convergence of immutable evidence does not imply safe unbounded
retention. Production admission needs authenticated authority plus hard limits
on envelope bytes, parent fan-in, unresolved dependencies, per-peer retained
evidence, traversal work, disk growth, and retry lifetime. These preprints are
very recent and are recorded as design pressure rather than settled authority.

## Recommended production vertical slice

The next revision should stop broadening the oracle and bind one real operation
through the product stack:

1. **Canonical authenticated envelope.** Add a signature or documented MAC
   construction over version, folder/object identity, actor/key epoch, unique
   event, exact parent hashes, value commitment, membership epoch, and resource
   limits. Specify canonical bytes independently enough for test vectors.
2. **SQLite evidence schema.** Store exact envelope bytes, operation ID, actor
   dot, parent edges, authentication material, evidence state, and payload
   commitment. Enforce immutable uniqueness and bounded cardinalities.
3. **Atomic local mint.** In one transaction, reserve the next counter, freeze
   canonical bytes and signature, insert the operation and parent edges, replace
   heads, and append an outbox record. Crash injection must cover every
   statement boundary and commit outcome.
4. **Deterministic restore/project.** Load evidence without trusting cached
   active flags, validate authentication and membership epoch, reconstruct the
   graph, and compare the result with this pure model. Cached incremental state
   may be used only when recomputation proves it.
5. **Two-process transport.** Send digest-bound canonical envelopes over a real
   authenticated connection, persist inbox/outbox retry state, handle duplicate,
   reorder, reconnect, truncation, and dependency pull, and enforce wire/count/
   dependency/time budgets before allocation.
6. **Payload materialization.** Fetch chunks by immutable digest, verify the
   complete file, bind final filesystem publication to the active operation ID,
   and preserve concurrent nonprimary files until policy-authorized cleanup.
7. **Incremental projector.** Maintain affected-subgraph indexes and compare
   every mutation against the global reference projector under generated DAGs,
   late forks, trust changes, and crashes.
8. **Trust lifecycle.** Model enrollment, key rotation, lost-counter recovery,
   revocation, malicious authorized forks, and reclassification after trust
   changes. Only then consider a Byzantine or multi-writer security claim.

## Explicit nonclaims

Rev0866 does not claim:

- authenticated operation provenance;
- resistance to forged-dot denial of service;
- arbitrary Byzantine convergence or accountability;
- a membership, trust-governance, key-rotation, or revocation protocol;
- a production SQLite operation/outbox cutpoint;
- a real remote transport or compact Merkle/delta anti-entropy protocol;
- payload/chunk storage or filesystem publication bound to operation identity;
- incremental or production-scale projection performance;
- history compaction, causal stability, tombstone garbage collection, or secure
  deletion;
- confidentiality, anonymity, metadata hiding, forward secrecy, or
  post-compromise security;
- formal verification; or
- full-platform, full-project sanitizer, ThreadSanitizer, release-build, or
  Windows runtime coverage.

## Audit conclusion

Rev0866 moves the convergence model from “dotted operations with useful
invariants” to “exact hash-linked evidence with deterministic applicability.”
It eliminates a real arrival-order authority defect and removes several
wasteful projection designs discovered during implementation. The strongest
remaining recommendation is unchanged in spirit but now much more concrete:
make this envelope real in SQLite and on a two-process authenticated wire, then
use the pure projector as the differential authority. Further isolated local
hardening without that vertical slice would provide less mission value than
integrating the evidence path end to end.
