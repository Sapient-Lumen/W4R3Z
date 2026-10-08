# AnonSync rev0872: durable time-fence and state-machine audit

## Executive diagnosis

AnonSync is not primarily a file transfer program. Its heart is an authority
pipeline:

> Exact, authorized, canonical evidence is durable fact. Projection, counters,
> queues, leases, clocks, retries, receipts, and performance indexes are
> subordinate records. They may coordinate or accelerate work, but they may not
> silently acquire more authority than the exact durable cutpoint that created
> them.

Rev0871 made outbox expiry semantically real. A receipt was current only before
its exclusive deadline; at or after the deadline it could no longer settle,
renew, or release the attempt. That closed a serious split between “may be
reclaimed” and “still may settle.”

One authority gap remained. Rev0871 evaluated expiry against the caller's
supplied `now_epoch`, but it did not durably remember time already observed.
The same owner could therefore execute this sequence:

1. Observe epoch 115 for a receipt expiring at 115 and correctly classify it as
   expired.
2. Return without changing the outbox row, because expiry itself is a typed
   result rather than a replacement claim.
3. Restart, or simply accept a later API call, with epoch 114.
4. Reclassify the same still-stored receipt as current.
5. Settle, renew, or release authority that the owner had already observed as
   expired.

The defect was not a torn SQLite transaction. It was an incomplete authority
model: time could revoke authority, but the revocation observation was not
retained. A backwards clock supplied after an expiry observation could make
revoked authority appear live again.

Rev0872 adds a separate, digest-bound, restart-persistent high-water row for
outbox liveness observations. Valid scheduling observations and matching
current or expired receipts may advance it. A lower subsequent observation is a
hard rollback error. Missing intents and stale receipts cannot ratchet it,
because those inputs do not possess the exact current attempt authority needed
to speak for that row.

The clock row is intentionally *not* folded into the evidence generation. A
liveness observation is not canonical operation history and must not pretend to
be. It has its own exact row, digest, schema, snapshot fields, migration rule,
conditional update, staged re-attestation, crash tests, and nonclaims.

A separate state-machine audit found another defect: persisted lease validation
accepted an unreachable state with `dispatch_attempts > 0`, no active claim,
and no retry time. The public state machine cannot mint that state. If accepted
on restore, however, it becomes immediately claimable and silently launders a
corrupt row into new authority. Rev0872 rejects it in the pure validator and in
v2-to-v3 migration.

## Heart of the mission

The project mission is a chain of mutually constraining owners:

1. **Canonical identity.** Freeze exact operation bytes before deriving one
   immutable operation ID.
2. **Exact causality.** Name immediate predecessors. Summary clocks may help
   locate missing work but may not replace exact parent evidence.
3. **Actor and membership authority.** Bind operations to authenticated actor,
   key, membership, and revocation epochs.
4. **Crash-consistent publication.** Publish exact evidence, projection,
   counters, sender intent, dispatch state, and any payload commitment at one
   explicit cutpoint.
5. **Deterministic projection.** Given the same authorized evidence and trust
   state, independent replicas must derive the same active and visible state.
6. **Bounded dissemination.** Duplicates, missing dependencies, adversarial
   identities, retries, bytes, CPU, storage, and time must remain under explicit
   ceilings.
7. **Effect ownership.** A receiver must idempotently bind a terminal record to
   the exact filesystem-visible effect that it owns.
8. **Privacy with a threat model.** Anonymity, unlinkability, confidentiality,
   and metadata claims require a stated adversary and observable surface.

The compact invariant is:

> No untrusted input, crash frontier, stale receipt, missing dependency,
> resource claim, timeout, clock movement, migration shortcut, or local pressure
> decision may silently gain authority.

Rev0872 is a narrow advance in item 6. It prevents already-observed liveness
from moving backwards inside one SQLite owner. It is not a substitute for the
missing owners in items 3, 7, and 8.

## The rollback counterexample in exact terms

Consider one durable outbox intent:

