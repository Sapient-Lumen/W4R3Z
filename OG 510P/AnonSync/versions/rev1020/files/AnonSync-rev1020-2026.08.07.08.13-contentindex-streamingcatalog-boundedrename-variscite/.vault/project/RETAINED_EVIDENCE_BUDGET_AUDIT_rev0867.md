# Retained-evidence budget and mission audit: AnonSync rev0867

## Executive finding

AnonSync's heart is **evidence-authorized, crash-consistent, bounded
convergence**. Copying file bytes is a downstream effect. The authoritative
system must first decide which exact observations exist, who was allowed to
mint them, what exact causal history they depend on, whether those observations
survived a crash, and which deterministic visible state follows when replicas
hold equivalent evidence and trust state.

Rev0865 and rev0866 materially improved the semantic half of that mission:
dotted event identity, canonical hash-bound operations, exact parent IDs,
arrival-independent projection, pending history, and fork quarantine. The deep
rev0867 audit found that the resource half still had a severe multiplication
hole. Per-envelope limits did not imply a useful bound on the complete retained
evidence owner.

At the previous defaults, `max_operations == 10000` and
`max_canonical_operation_bytes == 4 MiB` authorized up to
41,943,040,000 canonical bytes, or exactly 39.0625 GiB, before accounting for
`std::map` nodes, duplicated keys, vector capacity, strings, allocator metadata,
projection indexes, or payload storage. Pending and quarantined evidence was
retained just like active evidence, so an attacker did not need to make useful
state to consume that allowance.

Rev0867 closes that particular amplification path with exact cumulative budgets
for canonical envelope bytes, causal-context entries, and predecessor IDs. The
budgets cover every retained state and are published atomically with the graph
projection. This is a safety ceiling, not garbage collection and not a complete
availability design.

## Mission invariant

A useful compact statement of the mission is:

> Given the same authorized canonical evidence and trust state, independent
> replicas must derive the same state; no untrusted input, crash cutpoint,
> duplicate, missing dependency, or resource claim may silently acquire more
> authority than its exact validated evidence permits.

That sentence has four inseparable parts.

1. **Exact evidence.** Event identity must bind canonical bytes and exact causal
   dependencies, not merely a summary or arrival order.
2. **Authority.** Actor identity, membership, key epoch, revocation, and local
   counter ownership must be explicit and durable.
3. **Atomic publication.** Evidence, projection metadata, local minting
   authority, and retry/outbox intent must cross one durable cutpoint.
4. **Bounded work and retention.** The system must remain fail-closed under
   hostile counts, bytes, graph shapes, retries, identities, and disk pressure.

The current cube is strongest as a collection of C++ ownership boundaries,
SQLite hardening components, crash-oriented tests, and an increasingly precise
in-memory convergence oracle. It is not yet a production end-to-end sync
protocol.

## What rev0867 changes

### One aggregate charge across every evidence state

`SyncReplicaModelLimits` now contains independent cumulative ceilings:

- `max_retained_canonical_bytes`, default 256 MiB;
- `max_retained_context_entries`, default 1,000,000; and
- `max_retained_predecessor_ids`, default 1,000,000.

Each admitted operation contributes an exact charge based on its canonical
versioned envelope and actual metadata cardinalities. Active, pending, and every
quarantined state are charged identically. A same-dot fork therefore cannot
escape the budget merely because the projector refuses to activate it.

The configuration contract requires every aggregate ceiling to admit at least
one envelope legal under its corresponding per-envelope ceiling. This prevents
a self-contradictory policy in which an operation is individually valid but no
empty model can retain it.

### Exact canonical measurement, not an object-size guess

`sync_replica_operation_canonical_size_or_throw` reuses the canonical semantic
validation and exact size arithmetic without constructing the encoded byte
string. It intentionally measures stable protocol material rather than
`sizeof`, allocator capacity, or platform-dependent object layout.

