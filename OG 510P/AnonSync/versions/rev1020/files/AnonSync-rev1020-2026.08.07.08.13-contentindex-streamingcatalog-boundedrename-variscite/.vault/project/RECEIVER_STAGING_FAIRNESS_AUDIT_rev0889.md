# Receiver staging fairness and retention audit — rev0889

## Executive finding

The receiver file-effect owner is bounded and now isolates each retained
`device_id`, but it is not fairly scheduled and is not self-healing. One
authorized party able to enroll many device IDs—or ordinary long-lived churn
across many legitimate devices—can still fill a folder's entire retained effect
count or payload-byte budget with valid, identity-bearing operations that never
become materializable. Once full, unrelated peers receive
`EffectCapacityBlocked` indefinitely because there is no stable membership-
principal quota, protected reserve, expiry, dead-letter owner, or garbage
collection transition.

Normal successful use also accumulates toward the same permanent ceiling:
published payload bytes remain stored and counted. The current bounds prevent
unbounded disk growth, but they convert eventual capacity exhaustion into a
folder-wide liveness failure.

This is a high-impact availability and operability gap. It is not evidence that
an unauthenticated network peer can mutate durable state: rev0889's accepted
session owner requires mutual TLS and explicit SPKI-to-actor membership before
the file service. It is evidence that a malicious, compromised, buggy, or merely
very active authorized member can monopolize a shared durable resource.

Rev0889 implements a first durable isolation slice: every owner load re-derives
exact retained usage by actor epoch and by `device_id`; schema v3 persists and
binds per-device count/byte limits plus compact usage witnesses; and a capacity
rejection carries receiver-local folder/device budgets bound to the inspected
effect cutpoint. This prevents actor-epoch rotation from resetting a charge and
lets one saturated known device leave folder headroom for another. It still does
not prove a membership principal, reserve capacity across arbitrarily many
device IDs, schedule fairly, or free one byte. Payload retention participates in
crash recovery and exact idempotency; incorrect reclamation could trade an
availability problem for integrity loss.

## Exact current behavior

`SyncReplicaFileEffectSqliteOwnerLimits` persists five admission limits per
folder/root authority:

- `max_effects` (default 10,000);
- `max_payload_bytes` for one operation (default 4 MiB);
- `max_retained_payload_bytes` (default 256 MiB);
- `max_effects_per_device` (default 2,500); and
- `max_retained_payload_bytes_per_device` (default 64 MiB).

The effect table has only two durable states:

```text
staged -> published
```

There is no delete API or collectible state. `derive_attestation_or_throw()`
adds every stored payload's size to `retained_payload_bytes` regardless of
whether its effect is staged or published. Both states remain in the effect-set
and cutpoint digests.

The public snapshot now contains sorted, re-derived
`SyncReplicaFileEffectActorUsage` and `SyncReplicaFileEffectDeviceUsage`
vectors. Actor usage preserves the complete `(device_id, epoch)` namespace;
device usage aggregates epochs without claiming that `device_id` is a human or
stable membership principal. The vectors are re-derived rather than trusted as
persisted counters; schema v3 stores only an exact device count and usage digest
that every load recomputes. `stage_with_diagnostics_or_throw()` returns exact
folder/device resource budgets and current actor/device usage only when a unique
stage is capacity-blocked. The generic peer-visible receipt remains
`EffectCapacityBlocked`, and sender-local policy still owns retry timing.

The receiver ordering is intentional:

```text
complete authenticated request
    -> validate folder/peer/actor/channel binding
    -> stage exact payload in the effect database
    -> admit causal evidence in the replica database
    -> acquire exact active-primary projection guard
    -> atomically materialize or reconcile filesystem effect
    -> build exact receipt
```

Staging before causal admission ensures that a crash, retry, or later causal
activation does not lose the exact payload corresponding to already-observed
operation evidence. It also means payload capacity is consumed before the
receiver knows whether the operation is active, pending, quarantined,
projection-blocked, or destination-conflicting.

A new unique stage is rejected at the first violated boundary:

```text
folder effect count
folder retained payload bytes
device effect count
device retained payload bytes
```

The duplicate path is checked first, so an exact retry can still reconcile an
already-retained operation when the database is otherwise full or its device is
saturated. Device usage spans actor epochs, but a newly enrolled device ID has a
separate charge. The folder caps remain the final aggregate safety boundary.

## Starvation sequence

An authorized actor can cause folder-wide starvation with protocol-valid input:

1. Establish a mutually authenticated TLS session and pass membership mapping.
2. Send unique, bounded file operations whose sender actor and channel binding
   are valid.
3. Choose operations that remain causally pending, are quarantined, lose the
   active-primary projection, or conflict at the immutable destination.
4. Each request is staged before that nonterminal causal/effect result is
   known.