- `claim_id = C`
- `claimed_at_epoch = 100`
- `lease_expires_at_epoch = 115`
- `dispatch_attempts = 1`

Under rev0871:

| Call | Supplied time | Receipt relation | Result | Durable memory of time |
|---|---:|---|---|---|
| settle | 115 | exact `C` | `ExpiredClaim` | none |
| settle | 114 | exact `C` | `Applied` | row deleted |

Both classifications were locally consistent with their supplied timestamps,
but the sequence was globally inconsistent with the owner's own history. The
second call regained terminal authority after the first call had revoked it.

Under rev0872, the first call atomically publishes `high_water_epoch = 115`
before returning `ExpiredClaim`. The second call classifies the exact receipt,
then attempts to observe 114, and fails because 114 is below the durable fence.
No outbox, evidence, generation, or clock mutation commits.

This is an anti-rollback guarantee for retained local observations. It does not
prove that 115 was accurate. A malicious or broken caller can still supply an
arbitrarily large timestamp and ratchet the owner forward. That forward-jump
problem is deliberately recorded as unresolved rather than hidden behind the
word “monotonic.”

## Authority taxonomy

Rev0872 distinguishes five kinds of state that were easy to conflate.

### 1. Canonical evidence

Immutable operation bytes, exact parent edges, actor dot, and retained evidence
state are the durable facts from which projection is derived. They remain the
primary authority.

### 2. Derived projection and redundant metadata

Visible rows, heads, counts, aggregate charges, and digests are independently
recomputed and checked against canonical evidence. They accelerate reads and
make corruption fail closed, but they do not replace evidence.

### 3. Dispatch-attempt authority

The exact outbox row and current `claim_id` identify one sender-side processing
attempt. The receipt is opaque and CSPRNG-bound. A stale receipt cannot settle a
replacement attempt.

### 4. Liveness observation authority

The new singleton clock row says only: this owner has validly accepted an outbox
liveness observation at least this large. It can revoke or delay local receipt
transitions, but it cannot create operation evidence, authenticate a peer,
settle receiver work, or prove physical time.

### 5. Caller input

`now_epoch` is still input, not authority by itself. It becomes durable liveness
state only at a path that already possesses the required local authority:

- a valid scheduler call, even when no intent is ready; or
- an exact matching current or expired receipt.

An invalid identity, missing intent, or stale receipt cannot ratchet the clock.
This prevents unauthoritative responses from becoming a forward-time denial of
service through this API surface.

## Schema v3 clock row

The exact v3 schema adds one STRICT singleton table:

```sql
CREATE TABLE sync_replica_outbox_clock(
  id INTEGER PRIMARY KEY CHECK(id=1),
  high_water_epoch_be BLOB NOT NULL CHECK(length(high_water_epoch_be)=8),
  clock_digest TEXT NOT NULL CHECK(length(clock_digest)=64)
) STRICT
```

The high-water value uses the same canonical eight-byte big-endian encoding as
other durable unsigned counters. The digest domain is
`anonsync-sync-replica-outbox-clock-v1` and binds:

- folder ID;
- local device ID;
- local actor epoch; and
- high-water epoch.

This prevents accidental transplant across folder or actor epochs and makes
casual row mutation detectable. The digest is unkeyed. An attacker able to
rewrite the database and recompute hashes is outside this guarantee.

All SQL references are explicitly `main.` qualified. A same-named TEMP table
cannot shadow the authority row. Connection-local TEMP triggers may still run
inside the transaction, so every staged publication reloads and compares the
complete intended state before commit.

## Why the clock is outside the evidence cutpoint

It would have been simpler to add `high_water_epoch` to `sync_replica_meta` and
increment `state_generation` every time a scheduler checked the queue. That
would be semantically wrong and operationally noisy.

A no-ready scheduling poll changes no operation, evidence classification,
visible state, outbox intent, claim, or retry policy. Treating it as an evidence
state generation would:

- overstate what happened;
- create needless cutpoint churn;
- amplify write traffic and digest recomputation;
- confuse consumers that interpret generation changes as state changes; and
- make future differential projection less precise.

Rev0872 instead gives liveness its own row and digest. `snapshot_or_throw`
exposes both `outbox_time_high_water_epoch` and `outbox_clock_digest` alongside
but distinct from `state_generation` and `cutpoint_digest`.

A clock-only publication still receives the same transactional discipline:
exact conditional update, complete staged restore, comparison with intended
model/meta/outbox/clock, typed write-authority check, and commit.

## Pure C++ anti-rollback primitive

`advance_sync_replica_outbox_time_high_water_or_throw` has deliberately small
semantics:

- zero observations are invalid;
- an equal observation is idempotent;
- a larger observation advances the fence; and
- a smaller observation is rejected as rollback.

It does not read a system clock, persist anything, infer trust, or choose a
forward-jump policy. Keeping it pure makes the authority rule deterministic and
independently testable while leaving clock acquisition to a future owner.

## Transition matrix

The clock update policy is intentionally asymmetric.

| API path | Input relation | May advance clock? | Reason |
|---|---|---:|---|
| claim scheduler | valid identities and positive epoch | yes | scheduler owns local readiness observation |
| claim scheduler | no ready intent | yes | “nothing ready at t” is still a valid liveness observation |
| claim scheduler | lower than high-water | no; throws | rollback must not revive expired work |
| settle/renew/release | intent missing | no | input does not name retained attempt authority |
| settle/renew/release | stale receipt | no | stale attempt cannot ratchet current owner time |
| settle/renew/release | exact current receipt | yes | exact current attempt may speak at this boundary |
| settle/renew/release | exact expired receipt | yes, committed before return | revocation must survive restart and rollback |
| any path | invalid identity/zero/overflow | no | validation fails before durable time authority |

The stale-receipt rule matters. Suppose attempt A has been replaced by B, and A
returns with a wildly future timestamp. If stale input could advance the global
clock, an old unauthoritative worker could expire or delay unrelated current
attempts. Rev0872 returns `StaleClaim` without granting that timestamp durable
authority.

## Atomic publication and crash behavior

Every time-changing path runs inside `BEGIN IMMEDIATE`. SQLite documents that
this begins a write transaction immediately and may contend with another writer.
That makes the writer interval an explicit scarce resource and also gives the
clock update one serial publication point.

The exact update compares the previous high-water bytes and digest in the
`WHERE` clause and requires exactly one changed row. Losing that exact prior
row is an authority failure, not a blind overwrite.

Before commit, the owner independently restores:

- exact schema;
- metadata and all digests;
- canonical operations and parent edges;
- evidence classifications;
- heads and visible projection;
- local-operation mapping;
- outbox intents and leases; and
- the clock row and digest.

The staged state must equal the intended model, meta, outbox, and clock. A TEMP
trigger that mutates the clock digest after the owner's UPDATE therefore causes
re-attestation to fail and the transaction to roll back.

A self-exec crash probe terminates the process immediately after the clock
UPDATE and before COMMIT. On restart, SQLite exposes the old fence, not a
partial observation. Repeating the operation then publishes the new fence
atomically.

## Schema migration

Rev0872 accepts only three exact schema states:

- empty database, initialized directly as v3;
- exact rev0869 schema v1; or
- exact rev0871 schema v2.

Any other schema text or state is rejected rather than repaired heuristically.
Both prior versions are fully restored and attested inside one IMMEDIATE
transaction before old protocol tables are replaced.

### v1 to v3

V1 had no lease fields and no clock history. All migrated outbox rows are
unclaimed first attempts, so the only provable initial fence is zero.

### v2 to v3

V2 retained claims and retry times but no global observation history. Migration
therefore computes the strongest conservative lower bound derivable from each
retained lease:

- an active claim proves time reached at least `claimed_at_epoch`;
- a released attempt proves release time was positive and no earlier than
  `retry_not_before_epoch - max_retry_delay`; and
- an untouched intent proves no positive time.

