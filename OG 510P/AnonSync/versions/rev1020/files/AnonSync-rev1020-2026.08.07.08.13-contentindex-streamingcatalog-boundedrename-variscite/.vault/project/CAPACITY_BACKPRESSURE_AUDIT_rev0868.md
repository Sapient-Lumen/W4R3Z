# Capacity, backpressure, and anti-entropy audit: AnonSync rev0868

## Executive finding

AnonSync's heart remains **evidence-authorized, crash-consistent, bounded
convergence**. The product is not fundamentally a file copier. It is an owner of
exact immutable observations, their authority, their causal dependencies, their
durable publication boundary, and the deterministic projection that follows
when replicas possess equivalent evidence and trust state.

Rev0867 made retention limits exact, cumulative, and atomic. The rev0868 audit
found that the resulting failure mode was still semantically wrong at the
network boundary: a remote operation that was fully well-formed and belonged to
the folder could throw the same kind of terminal exception used for invalid
input merely because this receiver's local retained-evidence budget was full.
That conflated two independent questions:

1. **Is this canonical envelope valid evidence for this folder?**
2. **Can this particular replica retain it under its current local policy?**

That conflation is severe. Validity is a property that peers must be able to
agree on. Capacity is transient, local, policy-dependent state. A low-capacity
replica must not manufacture a global rejection fact, quarantine a valid event,
or cause a sender to discard its only retryable copy.

Rev0868 introduces an explicit `CapacityBlocked` result, exact read-only remote
admission preflight, and a simulator delivery path that preserves blocked
messages. It also corrects three hidden work-amplification paths: whole-graph
copying for duplicate and capacity-blocked delivery, repeated canonical
validation after preflight, and temporary string ownership in partition lookup.
A drain pass now records which messages are capacity-blocked so it can make
progress on later messages without spinning or starving them.

This is an executable reference boundary, not yet a production transport or
SQLite backpressure protocol.

## Mission invariant

A compact statement of the mission is:

> Given the same authorized canonical evidence and trust state, independent
> replicas must derive the same state; no untrusted input, crash cutpoint,
> duplicate, missing dependency, resource claim, or local pressure decision may
> silently acquire more authority than its exact validated evidence permits.

Rev0868 adds the final phrase deliberately. Resource policy must not mutate the
meaning of evidence.

The mission has four coupled owners:

- **canonical evidence** binds exact bytes, event identity, and exact parents;
- **authority** binds actors, membership, key epochs, revocation, and recovery;
- **atomic publication** binds evidence, projection, local minting authority,
  and outbox/retry intent across a durable cutpoint; and
- **bounded liveness** separates invalidity, trust, applicability, and local
  retention so overload is survivable without becoming semantic corruption.

The current cube is strongest as a C++ ownership and fault-injection corpus, a
hardened collection of SQLite/filesystem boundaries, and an increasingly exact
in-memory convergence oracle. The central missing product artifact remains one
vertical production path through authenticated transport, durable operation
storage, deterministic projection, payload verification, and retry.

## The severe semantic defect

### Capacity was expressed as invalid-input failure

Before this revision, `SyncReplicaModel::accept_remote_or_throw` validated a
remote envelope and then threw `std::length_error` if the retained operation
count or any cumulative budget was exhausted. That prevented mutation, but it
did not carry enough meaning for a protocol owner. A transport could reasonably
interpret the exception as permanent rejection, discard the message, report the
peer as malicious, or quarantine the operation.

The model now has an explicit result algebra:

- `InsertedActive`, `InsertedPending`, and `InsertedQuarantined` mean a new
  immutable owner was retained and projected;
- `Duplicate` means the exact immutable owner already exists; and
- `CapacityBlocked` means the envelope passed canonical identity, semantic, and
  folder validation, but one or more local retention budgets would be crossed.

Malformed canonical material and a different folder still throw. A valid
capacity-blocked envelope is not retained, not projected, not quarantined, and
not allowed to alter local authority or aggregate counters.

### Why ordering matters

Capacity must be checked **after** canonical and folder validation for a new
operation. Otherwise a full replica becomes an invalidity oracle bypass: an
attacker can send malformed bytes or a cross-folder envelope and obtain a
benign retryable result without paying the validation that distinguishes bad
input from pressure.

Exact retained duplicates are the exception. Their immutable bytes were already
validated when the owner was admitted. Rev0868 detects byte-identical replay
before re-encoding and SHA-256 validation, reports zero incoming resource
charge, and can retire the transport duplicate without allocating.

