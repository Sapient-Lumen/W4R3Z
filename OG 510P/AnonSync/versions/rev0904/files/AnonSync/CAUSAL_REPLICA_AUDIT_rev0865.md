# Causal replica audit: AnonSync rev0865

## Audit question

What must be true before AnonSync can honestly claim that two devices converge,
and where did the existing implementation confuse deterministic behavior with
valid replicated semantics?

## The heart of the mission

AnonSync is not principally a file copier, a digest library, or a collection of
SQLite safety wrappers. Its core mission is to turn observations into bounded,
durable, causally meaningful operations and then ensure that independent
replicas derive the same user-visible state from the same authorized evidence.

That mission has four inseparable propositions:

1. **Unique update identity.** A write must have an identity that cannot be
   silently reused for different bytes. Causal context and update identity are
   related but not interchangeable.
2. **Atomic durability and publication.** The update, its local counter, its
   payload commitment, its causal predecessors, and its dissemination intent
   must cross one recoverable cutpoint.
3. **Deterministic reconstruction.** Given the same accepted immutable update
   evidence, every replica must derive an equivalent visible state, including
   explicit treatment of concurrent files and tombstones.
4. **Fault-tolerant dissemination.** Delay, duplication, reordering, partitions,
   restart, and retry must not change the semantic result or exceed declared
   resource budgets.

Privacy and anonymity are a fifth product-level obligation, but they cannot be
made meaningful until the replicated operation protocol exists. Encrypting an
ill-defined state machine only hides an ill-defined state machine.

## Severe finding 1: equal lineage was used as two different identities

The legacy manifest representation uses a version vector as `lineage`. The
planner compared two entries with equal vectors but different version digests
and passed them to the ordinary deterministic conflict resolver.

That behavior was attractive because it always selected a winner. It was also
semantically wrong. A version vector answers a causal-order question: which
replica counters are included in the history? It does not provide a unique name
for each write. If both peers claim exactly the same history yet bind different
bytes to it, at least one invariant has failed:

- a device reused a counter;
- state was rewritten without minting a new event;
- two writers shared one purported single-writer identity;
- an operation was corrupted; or
- a peer equivocated.

Calling the values concurrent conceals that evidence. Rev0865 fails closed and
requires repair. The new dotted model separates each event's dot from its causal
context so ordinary concurrency can be represented without overloading the
vector.

## Severe finding 2: planner failure could expose a valid-looking prefix

`build_sync_manifest_diff_plan` wrote directly into its caller-visible output.
A late failure could therefore leave earlier entries populated. Even when a
caller checks the returned error today, partial authority in an output object is
a future misuse hazard and violates the repository's own failure-atomic style.

The function now clears the output, builds an unpublished candidate, validates
its final shape, and move-publishes only on success. The regression deliberately
creates an earlier local-only entry followed by equal-lineage divergence and
requires the output to remain completely empty.

## Severe finding 3: local state and network publication initially had two
## cutpoints

The first simulator implementation mutated the local model and then attempted
to enqueue peer messages. Queue allocation or budget failure could throw after
the operation existed locally. A caller would see failure even though a local
dot had been consumed and durable history had changed.

Rev0865 uses a candidate model. It preflights cardinality, stages the operation,
builds and charges the complete broadcast, derives the durable snapshot, and
atomically inserts the message batch. Only then does a no-throw commit replace
live and durable state. A rejected enqueue leaves the model, durable snapshot,
message IDs, queue charges, and next local counter unchanged.

This is a simulator cutpoint, not yet the production SQLite cutpoint. It defines
what the production transaction must eventually preserve.

## Severe finding 4: a count limit was mislabeled as a memory limit

A queued message owns source and destination IDs plus an entire operation and
causal context. One million small messages and one million maximum-context
messages are not equivalent resource claims. A count-only queue ceiling left a
large uncontrolled dimension.

The simulator now maintains a second deterministic semantic-byte budget. The
weight counts fixed-width scalar values and every owned string byte. It is
explicitly not a promise about allocator overhead or wire encoding. That makes
it stable across platforms and suitable for invariant tests while remaining an
honest lower-level accounting unit.

## Severe finding 5: budget enforcement happened after amplification

The first semantic-byte correction still gathered operation snapshots,
reserved a mesh-sized vector, and copied every operation before queue
publication checked the budget. A failure path could perform the exact
amplification the bound was supposed to prevent.

The refactor now performs:

- batch cardinality and message-ID preflight before source-set copies;
- exact semantic-weight accumulation before mesh-sized `reserve` and payload
  copies;
- a second complete preflight after the batch is staged; and
- rollback of every inserted map node if queue publication throws.

The focused corpus proves both count and semantic-byte denial with no visible
batch prefix and verifies that dropping or delivering messages releases the
exact charge.

## Severe finding 6: bidirectional partition mutation lacked a strong guarantee

Installing a two-way partition requires two set insertions. If the second
allocation threw after the first succeeded, the simulator could report failure
while retaining a one-way partition. The first insertion is now erased when the
second insertion throws, unless that direction pre-existed.

## Severe finding 7: an audit encoded the bug

The lexical conflict-convergence audit explicitly expected equal-lineage
values to become deterministic conflicts. When runtime semantics were fixed,
the full registry correctly failed because the audit was stale. The solution
was not to suppress the audit. It was updated to require the new fail-closed
branch, forbid conflict resolution inside it, and require private candidate
publication plus a late-failure regression.

This episode illustrates a broader risk in the cube: structural audits can
freeze implementation accidents. Runtime semantic tests and reference models
must remain primary; lexical checks should guard narrow integration properties,
not define distributed semantics.

## Executable reference semantics

### Operation identity

`SyncReplicaOperation` binds:

- folder ID and canonical path;
- file or tombstone kind;
- file size and lowercase content SHA-256 for files;
- one actor `(device_id, epoch)` and positive counter dot;
- a strictly sorted, unique causal context; and
- a domain-separated, length-framed canonical SHA-256 operation ID.

Within one actor epoch, a dot must be exactly one greater than that actor's
context counter. Epoch rotation provides a new mint namespace after loss or
intentional reset; it is not automatically generated by this model.

### Admission

Exact duplicates are idempotent. A known operation ID with different semantic
bytes is treated as a digest-collision invariant failure. A reused dot with a
different operation ID is rejected as equivocation/counter reuse. Remote
operations cannot mint inside the local actor epoch or claim a future local
event that the replica never minted.

Pairwise checks reject causal cycles and contexts that claim an existing
predecessor without dominating that predecessor's own context. Admission is
strongly exception-safe: the operation map and dot map either both gain one row
or neither changes.

### Visibility

For each path, every operation causally covered by another same-path operation
is superseded. The remaining maximal operations are the visible multi-value
set. A deterministic total policy chooses a primary:

- tombstones beat files in a concurrent file/tombstone race to prevent silent
  resurrection;
- equal-kind values use immutable operation-ID order; and
- every visible nonprimary file remains a preservation candidate.

The primary is a projection, not deletion of history. The model retains all
immutable operations.

### Restore

Durable state must list operations strictly sorted by operation ID. Restore
revalidates every operation, rejects duplicate IDs or dots, requires every local
counter from 1 through `last_local_counter`, rejects gaps, and rejects references
to a future local event. The restored operation and visible-state digests are
recomputed rather than trusted.

### Network schedules

The simulator can enqueue normal broadcasts or full-set anti-entropy, duplicate
and drop individual messages, deliver oldest or newest first, block directional
links, crash a node to its durable snapshot, and restart through model restore.
The deterministic chaos scenario deliberately combines all of these and then
heals and exchanges complete state until all replicas agree.

## Where the model remains intentionally incomplete

### First-observed fork admission is not Byzantine convergence

If an attacker creates two validly shaped operations with the same dot and
sends fork A first to one replica and fork B first to another, each rejects the
other fork after its first admission. Their accepted update sets differ. The
current model detects local equivocation but does not provide a globally
arrival-independent fork verdict.

A production design should retain both signed/hash-linked pieces of evidence,
derive validity or quarantine from the complete shared evidence set, and make
active-state reconstruction deterministic. That is a stronger property than
simply rejecting the second arrival.

### Missing predecessors are tolerated

A successor can be admitted before an operation named by its context. This is
needed to model reordering without a pending-dependency subsystem, but it means
a forged coherent-looking successor can influence the observed frontier. A
production implementation should store such nodes as unresolved and activate
them only after dependencies and membership authority are satisfied.

### Authentication is absent

SHA-256 operation IDs bind bytes but do not identify who was authorized to
create them. The actor epoch is a caller-provided value, not a key or
certificate. There is no signature, MAC, authenticated transcript, enrollment,
rotation, revocation, or membership epoch.

### Durability is simulated

The in-memory durable snapshot has an atomic assignment cutpoint. It does not
prove that SQLite counter reservation, exact operation bytes, predecessor heads,
outbox publication, or filesystem payload state are committed atomically across
process crash and power loss.

### Anti-entropy is intentionally wasteful

Full-set copying is useful for a small oracle but not a protocol. Pairwise
causality and visible projection are quadratic. Contexts are folder-wide rather
than path- or object-scoped. There is no compaction, stable frontier, tombstone
GC, Merkle summary, delta exchange, or streaming backpressure.

### The name “AnonSync” remains aspirational

There is no demonstrated anonymous routing, metadata minimization, unlinkable
peer identity, traffic-analysis defense, relay protocol, cover traffic, or
privacy threat model. A direct authenticated peer protocol is the nearer
engineering prerequisite; anonymity should then be designed against explicit
adversaries rather than inferred from encryption.

## Recommended production architecture

The following is a research-informed direction, not a claim that the exact
shape is already proven optimal:

1. **Immutable update evidence layer.** Store content-addressed canonical update
   nodes containing actor/key epoch, unique counter or nonce, path/object ID,
   value commitment, and predecessor heads/hashes. Authenticate each node.
2. **Deterministic validator and projection.** Separate “known evidence” from
   “active valid updates.” Given the same node set, all replicas should classify
   valid, pending, forked, revoked, and malformed nodes identically, then derive
   the same multi-value state.
3. **Transactional local mint.** A SQLite transaction reserves the next local
   event, writes exact canonical bytes/signature/predecessors, advances heads,
   and inserts an outbox item. No API reports failure after the event is durable.
4. **Dependency-oriented anti-entropy.** Exchange signed heads or Merkle-DAG
   roots, request missing nodes and predecessors, stream within count/byte/time
   budgets, and avoid copying full histories.
5. **Payload materialization.** Bind chunks and final filesystem publication to
   the immutable operation ID and content digest. Keep conflict-preserved files
   explicit until policy-authorized cleanup.
6. **Authenticated two-process vertical slice.** Exercise real sockets,
   reconnect, replay, crash, duplicate delivery, and SQLite recovery. Compare
   every resulting operation set and visible state against this oracle.
7. **Privacy layer.** Define adversaries and metadata before selecting relays,
   onion routing, pseudonymous device credentials, private discovery, or cover
   traffic. Do not call transport encryption anonymity.

## Audit conclusion

Rev0865 corrects a genuine causal-identity defect and establishes the first
executable network convergence reference in the cube. It also exposes the next
boundary clearly: the product still needs a durable, authenticated,
hash-linked operation protocol whose validity and projection are independent of
arrival order. More local authority wrappers without that vertical slice would
resume the assurance inversion identified in rev0864.