The migrated fence is the maximum of those lower bounds. It is not the exact
historical maximum observation, because v2 did not retain that fact. No
migration can reconstruct information that was never stored.

An independently constructed exact v2 fixture proves that a live receipt,
outbox digest, and cutpoint survive migration and restart. A malformed v2 row
with dispatched history but neither active nor retry authority is rejected, and
the failed transaction leaves the database at exact schema v2 with no partially
published clock table.

## State-machine audit: unreachable dispatched history

The previous validator accepted this shape:

```text
dispatch_attempts = 1
claim_id = ""
worker_id = ""
claimed_at_epoch = 0
lease_expires_at_epoch = 0
retry_not_before_epoch = 0
```

No public transition creates it:

- an untouched row has zero attempts and no retry;
- a claim has an exact receipt, worker, claim time, and deadline; and
- a release preserves the attempt count and installs a positive retry time.

Yet the old claimability rule treated an empty claim with no retry delay as
immediately claimable. Restore would therefore accept corrupt or hand-crafted
history and mint a new attempt from it. That is an assurance inversion: the
validator admits more authority than the constructor and transition functions
can produce.

Rev0872 closes the state space:

- `dispatch_attempts == 0` requires no claim and `retry_not_before == 0`;
- an active claim requires positive attempts and a complete bounded lease; and
- `dispatch_attempts > 0` without an active claim requires positive retry
  authority.

The invariant is enforced by pure tests, current restore, and exact v2
migration.

## Refactor: one versioned cutpoint authority encoder

Adding schema v3 required preserving exact v2 cutpoint verification. Duplicating
all cutpoint field appends for v2 and v3 would create a subtle migration risk:
one version could omit, reorder, or encode a field differently by accident.

Rev0872 factors the shared authority material into
`append_cutpoint_authority`, then applies version-specific domain and schema
version framing in `versioned_cutpoint_digest_or_throw`. V1 keeps its historical
exact domain behavior; v2 and v3 share one ordered encoder with distinct domain
separation.

This refactor reduces drift without rewriting old evidence. Exact historical
formats remain frozen.

## Test surface added or strengthened

The pure lease test now covers 34 checks, including:

- zero, equal, forward, and rollback high-water observations;
- exact current/stale/expired receipt boundaries;
- heartbeat and retry limits; and
- rejection of dispatched history without active or retry authority.

The SQLite owner test now covers 141 checks, including:

- clock-only advancement with unchanged evidence generation and cutpoint;
- matching expiry committed as a durable revocation observation;
- rollback rejection after expiry;
- stale receipt non-ratcheting behavior;
- exact v1 and v2 migration;
- live v2 receipt preservation and conservative fence seeding;
- malformed-v2 transactional rollback;
- TEMP table shadow resistance;
- TEMP-trigger clock corruption rollback;
- direct clock tamper detection;
- restart persistence; and
- process death after clock UPDATE but before COMMIT.

The clock crash probe is distinct from the existing claim and heartbeat crash
probes. A separate liveness row requires its own crash oracle rather than
assuming evidence-cutpoint tests cover it.

## What changed in the assurance model

Rev0872 can now claim:

- once this owner accepts a valid outbox liveness observation at epoch `t`, it
  will not later accept a smaller authoritative observation;
- an exact receipt observed expired cannot regain authority through a later
  clock rollback;
- the fence survives restart and is atomic with any associated lease action;
- clock-only observations do not falsely advance evidence state generation;
- exact v1 and v2 databases migrate transactionally to v3; and
- unreachable dispatched lease state is rejected rather than laundered.

Rev0872 cannot claim:

- the supplied epoch is physically correct;
- future jumps are bounded or authenticated;
- clocks agree across replicas;
- raw OS monotonic values survive reboot with the same epoch;
- lease expiry is safe under an unstated drift bound;
- a sender receipt is a receiver acknowledgement;
- duplicate transmission or duplicate receiver effects are impossible; or
- the local digests resist an attacker who can rewrite and rehash the store.