The order is therefore:

1. exact retained duplicate check;
2. full canonical validation and exact measurement for a new candidate;
3. folder binding and same-ID collision handling;
4. exact resource-vector construction;
5. local capacity decision; and
6. insertion plus deterministic projection only if admissible.

This preserves both security and cheap idempotence.

## Exact read-only admission preflight

`SyncReplicaRemoteAdmissionPreflight` carries a readiness value and four exact
resource vectors:

- retained operation count, incoming count, and operation limit;
- retained canonical bytes, incoming canonical bytes, and byte limit;
- retained causal-context entries, incoming entries, and entry limit; and
- retained predecessor IDs, incoming IDs, and predecessor limit.

Each vector uses subtraction-before-addition in `would_exceed()`. This avoids an
unsigned wraparound in which a malicious incoming charge could make a
prospective total appear small.

Preflight has no mutation. Exact duplicates report incoming charge zero for all
four dimensions. New candidates receive their exact stable semantic charge,
not `sizeof` or an allocator estimate. `CapacityBlocked` is selected if any
independent dimension crosses its configured local limit.

The insertion consumer is private. It can be called by normal model admission or
by the network simulator, which is a narrowly declared friend. Before insertion
it verifies that the preflight still describes the candidate model's retained
count, retained counters, and limits, that it is admissible, that no budget is
exceeded, and that the operation ID is absent. In this single-threaded immutable
reference harness, the simulator can preflight the live owner, copy that exact
owner, and consume the same plan in the copy without a second canonical
validation/hash pass.

This is a trusted internal optimization boundary. It is not a serialized or
unforgeable protocol token, and rev0868 makes no such claim. A production
admission ticket would need explicit binding to exact operation identity,
policy epoch, storage generation, and expiry, or it should remain entirely
inside one transaction owner.

## Corrected whole-graph copy amplification

### Previous delivery cost

The simulator previously copied the entire destination `SyncReplicaModel`
before asking whether the incoming message was:

- an exact duplicate;
- valid but over local capacity; or
- actually admissible.

The copy includes all retained operations, strings, vectors, maps, evidence
states, active IDs, causal heads, and model counters. It was followed by a
fresh durable snapshot. Thus a tiny duplicate retry could cause work
proportional to the complete destination graph. Under anti-entropy replay, that
turns benign idempotence into CPU and allocation amplification.

### Rev0868 delivery cost

The simulator now preflights the live immutable owner first.

- **Duplicate:** erase the queued message and return `Duplicate`; do not clone
  the graph, reproject state, or manufacture a durable rewrite.
- **Capacity blocked:** return `CapacityBlocked` and keep the queued message; do
  not clone the graph or rewrite durable state.
- **Admissible:** copy the model, consume the already validated preflight in the
  copy, build the candidate durable snapshot, then atomically publish live and
  durable candidates before removing the message.

The asymptotic improvement is material. The duplicate path moves from work
proportional to the retained graph plus durable snapshot to logarithmic owner
lookup and queue retirement. The capacity path performs canonical validation
and exact budget calculation, but no complete graph copy. A genuinely
admissible operation still incurs the simulator's deliberately expensive copy
because that copy models atomic live/durable publication; it no longer incurs a
second canonical validation and hash after the copy.

The allocation-fault test arms the very next global allocation while delivering
an exact duplicate. Delivery still succeeds, proves zero attempted allocations,
removes the queue owner, and leaves the durable destination unchanged.

## Corrected partition lookup allocation

The first duplicate failpoint probe exposed a subtler defect. The simulator's
partition set stored `std::pair<std::string, std::string>`-like owned keys and
called `contains({source, destination})`. That brace expression constructed two
temporary owned strings even for a negative lookup. The supposed zero-allocation
duplicate fast path therefore allocated before admission.

Rev0868 replaces the key policy with:

- an owning `DirectionKey` for stored partition edges;
- a non-owning `DirectionView` of two `std::string_view`s for lookup; and
- a transparent strict weak ordering comparator supporting every key/view
  direction.

Delivery, drain, query, and heal now perform heterogeneous logarithmic lookup
without temporary string ownership. Healing uses `find(view)` followed by
iterator erasure because heterogeneous `erase(key)` availability differs across
standard-library versions. The public semantics do not change, but a hidden
retry-path allocation and linear-search temptation are removed.

## Corrected drain starvation and spin