5. Repeat across enough enrolled device IDs until either aggregate count or
   retained bytes reaches its persisted folder ceiling.
6. All new unique operations from every actor receive `EffectCapacityBlocked`.
7. Sender retry policy delays those requests, but no receiver transition frees
   capacity, so retry alone cannot restore liveness.

A peer need not violate payload digest, operation identity, canonical encoding,
TLS, or membership policy. This is resource capture through valid authority,
not parser abuse.

The same terminal state is eventually reachable without an attacker. Published
operations retain their payloads and count forever. A long-lived folder with
normal churn will ultimately exhaust a finite permanent-history limit.

## Why obvious fixes are unsafe

### Delete staged payload after a nonactive evidence receipt

A pending operation may later become active when predecessors arrive. Deleting
its exact payload would leave canonical operation evidence without the bytes
needed to materialize the authorized effect. A sender retry might recover the
payload, but availability of the sender is not durable receiver authority and
cannot be assumed.

### Delete the least-recently-used effect

Recency is a cache heuristic, not causal stability or authorization. LRU could
delete the only exact bytes needed for crash reconciliation, duplicate receipt,
or later activation. It would let access patterns rewrite authority history.

### Delete published payload immediately

Publication can crash after filesystem namespace durability but before the
SQLite published mark, or vice versa around later receipt delivery. Exact bytes
are currently used to reconcile immutable destination state and idempotent
retry. Reclamation needs a proved terminal/checkpoint frontier, not a successful
`rename` observation alone.

### Lower the global limits

Smaller limits reduce damage per folder but make starvation easier. Larger
limits delay the same failure and increase restore cost. Neither adds fairness
or lifecycle.

### Quota by TLS connection or actor epoch only

A member can reconnect. Actor epochs may rotate legitimately, and a malicious
member may seek repeated enrollment if the membership model permits it. Quota
identity must be tied to a durable stable membership principal and policy, while
still recording exact actor epochs for evidence.

### Evict on operator command without a durable protocol

An unrecorded administrative deletion would make replicas and restarts derive
different retained authority. Operator action must itself be typed, durable,
auditable, and constrained by causal/receipt/checkpoint state.

## Required design separation

A safe correction needs at least four separate concepts:

1. **Exact retained authority.** Canonical operation, payload digest/bytes,
   effect state, and receipt/reconciliation evidence.
2. **Admission accounting.** Who is charged, how much, in what state, and under
   which persisted policy epoch.
3. **Fair scheduling.** Which principal may consume shared headroom next;
   summaries can guide selection but cannot authorize deletion or publication.
4. **Reclamation authority.** A durable proof that exact bytes may be removed
   while preserving retry, convergence, repair, and audit obligations.

Folder/device hard counters are simple and correctly bounded, but still
insufficient for a multi-member service without stable principal identity,
protected reserve, scheduling, and reclamation authority.

## Proposed staged correction

### Phase 1: truthful accounting and device hard isolation — completed narrow slice in rev0889

Rev0889 now derives, persists witnesses for, and restart-tests:

- exact actor epoch;
- device aggregation across actor epochs;
- staged versus published effect counts;
- retained payload bytes;
- folder and per-device count/byte policy in the cutpoint; and
- the first violated budget and exact cutpoint that rejected one request.

Still add derived, independently re-attested usage by:

- stable membership principal and policy epoch;
- causal evidence state;
- materialization result;
- canonical bytes;
- oldest/newest generation; and
- terminal versus potentially activatable status.

The persisted rows already contain operation actor identity and exact bytes, so
an O(history) oracle can derive this without making counters authoritative.
A future indexed owner may cache counters only if it re-attests them against the
same row closure.

Before expanding the wire protocol, define privacy-bounded structured capacity
classes that can distinguish:

- folder hard cap;
- device hard cap versus stable-principal hard cap;
- principal soft/fair-share cap;
- quarantine reserve exhausted;
- terminal-retention reserve exhausted; and
- temporary scheduler pressure.

The current local diagnostic is intentionally more detailed than the wire
receipt. Do not expose unrelated member usage or receiver-selected retry timing
as sender authority; local sender policy should continue to own retry
cutpoints.

### Phase 2: persisted quota policy and reservations

Persist a versioned policy with:

- folder hard count/byte limits;
- per-principal hard limits;
- soft fair shares;
- minimum uncommitted reserve for other principals;
- a separate bounded reserve for duplicates/reconciliation;
- a bounded quarantine/pending pool;
- maximum single-operation bytes; and
- policy epoch/digest in the effect cutpoint.

Before storing a new payload, mint a durable reservation charged to the stable
membership principal and exact operation ID. Reservation, stage, and release
must be idempotent. Duplicate retries must not double-charge. A crash after
reservation but before payload commit must be recoverable without leaking
capacity forever.