## Online primary-source research

Research was accessed on 2026-07-21. The sources are analogies and constraints,
not claims of protocol compatibility.

### Linux clock families

The Linux `clock_gettime(3)` documentation distinguishes clocks with materially
different semantics:

- `CLOCK_REALTIME` can jump when wall time is changed;
- `CLOCK_MONOTONIC` does not jump backwards during one boot, is measured since
  boot, and excludes suspend time; and
- `CLOCK_BOOTTIME` is similarly nonsettable but includes suspend time.

Source:
https://man7.org/linux/man-pages/man3/clock_gettime.3.html

Design consequence: persisting a raw `CLOCK_MONOTONIC` or `CLOCK_BOOTTIME`
reading as if it were a stable cross-reboot epoch is wrong. A future clock owner
needs boot identity and an explicit reboot recovery model, or a different
persistable time representation.

### Gray and Cheriton leases

The original lease paper treats leases as time-based rights and analyzes clock
error. It notes that fast and slow clocks can cause correctness or traffic
problems, and states that correct lease behavior requires at least a known bound
on clock drift when communicating lease duration.

Source:
https://web.eecs.umich.edu/~mosharaf/Readings/Leases.pdf

Design consequence: “monotonic” alone is insufficient. A production lease owner
must state what clock is used, how drift/uncertainty is bounded, what happens
across reboot, and how forward anomalies are quarantined.

### SQLite transaction semantics

SQLite documents that `BEGIN IMMEDIATE` starts a write transaction immediately
and can fail with `SQLITE_BUSY` when another writer is active. A transaction
holds a stable read snapshot, and changes become visible atomically at commit.

Source:
https://sqlite.org/lang_transaction.html

Design consequence: the time fence belongs in the same exact write transaction
as the lease transition it authorizes. Unrelated latency should remain outside
the writer interval, while full staged re-attestation stays inside.

### Amazon SQS visibility timeout

Amazon SQS describes a visibility interval that begins on receive, permits
extension while processing, and makes an unacknowledged message eligible for
redelivery after expiry. It also warns that standard queues are at-least-once,
so duplicate delivery remains possible.

Sources:
https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html
https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_ChangeMessageVisibility.html

Design consequence: work identity, processing-attempt receipt, liveness
interval, and terminal settlement are separate objects. AnonSync's local sender
lease still does not provide a receiver-owned terminal record.

### Google Cloud Pub/Sub acknowledgement IDs

Google Pub/Sub's exactly-once documentation states that when multiple valid
deliveries occur, only the latest acknowledgement ID may acknowledge the
message. It also treats expired acknowledgement IDs as invalid because a newer
delivery may already be in flight.

Source:
https://docs.cloud.google.com/pubsub/docs/exactly-once-delivery

Design consequence: rev0871's attempt-bound receipt and rev0872's durable expiry
memory follow the same broad authority separation. AnonSync does not claim
Pub/Sub's regional service guarantees.

### etcd revisions and lease timing

etcd documents one increasing revision per modifying operation and describes
that revision as a logical clock for key-value changes. Completion is tied to
consensus commit and durable storage.

Source:
https://etcd.io/docs/v3.6/learning/api_guarantees/

Design consequence: logical change order and physical lease time are distinct.
AnonSync's evidence generation orders publications; the outbox clock fences
liveness. Neither should impersonate the other.

### Hybrid logical clocks

Kulkarni, Demirbas, Madeppa, Avva, and Leone propose hybrid logical clocks that
preserve causal ordering while staying close to physical time and masking common
NTP nonmonotonicity. Their design also bounds divergence and rejects
out-of-bounds clock information.

Source:
https://cse.buffalo.edu/tech-reports/2014-04.pdf

Design consequence: HLC is promising for causal timestamps and consistent
snapshot selection, but it is not by itself proof that a physical lease has
expired. AnonSync should not replace the new local expiry fence with an HLC
without specifying physical-time uncertainty and forward-jump policy.

### NTP protocol