Making capacity nonthrowing creates a new liveness hazard unless the drain loop
changes. The old loop repeatedly selected the oldest or newest transport-
deliverable message. If that message remained queued after a capacity result,
the next iteration selected the same message again. Depending on
`max_deliveries`, the loop could spin indefinitely or consume the entire call
budget without trying later messages.

Rev0868 records capacity-blocked message IDs for the duration of one drain pass.
Selection skips those IDs while preserving the requested oldest-first or
newest-first order among all not-yet-blocked candidates. A capacity result does
not increment the delivered count. The pass ends when no unattempted
transport-deliverable message remains.

This gives a precise fairness property for the in-memory harness:

> One locally blocked message cannot prevent later unblocked messages from being
> attempted during the same drain call.

It is not production fairness. The set is ephemeral, has no retry deadline, and
is not shared among workers. A production queue needs durable scheduling,
per-principal fairness, backoff, wakeup conditions, and bounded retry metadata.

## State-transition matrix

| Envelope condition | Semantic result | Retained? | Quarantined? | Queue after delivery | Durable rewrite? |
|---|---|---:|---:|---:|---:|
| malformed/invalid identity | exception | no | no | unchanged by failed delivery | no |
| different folder | exception | no | no | unchanged by failed delivery | no |
| exact retained duplicate | `Duplicate` | already | unchanged | removed | no |
| valid, local budget full | `CapacityBlocked` | no | no | retained | no |
| valid, missing exact parent | `InsertedPending` | yes | no | removed | yes |
| valid, deterministic quarantine | `InsertedQuarantined` | yes | yes | removed | yes |
| valid and applicable | `InsertedActive` | yes | no | removed | yes |

The table is intentionally orthogonal. “Quarantined” is a deterministic
projection/evidence state after retention; it is not a synonym for transport
rejection or local pressure.

## Executable evidence

The new `sync_replica_capacity_backpressure_test` exercises 19 focused checks:

- exact duplicate preflight at a full operation-count boundary;
- zero incoming charge for every duplicate resource dimension;
- exact blocked resource vectors for a valid new envelope;
- no mutation of evidence, visible state, durable state, counts, or bytes;
- no accidental quarantine of the blocked operation;
- malformed and cross-folder input still rejected while full;
- successful admission of the same exact envelope under a larger local limit;
- duplicate delivery with the next global allocation forced to fail;
- unchanged durable destination on duplicate retirement;
- retained queue and exact queue-byte accounting on capacity block;
- oldest-first progress past blocked messages to a later duplicate; and
- newest-first termination without spin when only blocked messages remain.

The aggregate budget test now expects explicit `CapacityBlocked` for remote
pressure while preserving throwing behavior for invalid configuration, local
mint exhaustion, and over-budget durable restore. It also verifies exact
preflight canonical-byte charge.

Two structural audits make the boundary difficult to regress accidentally.
The aggregate audit checks exact budgets, result separation, and atomic
publication. The capacity audit checks validation ordering, duplicate zero
charge, preflight-before-copy, private plan consumption, transparent partition
lookup, blocked-message skipping, sanitizer inclusion, CMake registration, and
rev0868 package requirements.

The final release evidence records the exact compiler, sanitizer, analyzer,
registry, and source-audit results under `REVISION_EVIDENCE/rev0868/`. Counts in
that evidence are publication authority; this narrative is not.

## What is still missing

### 1. The result does not cross a production durable boundary

`CapacityBlocked` currently exists in the reference model and network
simulator. There is no production SQLite inbox row, sender outbox state,
receiver pressure record, retry schedule, or two-process transport frame that
preserves the result across crash.

The next vertical slice should atomically couple:

- authenticated canonical operation bytes and exact parents;
- receiver admission/trust/validity verdict;
- exact resource charge or blocked resource vector;
- deterministic projection/head changes when admitted;
- durable sender/outbox ownership when not yet acknowledged; and
- a retry trigger tied to policy/storage generation rather than a busy loop.

A sender must not erase its durable outbox merely because one receiver is full.
A receiver must not retain unbounded blocked envelopes merely to promise retry.
The protocol needs bounded ownership on both sides.

### 2. There is no authenticated principal or fairness domain

The current actor fields are semantic identifiers, not authenticated
principals. A stream of disposable device IDs can still consume validation CPU,
queue slots, and retained capacity. A global folder budget allows the first
principal to fill all shared space.

Likely production policy needs authenticated membership/key epochs, cheap
pre-authentication rejection, per-principal quotas, reserved recovery capacity,
weighted fair scheduling, and strict limits for unknown or revoked identities.
These mechanisms must not let local fairness policy masquerade as canonical
validity.