This stable measure is appropriate for protocol accounting and deterministic
restore. It is not a claim about total resident memory. The model still needs a
separate empirical/allocator-aware RSS policy before production exposure.

### Atomic admission and restore

Local mint, remote admission, and durable restore all preflight prospective
aggregate totals before publication. Counters are committed only in the same
no-throw section that swaps the newly derived active set, evidence-state map,
and causal heads into place.

Every throwing projection or allocation cutpoint erases the inserted candidate
and leaves the three retained counters unchanged. The exhaustive allocator
sweep now checks those counters as well as durable state, local counter
authority, evidence membership, and active state.

Restore now consumes `SyncReplicaDurableState` by value. Callers may pass an
rvalue and transfer operation vectors and local authorization IDs into the
model rather than cloning an entire retained graph. Restore still validates
every canonical operation, exact ID, sort order, local binding, cumulative
budget, and projection before publishing the reconstructed owner.

### Duplicate replay no longer repeats canonical hashing

A byte-identical operation already held by the immutable evidence owner is
idempotent authority. Rev0867 detects that exact duplicate before canonical
re-encoding and SHA-256 validation. A same-ID but different value still takes
the full validation path and is rejected unless SHA-256 itself has collided.

The allocation-fault executable arms the first global allocation and proves
that exact duplicate replay performs zero allocations and leaves durable state
unchanged. This reduces a retry/replay CPU and heap-amplification path without
weakening identity checks for new evidence.

### Validation no longer clones actor strings

Canonical semantic validation previously copied the preceding
`SyncReplicaActor`—including its `device_id` string—at each causal-context entry
merely to check strict ordering. It now keeps a non-owning pointer into the
already-owned vector. This removes avoidable heap traffic from every encode,
decode, measurement, ID derivation, admission, and restore traversal.

### Audit machinery no longer relies on a stale magic count

`tools/audit_sync_sqlite_sidecar_snapshot.py` previously required exactly 50
Python CTest command registrations. Adding one legitimate hermetic source audit
made that unrelated assertion fail. Rev0867 replaces the frozen number with a
dynamic invariant: at least the historic floor remains, and every registered
Python command is still launched through the hermetic `-B -S` form.

The distinction matters. An audit should defend a property, not preserve an
accidental count that punishes healthy growth.

## Executable evidence

The focused C++ corpus now reports:

- 67 network/model checks over 44 generated operations;
- 1,288 codec/hash-graph/projection checks, including a 384-operation reverse
  chain, 128-root fan-in, and 192 differential candidates;
- 688 allocation-atomicity checks over 180 local and 158 remote throwing
  allocation cutpoints, plus allocation-free exact duplicate replay; and
- 25 aggregate-budget checks spanning active, pending, quarantined, duplicate,
  restore, local mint, context, predecessor, and byte ceilings.

That is 2,068 focused runtime checks. The same four executables pass under GCC,
Clang 17 with `-Werror`, and GCC ASan/UBSan with leak detection and halt-on-error.
Clang's static analyzer reports no findings in the two changed production
translation units and two changed runtime-test translation units. All 168
registered GCC tests pass: 167/167 in the parallel registry lane plus the
integration-scale `anonsync_core_sync_domain_model_selftest` in isolation, where
it reports 611/611 internal assertions. This split is intentional release
evidence: in this cloud container, repeatedly launching the declared serial
owner immediately after the parallel lane can stall in CTest's wrapper even
though the executable and an isolated CTest invocation terminate cleanly.

These results are implementation evidence, not a proof of the broader product
claims listed below.

## Severe gaps that remain

### 1. The reference model is still not the production cutpoint

The largest mission gap is unchanged: the canonical evidence owner is an
in-memory oracle. The production path does not yet atomically reserve a local
dot, persist exact operation bytes and parent edges, update projection/head
state, and append outbox intent in one SQLite transaction.

Without that vertical slice, a crash can still separate semantic intentions
that the reference model treats as one publication. The next substantial C++
work should therefore be a narrow SQLite owner rather than another broad layer
of disconnected checks.