NTP's current protocol specification defines network time synchronization but
does not turn unauthenticated application-supplied epoch values into trusted
lease authority.

Source:
https://www.rfc-editor.org/info/rfc5905/

Design consequence: future trusted-time work should separate clock source,
synchronization status, uncertainty, authentication, and application policy.

## Severe gaps that remain

### 1. No trusted clock owner

The public SQLite API still accepts caller-supplied epoch values. The durable
fence prevents rollback but can amplify a far-future mistake or malicious input
into persistent denial of service. This is now the highest-leverage time defect.

A future owner should acquire time internally and expose an observation record,
not a naked integer. Candidate fields include:

- wall-clock epoch;
- boot/session identity;
- monotonic or boottime reading;
- source and synchronization state;
- uncertainty bound;
- maximum accepted forward step;
- last durable observation; and
- explicit quarantine/recovery reason.

### 2. No forward-jump quarantine or recovery protocol

Rollback is rejected, but a leap from 100 to 10^18 is currently accepted if it
arrives through an authoritative path. A production policy needs a maximum
forward delta or uncertainty envelope. Exceeding it should quarantine scheduling
rather than silently expire every receipt and defer every retry.

Recovery must be explicit. Blindly resetting the fence reintroduces rollback.
Possible approaches include operator-authorized epoch reset, a new local actor
or clock epoch, signed time evidence, or a boot-bound recovery record.

### 3. No automatic scheduler or heartbeat owner

The APIs exist, but no production component owns wakeups, heartbeat cadence,
lease extension, cancellation, shutdown, or retry calculation. A future
scheduler must preserve exact receipt identity and must not continue heartbeats
after terminal receiver evidence.

### 4. No receiver-side terminal authority

A sender-side settlement call proves only that a local caller presented the
current receipt. It does not prove the destination durably retained the
operation, authenticated it, projected it, or atomically published the intended
filesystem effect.

The next vertical slice should define a canonical request, authenticated sender
and receiver identities, a receiver idempotency key bound to the exact
operation and attempt, and a terminal receiver record that can authorize local
sender settlement.

### 5. No payload/effect publication owner

Operation metadata and outbox intent do not yet own chunk materialization,
content verification, temp-file creation, atomic rename, directory durability,
or crash recovery of visible effects. This is a larger correctness gap than
additional queue optimization.

### 6. No authenticated actor or local-store authority

Cutpoint, outbox, claim, and clock digests are structural, not keyed. Actor
signatures or MACs, membership epochs, key rotation, revocation, recovery,
rollback-resistant storage, and post-compromise behavior remain absent.

### 7. No causal stability or compaction

The system retains exact history and reprojects it. It has no proof that all
relevant replicas have observed a tombstone or that old evidence can be safely
collected. Old-replica rejoin and forgotten membership remain unresolved.

### 8. No privacy threat model

The project name must not become an accidental assurance claim. Folder IDs,
device IDs, operation timing, graph shape, destination fanout, retry timing, and
traffic volume remain observable in current structures. There is no stated
adversary, cover traffic, metadata-hiding transport, unlinkability proof, or
secure-erasure story.

## Waste and scaling audit

### Full-history restore on every owner operation

Every mutation reconstructs all retained evidence and projection, then changing
mutations perform another full staged restore before commit. This is expensive
in CPU, allocations, SQLite reads, and writer-lock duration.

It is currently intentional: the path is the strongest executable oracle in the
cube. Removing it before a narrow path can be differentially checked would trade
visible cost for hidden authority bugs.

The correction path is staged:

1. retain full restore as migration verifier, periodic auditor, repair owner,
   and differential oracle;
2. add point reads for one outbox intent, clock row, and exact meta cutpoint;
3. use an exact conditional UPDATE with row generation/digest authority;
4. incrementally project only the affected dependency subgraph; and
5. continuously compare sampled narrow-path results against full restoration.

### Global clock writes on no-ready polls