### 3. Blocked retry has no backoff or wake condition

The simulator retains blocked messages indefinitely and retries only when the
caller invokes drain again. A production scheduler needs at least:

- an explicit reason/resource vector;
- a bounded retry count and metadata size;
- exponential or policy-driven backoff with jitter;
- a `Retry-After`-like lower bound or receiver policy generation;
- wakeup on compaction, quota release, membership change, or operator action;
- dead-letter/operator state that does not silently discard valid evidence; and
- protection against a malicious receiver forcing permanent sender retention.

### 4. Retention still has no lifecycle

Capacity separation improves correctness at the ceiling; it does not prevent a
healthy long-lived replica from reaching that ceiling. There is still no causal
stability certificate, checkpoint/root attestation, safe compaction,
tombstone collection, or old-replica rejoin policy.

A sustainable design needs to distinguish at least:

- immutable identity proof that must remain;
- hot operation material needed for dependency service;
- projection indexes that can be rebuilt;
- payload chunks with independent lifecycle; and
- compact fork/revocation/checkpoint proofs.

### 5. Resource accounting is semantic, not physical

Canonical bytes, context entries, predecessor IDs, queue semantic bytes, and
operation count are stable protocol measures. They do not equal resident
memory, allocator fragmentation, SQLite page/WAL growth, filesystem blocks,
payload bytes, compression expansion, network bytes, CPU, or wall time.

Production must combine deterministic protocol charges with empirical hard
ceilings at storage, process, and transport owners. It must also test the
interaction: for example, a stable 1 MiB envelope can consume substantially
more than 1 MiB across decoded strings, indexes, journal pages, retry copies,
and payload staging.

### 6. Anti-entropy still sends whole retained sets

The simulator's anti-entropy deliberately enqueues a point-in-time copy of every
retained operation. This is useful for correctness testing but wasteful as a
protocol. It has no head summary, set reconciliation, dependency request,
negative knowledge, range proof, or payload chunk negotiation.

The exact operation-ID graph built in rev0866 is the right authority boundary
for a future reconciliation layer: summaries can locate candidate differences,
but every admitted node still needs exact canonical bytes and parent IDs.

### 7. Privacy remains unmodeled

A capacity response can itself leak information: approximate retained volume,
membership activity, path churn, dependency shape, or operator policy. Retry
cadence and queue behavior can become linkability signals. No anonymity,
metadata-hiding, traffic-analysis resistance, forward secrecy, or
post-compromise claim follows from this revision.

A privacy threat model must decide whether pressure information is per-session,
coarse, padded, authenticated, rate-limited, and unlinkable before exposing a
rich resource vector on a real wire.

## Research review and speculative implications

The sources below are design inputs, not implementation authority.

### QUIC flow control: blocked is a protocol state, not malformed data

RFC 9000 defines explicit connection and stream flow-control limits and
`DATA_BLOCKED` / `STREAM_DATA_BLOCKED` signaling. The analogy is useful:
resource unavailability is modeled as a state that can change, independently of
whether already received bytes were syntactically valid.

Source: IETF RFC 9000, especially section 4.1,
https://datatracker.ietf.org/doc/html/rfc9000#section-4.1
(accessed 2026-07-21).

AnonSync should not copy QUIC's transport mechanics directly, but it should
preserve the same category distinction: “cannot accept now” is not “invalid.”

### HTTP overload and retry metadata

RFC 9110 distinguishes malformed or unacceptable requests from temporary
service unavailability and defines `Retry-After`; RFC 6585 defines 429 for
request-rate pressure and notes that generating responses under attack itself
consumes resources.

Sources:

- IETF RFC 9110, sections 10.2.3, 15.5.14, and 15.6.4,
  https://datatracker.ietf.org/doc/html/rfc9110
- IETF RFC 6585, section 4,
  https://datatracker.ietf.org/doc/html/rfc6585#section-4
  (accessed 2026-07-21).

The speculative implication is a bounded, authenticated pressure response with
coarse retry metadata. It must be cheap to produce and cannot require the
receiver to retain the rejected envelope.

### Memory exhaustion through eager Byzantine evidence

“Memory-Exhaustion Attack on the Blocklace Byzantine-Repelling CRDT,” submitted
16 July 2026, analyzes a fresh-identity/eager-evidence memory attack. It is very
recent and should be treated cautiously, but it reinforces a point already
visible in AnonSync: a global byte ceiling is not fair admission, and retaining
all adversarial evidence can itself be an availability vulnerability.