A simple first scheduler can enforce:

```text
principal_usage + requested <= principal_hard
and folder_usage + requested <= folder_hard
and remaining_folder_headroom >= reserve_for_others
```

Soft shares should govern selection when multiple principals are eligible, not
rewrite already-retained evidence.

### Phase 3: causal/effect lifecycle

The two-state effect model needs explicit lifecycle states or independently
bound lifecycle metadata, for example:

```text
Reserved
  -> StagedUnadmitted
  -> AdmittedPending | Quarantined | Active
  -> Published | DestinationConflict
  -> StableRetained
  -> Collectible
  -> Reclaimed
```

Names are not authority. Each transition needs exact prerequisites. A plausible
`Collectible` proof would bind some combination of:

- operation/effect terminal state;
- sender settlement or durable terminal receipt evidence where available;
- causal stability/checkpoint proving no future active projection requires the
  payload;
- conflict/tombstone retention policy;
- membership/rejoin policy for offline replicas;
- a minimum audit/repair retention generation; and
- a signed or otherwise authenticated compaction checkpoint.

AnonSync does not yet have causal stability, compaction, or rejoin semantics
strong enough to justify this transition. Those must be designed together.

### Phase 4: protocol-level payload admission

The current TLS record contains the complete request and payload before durable
service admission. Per-principal disk quota therefore does not bound transient
network/memory work.

A scalable protocol should separate:

1. a small authenticated operation offer;
2. receiver validation and durable quota reservation;
3. an exact reservation token bound to folder, peer principal, actor epoch,
   operation, payload digest/size, channel/session context, and expiry; and
4. bounded chunk transfer into a crash-safe staged object.

The receiver must not authorize payload chunks from an unauthenticated or
unreserved sender. The token must not become publication authority. Chunking,
resume, and deduplication should be differentially tested against the current
whole-payload oracle.

### Phase 5: daemon overload ownership

The accepted-session owner added in rev0889 is one-shot. The future listener
scheduler must add independent limits for:

- queued accepted descriptors;
- concurrent TLS handshakes;
- concurrent authenticated sessions per principal;
- aggregate in-flight request bytes;
- CPU-heavy certificate verification;
- request/receipt deadlines;
- source-address abuse diagnostics; and
- graceful drain/restart.

Network-source limits cannot replace membership-principal quotas, and
membership-principal quotas cannot replace preauthentication handshake limits.
Both are needed.

## Deterministic test plan

A correction should add a model and crash matrix that proves at least:

1. principal A reaches its soft/hard share while principal B can still stage
   within the protected reserve;
2. a single operation retry never double-charges count or bytes;
3. path-blocked operations consume no payload reservation;
4. capacity rejection creates no effect row or leaked reservation;
5. actor epoch rotation remains charged to the correct stable principal;
6. membership revocation does not silently free evidence still needed for
   repair/rejoin policy;
7. crashes before/after reservation, payload write, stage commit, causal
   admission, publication, receipt, collectible mark, and reclaim converge to
   one accounting cutpoint;
8. published effects remain recoverable until the exact reclamation proof;
9. an adversarial pending/quarantine stream cannot consume another principal's
   protected reserve;
10. terminal garbage collection cannot make a duplicate operation publish a
    second visible effect;
11. the indexed production owner and O(history) oracle derive identical usage,
    eligibility, and reclamation decisions; and
12. full database restart re-attests every cached counter and policy digest.

## Severity and priority

This gap should be addressed before exposing a long-running multi-member
listener to untrusted or weakly governed members. It is less urgent than
preventing unauthenticated durable mutation—which rev0889 now fences—but more
urgent than adding operation types, discovery, relays, or broad performance
optimization.

The safe near-term sequence is:

1. extend rev0889's truthful actor/device accounting to a durable membership
   principal and policy epoch, then export privacy-bounded pressure telemetry;
2. persist quota policy and idempotent reservations;
3. add fair admission while retaining the current owner as the oracle;
4. design causal stability, compaction, rejoin, and reclamation together; and
5. only then delete payload authority.

Until then, deployments should treat the folder and device limits as finite
lifetime admission budgets, not as self-healing cache ceilings or actual free-
disk quotas.

## Nonclaims

This audit does not prove an exploit over a deployed daemon; no such daemon is
shipped by this path. It does not claim that every authorized peer is hostile,
that current bounds are useless, or that payload retention is accidental. The
bounds prevent unbounded growth and the retention supports exact recovery.

It establishes a narrower fact from the current C++ and schema: capacity has
deterministic folder and per-device hard boundaries, all staged and published
payload bytes remain permanently counted, staging precedes causal admission,
and no stable-principal fairness or reclamation authority exists. The proposed
design is a direction for executable refinement, not a completed protocol proof.