### 2. Hash identity is not actor authentication

A canonical SHA-256 operation ID proves content identity, not who was authorized
to create the content. The current actor/device/epoch fields are semantic names,
not authenticated principals. A hostile peer can forge dots, consume retention,
and trigger local-epoch compromise behavior.

Production needs signed or MAC-authenticated envelopes, explicit folder
membership epochs, key rotation, revocation, recovery, and deterministic trust
state. Trust policy must itself be versioned evidence or an explicitly external
authority; otherwise replicas can hold the same operation graph and still
project different results.

### 3. Budgets stop damage but do not restore liveness

Once a cumulative ceiling is reached, the model correctly rejects more
evidence. It has no causal-stability protocol, checkpoint certificate,
compaction, tombstone collection, or safe evidence retirement. A long-lived
healthy folder therefore eventually reaches the same ceiling as an attacked
folder.

A production budget must be paired with a lifecycle:

- identify evidence that all relevant authorized replicas have durably covered;
- bind that claim to a checkpoint/root and membership epoch;
- retain enough proof to reject stale or equivocated history;
- compact payload and projection material separately from identity evidence;
- make recovery from an old replica explicit rather than silently resurrecting
  garbage-collected operations.

Until that exists, these limits are an emergency brake, not sustainable
retention.

### 4. Local capacity policy can fracture dissemination

Strong eventual consistency is conditional on correct replicas eventually
receiving and accepting the same valid updates. Two peers with different local
capacity, disk pressure, or admission order can retain different evidence sets.
A local `length_error` must therefore never be reinterpreted as proof that an
operation is globally invalid.

The transport/persistence design needs an explicit outcome such as
`valid-but-not-yet-retained`, durable backpressure, resumable dependency fetch,
and operator-visible capacity state. Limits may be local safety policy; they
must not silently alter canonical operation validity or make a convergence
claim across unequal retained sets.

### 5. Global budgets have no fairness or identity boundary

A single peer or a stream of disposable identities can fill a folder-wide
budget before useful collaborators do. The model has one global pool and no
per-peer, per-actor, per-membership, per-path, or dependency-class reservation.
Quarantined evidence is still full-cost retained material.

A production design likely needs all of the following:

- authenticated admission before expensive graph work;
- per-principal and per-folder quotas with reserved recovery capacity;
- bounded outstanding missing-dependency requests;
- rate and CPU budgets in addition to retained bytes;
- compact equivocation/fork proofs rather than indefinite full-envelope hot
  retention; and
- an operator policy for identities that are unknown, revoked, or demonstrably
  equivocating.

### 6. Canonical bytes are not disk or memory bytes

The exact canonical charge includes all encoded operation fields, context
entries, and parent IDs, but excludes map-node overhead, a second map key,
container spare capacity, projection indexes, allocator fragmentation, database
pages, indexes, WAL growth, snapshots, outbox rows, payload chunks, filesystem
temporary files, and transport buffers.

Production should meter at least three distinct quantities:

1. stable semantic bytes for cross-version protocol policy;
2. actual durable bytes, including SQLite/WAL/snapshot amplification; and
3. bounded live memory/workspace for decode, projection, dependency traversal,
   and payload verification.

Collapsing those into one number would create another false authority claim.

### 7. Projection and anti-entropy remain reference-scale

The projector recomputes the complete retained graph after each insertion, and
the simulator exchanges complete retained evidence. These choices are valuable
as deterministic oracles but remain superlinear over long construction
workloads and inefficient on the wire.

The safe optimization sequence is:

1. keep the current global projector as the executable oracle;
2. add an affected-subgraph incremental projector;
3. differentially compare every mutation and restore;
4. introduce range/head/dependency summaries that never substitute for exact
   missing-node possession; and
5. measure adversarial fan-in, long chains, forks, and missing-parent churn.

## Online research synthesis

The research reinforces the direction but does not replace a threat model or
implementation proof.