Source: arXiv:2607.15185, https://arxiv.org/abs/2607.15185
(accessed 2026-07-21).

Likely implications are authenticated identity scope, bounded unknown-identity
work, per-principal accounting, interest-driven evidence acquisition, and
compact proofs for misconduct rather than unbounded hot retention.

### Delta anti-entropy and set reconciliation

“Efficient Synchronization of State-based CRDTs” documents the redundancy of
repeated full-state propagation and designs delta-based synchronization.
“ConflictSync” explores digest-driven set reconciliation and reports large
transfer reductions in its evaluated settings.

Sources:

- Enes et al., “Efficient Synchronization of State-based CRDTs,”
  https://arxiv.org/abs/1803.02750
- “ConflictSync: Efficient State Synchronization for Conflict-free Replicated
  Data Types,” https://arxiv.org/abs/2505.01144
  (accessed 2026-07-21).

These works support moving beyond full retained-set replay, but summaries and
deltas must remain acceleration. AnonSync's authority should still be the exact
canonical operation and exact parent graph, with digest disagreement resolved
by requesting exact nodes.

## Recommended next architecture

A production design should make four verdict dimensions explicit rather than
compressing them into success/exception:

1. **Envelope validity:** canonical bytes, operation ID, parent shape, folder
   binding, and authenticated signature/MAC.
2. **Trust/admission:** membership epoch, revocation, key policy, principal
   quota, and unknown-identity policy.
3. **Applicability:** active, pending exact dependencies, fork evidence,
   invalid-dependent, revoked, or deterministic quarantine.
4. **Retention availability:** admitted, capacity blocked by resource vector,
   or retryable after a named policy/storage generation.

A narrow next C++ vertical slice could use SQLite tables conceptually equivalent
to:

- `operation_evidence(operation_id, canonical_bytes, actor, epoch, counter, ...)`;
- `operation_parent(operation_id, parent_id)`;
- `operation_charge(operation_id, canonical_bytes, context_entries, parents)`;
- `projection_state(path, active_operation_id, ...)`;
- `causal_head(actor, epoch, operation_id)`;
- `outbox(operation_id, peer_scope, retry_state, next_attempt, policy_generation)`;
- `inbox_verdict(peer_scope, operation_id, validity, trust, retention, ...)`; and
- `resource_policy(generation, limits, observed_usage, ...)`.

The exact schema is speculative. The invariant is not: local dot reservation,
canonical evidence, parents, charge, projection, heads, and outbox intent must
commit or roll back together. Recovery must verify and reproject rather than
trust cached projection rows blindly.

For anti-entropy, exchange authenticated head/root summaries, identify candidate
missing IDs with a bounded reconciliation structure, request exact nodes and
parents under explicit byte/count/dependency budgets, and acknowledge only
after durable admission. A capacity-blocked response should name no more detail
than necessary, be bounded and rate-limited, and keep durable ownership with the
sender until a protocol-defined terminal outcome.

## Recommended sequence

1. Build one SQLite-backed replica-operation owner that implements the rev0868
   verdict algebra and atomic cutpoint for a single folder.
2. Add crash-frontier tests around local mint, remote admit, blocked verdict,
   outbox acknowledgement, restart, and replay.
3. Bind envelopes to authenticated actor and membership epochs before exposing
   the path to arbitrary peers.
4. Add durable bounded retry with per-principal scheduling and explicit wake
   conditions.
5. Measure actual RSS, SQLite/WAL/disk, payload, CPU, and wire amplification under
   duplicate, blocked, malformed, fork, missing-parent, and fresh-identity load.
6. Replace full-set anti-entropy with exact-ID reconciliation while retaining the
   global reference projector as an oracle.
7. Define checkpoint/stability/compaction and old-replica rejoin semantics.
8. Write a privacy threat model before enriching pressure responses or making
   anonymity claims.

## Deliberate nonclaims

Rev0868 does not claim production SQLite admission, a production transport,
durable retry, authenticated actors, fair or Sybil-resistant allocation,
causal stability, garbage collection, sustainable retention, total physical
resource bounds, incremental projection, compact anti-entropy, payload
materialization, confidentiality, anonymity, metadata hiding, arbitrary
Byzantine convergence, formal proof, full-project sanitizer coverage,
ThreadSanitizer coverage, Release-mode all-target behavior, or Windows runtime
behavior.