A valid no-ready poll can advance the singleton clock and incur a write. That is
semantically necessary for rollback fencing, but a busy scheduler could create
write amplification.

Safe future optimizations include coalescing equal observations, minimum write
quantum under a trusted-time owner, and wake scheduling from exact next retry or
expiry. Any coalescing must preserve the promise that already-observed expiry
cannot later revive.

### Entropy drawn before a no-ready claim

Claim entropy is still acquired before `BEGIN IMMEDIATE`, even when no intent is
ready. This wastes a small CSPRNG draw but avoids holding SQLite's single-writer
slot while entropy is obtained. The trade is deliberate and preferable until a
narrow readiness precheck can be made without creating a time-of-check authority
race.

### Repeated exact schema text

V1, v2, and v3 schema strings are intentionally duplicated because stored
`sqlite_schema.sql` is protocol evidence. Generating old schema text from a new
template could accidentally rewrite historical authority. The cost is source
size and review burden; the benefit is exact migration attestation.

### Whole-outbox scheduler scan

Claim selection still scans the restored vector. The schedule index exists in
SQLite, but the reference owner does not yet use a narrow indexed claim query.
This is a known production-scale gap, not a correctness defect in the current
bounded oracle.

## Recommended next implementation sequence

1. **Trusted local time owner.** Internalize clock acquisition, persist a clock
   epoch/boot binding, enforce forward-step bounds, and add anomaly quarantine
   plus recovery tests.
2. **Owned scheduler.** Derive exact next wake from retry and expiry rows; batch
   no-ready observations and heartbeats without weakening receipt identity.
3. **Canonical attempt wire record.** Freeze sender request bytes and bind folder,
   operation, destination, attempt receipt, actor/key epoch, and payload
   commitment.
4. **Receiver idempotency/effect owner.** Atomically retain canonical operation
   evidence and publish or recover the filesystem-visible effect, then mint a
   terminal receiver record.
5. **Two-process crash matrix.** Kill sender and receiver before/after every
   durable cutpoint, including ambiguous network response, and prove duplicate
   delivery is harmless.
6. **Narrow outbox point path.** Use indexed exact rows and conditional updates,
   with the full owner retained as a differential oracle.
7. **Authenticated membership and key epochs.** Only then elevate structural
   digests into actual provenance and tamper-resistance claims.
8. **Compaction and privacy design.** Define causal stability, rejoin, erasure,
   and an explicit metadata adversary before deleting history or claiming
   anonymity.

## Deliberate nonclaims

Rev0872 does not claim:

- trusted physical time or authenticated time input;
- bounded forward clock movement;
- cross-reboot monotonicity from an OS monotonic clock;
- cross-node clock agreement or bounded drift;
- HLC-based lease correctness;
- production wake or heartbeat scheduling;
- receiver-authenticated settlement;
- exactly-once transport or exactly-once filesystem effects;
- arbitrary Byzantine convergence;
- Sybil-resistant fairness;
- authenticated local storage;
- complete key lifecycle, forward secrecy, or post-compromise security;
- payload/chunk materialization or atomic visible-file publication;
- causal stability, tombstone collection, or history compaction;
- physical RSS, WAL, disk, network, or global I/O deadline bounds;
- production-scale incremental projection;
- confidentiality, anonymity, unlinkability, metadata hiding, or secure erasure;
- full-project sanitizer or ThreadSanitizer coverage;
- Windows runtime behavior; or
- formal verification.

## Bottom line

Rev0871 made expiry a rule. Rev0872 makes an accepted expiry observation
survive the next call, the next transaction, and the next process.

That correction matters because authority cannot be allowed to oscillate with a
caller clock. The new fence is deliberately narrow: it remembers local liveness
without pretending to be canonical evidence or trusted physical time. The
state-machine audit also removes an impossible persisted lease shape that could
otherwise be laundered into a fresh attempt.

The next serious step is not another queue feature. It is to own time acquisition
and then carry attempt authority across an authenticated sender/receiver
boundary into an idempotent, crash-consistent filesystem effect.