- Almeida's CRDT survey explains the convergence condition in terms of replicas
  that have received the same updates and distinguishes operation-, state-,
  pure-operation-, and delta-state approaches. This supports keeping exact
  evidence possession separate from summaries and treating dissemination as a
  required part of the guarantee.
- Delta-state CRDT work demonstrates how incremental anti-entropy can reduce
  message size while retaining convergence over unreliable channels. It is a
  useful future optimization, not permission to make summaries authoritative.
- Kleppmann's Byzantine-CRDT work motivates hash-linked update graphs,
  deterministic validation, and exact dependency handling in untrusted peer
  systems. It also makes clear that ordinary CRDT claims do not automatically
  survive Byzantine behavior.
- The Blocklace work focuses directly on signed hash-pointer DAGs, equivocation,
  and finite harm. Its identity and signature layer is notably beyond the
  current AnonSync reference model.
- A very recent 16 July 2026 preprint, “Memory-Exhaustion Attack on the
  Blocklace Byzantine-Repelling Conflict-Free Replicated Data Type,” argues that
  finite eventual harm can still be arbitrarily large when attackers introduce
  fresh identities and correct nodes eagerly retain incriminating evidence.
  Its suggested direction—limit the identities whose evidence a node is willing
  to replicate—aligns with this audit's conclusion that aggregate bytes alone
  are not enough. Because it is a new two-page preprint, it is treated as a
  warning and design lead, not settled authority.

Primary sources reviewed on 2026-07-21:

- https://arxiv.org/abs/2310.18220
- https://arxiv.org/abs/1603.01529
- https://martin.kleppmann.com/papers/bft-crdt-papoc22.pdf
- https://arxiv.org/abs/2402.08068
- https://arxiv.org/abs/2607.15185

## Recommended next implementation sequence

### Step 1: SQLite evidence/projection/outbox transaction owner

Create one narrow C++ owner with an explicit schema and transaction boundary for
one folder:

- reserve `(actor, epoch, counter)` without reuse;
- store exact canonical envelope bytes and authenticated provenance fields;
- store exact parent edges and retained resource charges;
- derive and atomically publish active/pending/quarantined state plus heads;
- append outbox/dependency intent in the same commit;
- restore by validating bytes and recomputing projection rather than trusting
  cached flags; and
- expose crash injection at every statement/commit frontier.

The in-memory model should remain the differential oracle for this owner.

### Step 2: valid-but-capacity-blocked protocol state

Define a durable distinction among malformed, unauthorized, duplicate,
accepted, pending dependency, quarantined, and valid-but-capacity-blocked.
Capacity-blocked evidence should trigger bounded backpressure and operator
signals, not global-invalid caching.

### Step 3: authenticated identity and fairness

Bind every operation to a key and membership epoch before allowing expensive
retention or dependency work. Add per-principal credits/reservations and a
bounded unknown-identity path. Test Sybil-style identity churn and fork-proof
retention explicitly.

### Step 4: checkpoint/causal-stability and compaction oracle

Specify a checkpoint certificate that commits to evidence coverage, active
projection, trust/membership epoch, and retained fork proofs. Prove compaction
against restore and rejoin corpora before deleting any canonical evidence.

### Step 5: incremental projection and compact anti-entropy

Only after the durable owner and lifecycle are correct, optimize graph updates
and wire exchange. Every optimized result should remain differentially equal to
the global projector and complete-evidence simulator.

## Deliberate nonclaims

Rev0867 does not claim production persistence, authenticated operation
provenance, arbitrary Byzantine convergence, Sybil resistance, fair admission,
causal stability, garbage collection, history compaction, total RSS or disk
bounds, payload-byte accounting, production transport, compact anti-entropy,
payload materialization, confidentiality, anonymity, metadata hiding, forward
secrecy, post-compromise security, formal proof, ThreadSanitizer coverage,
full-project sanitizer coverage, Release-mode all-target behavior, or Windows
runtime behavior.
