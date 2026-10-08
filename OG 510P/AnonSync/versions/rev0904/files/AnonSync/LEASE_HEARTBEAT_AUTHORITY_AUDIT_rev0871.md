# AnonSync rev0871: live-receipt heartbeat authority audit

## Executive diagnosis

AnonSync is not fundamentally a file-copy loop. Its heart is an authority
pipeline:

> Exact, authorized, canonical evidence is durable fact. Every projection,
> counter, queue entry, lease, retry time, acknowledgement, and optimization is
> subordinate state that may accelerate or coordinate work, but may never gain
> more authority than the exact cutpoint that created it.

Rev0870 repaired one serious dispatch defect by giving each sender attempt a
fresh receipt. A delayed receipt from an old attempt could no longer settle a
new replacement attempt. That was necessary, but the lease still had a false
boundary: while the same receipt remained stored, it could settle or release the
intent even after its deadline. Expiry allowed another worker to replace the
claim, but did not itself revoke the old claim's terminal authority.

That means the previous object was better described as a *reclaim hint* than a
lease. It controlled when replacement became possible, not when ownership ended.
The distinction is dangerous around slow transports, paused workers, clock
boundaries, and delayed responses. Two workers could both plausibly believe they
were authorized: the old worker because its receipt still matched the row, and
the new worker because the deadline made the row reclaimable.

Rev0871 makes the deadline an actual authority boundary. The exact receipt and
an unexpired interval are now jointly required for settlement, retry release,
and renewal. The deadline is exclusive: at `now_epoch >=
lease_expires_at_epoch`, the receipt is expired. Time can revoke authority; it
can never create it. A matching receipt remains mandatory before the deadline.

The revision also adds bounded heartbeat renewal, moves CSPRNG acquisition out
of SQLite's single-writer interval, rejects overlong persisted active claims,
bounds API-minted retry delay, replaces repeated linear receipt lookup with
canonical binary search, and unifies claim/renew/release publication through one
exact-row and full-re-attestation path.

## Heart of the mission

The mission has seven linked owners:

1. Canonical operation identity freezes exact bytes before deriving an ID.
2. Exact parent evidence, not a summary clock, owns causality.
3. Actor and membership epochs must eventually own who may create evidence.
4. One crash-consistent publication must bind evidence, projection, mint
   authority, sender intent, and dispatch ownership.
5. Deterministic projection must be reproducible from retained evidence and
   trust state.
6. Dissemination must stay bounded under duplicates, missing dependencies,
   crashes, hostile identities, and resource pressure.
7. Privacy claims must be scoped to an explicit adversary and observable
   metadata model.

The current cube is strongest in canonical identity, exact evidence retention,
deterministic projection, and local SQLite publication. Its largest remaining
gaps are authenticated actor/membership authority, a real sender/receiver
transport with terminal receipts, receiver-side idempotent effect ownership,
payload publication, scalable incremental projection, trusted time and
scheduling, physical resource accounting, compaction, and a privacy threat
model.

## The false lease boundary in rev0870

The rev0870 pure state machine had two independent questions:

- Is this row claimable now?
- Does this receipt equal the stored `claim_id`?

Claimability observed the deadline. Settlement and release observed only the
receipt. Therefore an exact receipt at or after its own deadline remained able
to retire or reschedule the intent until a replacement claim was committed.
This produced an avoidable race window:

1. Worker A claims an intent until epoch 110.
2. At epoch 110, A is expired and worker B is entitled to reclaim.
3. Before B commits, A settles using the still-stored receipt.
4. Depending on lock order, either A retires work after its authority should
   have ended, or B replaces A.

SQLite serialization prevented a torn row, but serialization alone did not
answer which transition was semantically authorized. The old rule let lock
arrival decide. Rev0871 instead decides from the exact stored row plus the
explicit time boundary: A is expired at 110 and cannot settle, release, or
renew. B may then claim.

This is not an exactly-once claim. A may already have transmitted before expiry,
and B may retransmit after expiry. The correction is narrower and essential:
the local sender owner no longer accepts a terminal transition from an expired
receipt.

## Exact authority model

For one immutable `(destination_device_id, operation_id)` intent, the durable
lease state contains:

- cumulative `dispatch_attempts`;
- opaque `claim_id`;
- `worker_id`;
- `claimed_at_epoch`;
- exclusive `lease_expires_at_epoch`; and
- `retry_not_before_epoch` when unclaimed.

A receipt classification at epoch `t` is:

- **Stale** when the row is unclaimed or the expected claim differs;
- **Expired** when the exact claim matches but `t >= lease_expires_at_epoch`;
- **Current** only when the exact claim matches and
  `claimed_at_epoch <= t < lease_expires_at_epoch`.

Staleness is checked before the current row's clock floor. This is deliberate.
A receipt from an older attempt remains stale even if the caller supplies a time
before the newer attempt's `claimed_at_epoch`; it cannot use the replacement's
clock range to turn a stale response into a hard error or authority.

For an exact matching claim, `now_epoch < claimed_at_epoch` is rejected. That
catches obvious caller clock rollback at the authority boundary. It does not
prove that supplied epoch time is trustworthy or globally monotonic.

## Pure C++ lease state machine

`src/sync_replica_outbox_lease.hpp/.cpp` now owns all temporal receipt rules as
pure deterministic policy.

### Deadline revocation

`sync_replica_outbox_claim_status_at_or_throw` validates the complete persisted
state, the expected receipt syntax, and positive time. Settlement-facing code
uses the same classifier as renewal and retry release. There is no longer one
expiry rule for claim selection and another implicit rule for terminal actions.

The exclusive boundary is tested directly. One tick before expiry is current;
the exact deadline is expired. An expired receipt cannot be renewed or released
by the pure API.

### Heartbeat renewal

`renew_sync_replica_outbox_lease_or_throw` extends only an exact, current,
unexpired claim. It preserves the receipt, worker, original claim time, and
attempt count. A heartbeat therefore extends the same attempt rather than
minting a new identity.

The requested deadline is `now_epoch + lease_seconds`. Renewal never shortens an
existing deadline. When the existing deadline already covers the requested
interval, the pure function returns the identical state. The SQLite owner maps
that to `LeaseAlreadyCovered` and commits a durable no-op without changing the
state generation or cutpoint digest.

A claim cannot be extended beyond a fixed cumulative lifetime measured from its
original `claimed_at_epoch`. The current constants are:

- maximum single lease: 86,400 seconds;
- maximum cumulative lifetime of one claim: 86,400 seconds; and
- maximum API-minted retry delay: 86,400 seconds.

These are hard safety ceilings, not evidence that 24 hours is an appropriate
production default. A production policy should choose much smaller operational
intervals from measured task duration, duplicate cost, failure detection goals,
and clock behavior.

### Restore-time lifetime invariant

The state validator now rejects a persisted active claim whose deadline exceeds
the cumulative lifetime ceiling. This matters because validating only the
renewal API leaves a split authority model: runtime code would refuse to create
an overlong claim, while restart would accept one. Rev0871 closes that split for
active claim lifetime.

The retry-delay ceiling is enforced when release is minted, but the current
schema does not persist a separate `released_at_epoch`. Consequently restore
cannot reconstruct the original delay and independently prove that a stored
absolute retry time was no more than 24 hours from release. The cutpoint digest
still detects accidental mutation relative to its metadata, but it is unkeyed
and not an authenticated anti-tamper mechanism. A future schema should persist
retry scheduling provenance if restore-time proof of this policy is required.

### Bounded retry release

Retry release now requires the exact current unexpired receipt, an absolute
retry epoch no earlier than `now_epoch`, and a delay within the fixed ceiling.
Release clears active claim fields, preserves the attempt count, and installs
the retry time durably. Missing, stale, and expired receipts are no-op results
at the SQLite owner surface.

The revision does not implement exponential backoff, jitter, poison detection,
or dead-letter policy. It bounds the caller-supplied transition; it does not yet
own how the caller chooses that transition.

## SQLite transaction and publication refactor

`SyncReplicaSqliteOwner` remains the durable authority. Every public mutation
opens a typed transaction, restores and re-attests exact evidence and redundant
projection, applies pure policy, compares the complete prior outbox row, updates
metadata, reloads the staged cutpoint independently, and commits only if the
observed state exactly matches the intended publication.

### Entropy before the writer lock

Rev0870 called OpenSSL `RAND_bytes` after `BEGIN IMMEDIATE`. SQLite documents
that an IMMEDIATE transaction starts the write transaction immediately and may
fail with `SQLITE_BUSY` when another writer is active. In WAL mode, readers can
coexist, but there is still only one writer. Holding that scarce writer slot
while waiting on an external CSPRNG was unnecessary.

Rev0871 obtains exactly 32 CSPRNG bytes before entering the IMMEDIATE
transaction. The entropy itself carries no database authority. Inside the
transaction, the owner still reloads the exact cutpoint, selects the canonical
ready intent, and binds the loaded cutpoint, intent, worker, schedule, and
entropy into the claim ID. A competing writer cannot retarget the token because
selection and publication occur after the lock is acquired against the newly
loaded state.

This change deliberately accepts a small waste: one entropy draw can be
consumed when no intent is ready, or when the transaction later fails. That is
preferable to extending SQLite's one-writer critical section around CSPRNG
latency. A future point-read selector could avoid even that draw by first
finding a candidate, then acquiring entropy, then conditionally claiming under
an exact compare-and-swap transaction.

### Canonical binary lookup

Settlement, renewal, and release previously repeated linear `find_if` scans over
an outbox already restored in canonical `(destination, operation)` order.
Rev0871 centralizes exact lookup with `std::lower_bound`. This is a local
refactor, not a production scalability claim: the owner still loads the entire
outbox and retained history before searching. It nevertheless removes three
copies of key comparison logic and changes the in-memory lookup from linear to
logarithmic.

### One lease publication path

Claim and release had nearly identical sequences for exact prior-row update,
state-generation increment, digest recomputation, metadata update, staged full
restore, and commit. Renewal would have created a third copy. Rev0871 factors
that sequence into `publish_outbox_lease_update_or_throw`.

The helper does not weaken transaction typing or hide authority checks. It takes
the live typed transaction, exact prior lease, mutated canonical intent, loaded
model, folder identity, and actor identity. Every changing claim, renewal, and
release therefore shares the same exact-row compare and full precommit
re-attestation.

Settlement remains distinct because it deletes the intent rather than updating
its lease.

## Crash, restart, trigger, and concurrency coverage

The focused pure lease test now reports 31 checks. It covers current/stale/
expired classification, exclusive deadlines, clock rollback for a matching
receipt, renewal identity preservation, no-shortening behavior, already-covered
no-op renewal, expiry rejection, cumulative lifetime overflow, restore-time
rejection of overlong active state, bounded retry scheduling, invalid IDs,
invalid state shapes, and integer overflow.

The SQLite owner test now reports 113 checks. The receipt lifecycle test covers:

- initial claim;
- heartbeat extension;
- an already-covered heartbeat with no generation change;
- rejected overlong heartbeat and retry delay with no state change;
- restart preserving the renewed deadline;
- settlement, release, and renewal all returning `ExpiredClaim` at the exact
  deadline;
- replacement claim after expiry;
- stale old receipt no-ops;
- bounded retry release and delayed readiness; and
- final exact settlement.

Connection-local TEMP triggers are used as hostile in-transaction mutation
probes. A trigger that rewrites the claim row after claim publication, and a
separate trigger that rewrites it after renewal, are both detected by the
independent staged restore. The transaction rolls back rather than publishing a
valid-looking but unintended cutpoint.

A process-crash helper exits after the exact outbox-row renewal update but before
metadata publication and commit. Restart sees the prior deadline, proving that
the heartbeat did not partially escape the transaction. Retrying renewal then
publishes one exact new cutpoint. The existing competing-worker test continues
to prove that two claimers serialize to one current receipt.

These tests model process death and SQLite transaction rollback in this
container. They are not a hardware power-loss, filesystem, VFS, or storage-cache
attestation.

## Audit/refactor findings

### Corrected now

1. Expiry was only reclaim permission, not revocation. It now revokes all
   receipt-authorized terminal or extension transitions.
2. There was no heartbeat. A bounded, identity-preserving heartbeat now exists.
3. Runtime renewal policy and restart validation could have disagreed about
   cumulative claim lifetime. Restore now enforces the same ceiling.
4. Arbitrarily distant API-supplied retry scheduling is now rejected.
5. CSPRNG work no longer holds SQLite's single-writer interval.
6. Three repeated linear receipt lookups now share one canonical binary search.
7. Claim, renewal, and release now share one exact publication and re-attestation
   path.
8. Renewal now has its own trigger-corruption and process-crash frontier tests.
9. The release verifier now requires this revision's authority audit.
10. During publication review, an unintegrated delivery-protocol side branch was
    removed rather than shipped as dead, untested assurance surface. A wire
    protocol should enter the cube only with canonical codec tests, receiver
    ownership, authentication nonclaims, and end-to-end crash coverage.

### Still expensive or wasteful

The largest remaining waste is architectural, not a small loop. Each owner
operation performs an O(history) restore and deterministic reprojection. Claim
selection restores the whole evidence set and outbox even though only one
schedule row is needed. Every changing lease publication then performs another
full staged restore before commit. This is defensible as a correctness oracle,
but it is not a production algorithm.

A high-leverage redesign is a dual path:

- a narrow point-read and affected-row mutation path for ordinary work; and
- the present full restore/projector retained as a differential oracle,
  periodic auditor, migration verifier, and repair authority.

The narrow path must prove exactly which digests, counters, and projection rows
it owns. Replacing the full oracle with ad hoc cache trust would invert the
mission.

Other deliberate or unresolved costs include:

- one CSPRNG draw before discovering that no intent is ready;
- `BEGIN IMMEDIATE` even for missing, stale, expired, or already-covered receipt
  results, because the current API establishes its answer against one fully
  restored serialized cutpoint;
- full outbox digest recomputation after one lease-row change;
- caller-supplied wall-clock epochs without a persisted monotonic high-water
  mark;
- one fixed global 24-hour ceiling instead of persisted per-folder policy;
- no batched heartbeat or settlement path; and
- no physical accounting for WAL growth, checkpoint cost, disk occupancy, RSS,
  payload bytes, or filesystem effects.

## Online primary-source synthesis

The external systems below are analogies and design evidence. Rev0871 does not
claim protocol compatibility or identical guarantees.

### Amazon SQS

Amazon SQS issues a receipt handle for each receive action, and documentation
advises using the most recent handle when deleting. `ChangeMessageVisibility`
requires a receipt handle, applies a new visibility interval from the call, and
has an explicit maximum. AWS also documents invalid or no-longer-in-flight
receipt failures. This reinforces three separations that AnonSync needs:
logical message identity, one processing attempt's receipt, and a bounded
visibility/lease interval.

Primary sources:

- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_ChangeMessageVisibility.html
- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_DeleteMessage.html
- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-queue-message-identifiers.html
- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/troubleshooting-api-errors.html

SQS semantics are not copied literally. In particular, AnonSync's current
receipt is a local SQLite authority record, not a managed-service token, and no
remote delete protocol exists yet.

### Google Cloud Pub/Sub

Google's exactly-once delivery documentation describes expired acknowledgement
IDs as invalid and requires the latest valid delivery's acknowledgement ID.
Its lease-management documentation describes periodic deadline extension,
per-extension bounds, and a maximum total extension period, while warning about
the duplicate/delayed-redelivery tradeoff. This closely supports rev0871's
choice to preserve attempt identity during heartbeat while bounding cumulative
lifetime.

Primary sources:

- https://docs.cloud.google.com/pubsub/docs/exactly-once-delivery
- https://docs.cloud.google.com/pubsub/docs/lease-management

AnonSync does not claim Pub/Sub exactly-once delivery. It has no authenticated
receiver acknowledgement or managed lease service, and duplicate sends remain
possible.

### OASIS AMQP 1.0

AMQP 1.0 transport gives each unsettled delivery attempt a delivery tag unique
on its link while unsettled and distinguishes unsettled outcome from terminal
settlement. That supports treating attempt identity and settlement state as
first-class protocol concepts rather than deriving them from a logical message
key.

Primary source:

- https://docs.oasis-open.org/amqp/core/v1.0/csprd01/amqp-core-transport-v1.0-csprd01.html

AnonSync does not implement AMQP framing, links, dispositions, or settlement.

### SQLite transactions and WAL

SQLite documents that `BEGIN IMMEDIATE` begins a write transaction immediately
and can return `SQLITE_BUSY` when another write transaction is active. SQLite's
WAL documentation states that readers and a writer can coexist, but there is
still only one writer at a time. These facts justify moving unrelated CSPRNG
latency out of the writer interval and retaining an exact transactional
publication for the authoritative row and its cutpoint metadata.

Primary sources:

- https://sqlite.org/lang_transaction.html
- https://sqlite.org/wal.html

This does not prove cross-process scheduling fairness, cross-host leases, a
particular durability mode, or power-loss behavior.

## Speculative architecture from this cutpoint

### 1. Authenticated terminal receiver record

The next vertical slice should carry destination, folder, operation ID, payload
commitment, and opaque current claim through a canonical wire request. The
receiver should return a terminal record bound to the exact request and its own
durable cutpoint. Structural hashing is insufficient; the transport or record
must authenticate the receiver identity and actor/membership epoch.

A capacity-blocked or retryable receiver result must never authorize sender
settlement. Terminal retained/already-retained outcomes and explicit
backpressure need different types.

### 2. Receiver idempotency and effect ownership

Retained canonical operation evidence should be the receiver's idempotency
ledger, but filesystem-visible effects need their own atomic owner. A duplicate
attempt must either observe the exact already-published effect or resume an
unfinished effect without applying it twice. The operation, payload chunks,
temporary file, final rename, metadata, and terminal receipt need one documented
crash matrix.

### 3. Clock and scheduler owner

A production lease API should not trust arbitrary caller epochs. Persist a clock
high-water mark or another rollback policy, define which clock source is used,
and make wake scheduling an owned durable component. Heartbeats should run from
measured remaining work, not fixed blind polling. Scheduler death, long pause,
clock jump, restart, and lease cap exhaustion need explicit outcomes.

### 4. Bounded retry and poison policy

Move backoff calculation into pure policy. Inputs should include attempt count,
error class, per-folder limits, deterministic or explicit jitter entropy, and a
maximum age/attempt budget. Exhaustion should produce a durable poison or
operator-action state, not an infinite hot loop or an indefinitely stranded
intent.

Persist enough scheduling provenance to revalidate the delay after restart.

### 5. Point-read owner with full-oracle differential checks

Use the maintained schedule index to identify one ready key without restoring
history. Read the exact intent and the minimum metadata necessary to prove its
cutpoint, then perform a conditional update. Keep the existing full restore as
an oracle in tests, periodic audits, migration, and repair. Randomized
state-machine testing should run both paths and compare snapshots after every
transition.

### 6. Two-process transport crash matrix

The next integration harness should run separate sender and receiver processes
and crash at least at these boundaries:

- before send;
- after send before receiver transaction;
- during receiver publication;
- after receiver commit before response;
- after response before sender settlement;
- during sender settlement; and
- after lease expiry while either process is paused.

The expected result is at-least-once request delivery, idempotent retained
evidence/effect ownership, and exact receipt-fenced sender retirement—not a
vague exactly-once slogan.

### 7. Actor, membership, and privacy authority

Canonical IDs and unkeyed digests do not authenticate who authored an
operation. Add signed actor/key epochs, membership authorization, rotation,
revocation, recovery, rollback resistance, and old-epoch treatment before
trusting remote evidence.

Separately define the privacy adversary. Device IDs, timing, folder membership,
operation sizes, retries, dependency shape, IP metadata, and access patterns are
observable unless deliberately protected. The project name must not be treated
as a privacy guarantee.

## Validation interpretation

Rev0871's strongest claims should remain exact and local:

- the pure lease state machine has one shared current/stale/expired classifier;
- expiry revokes settlement, release, and renewal at an exclusive deadline;
- heartbeat preserves attempt identity, never shortens, and obeys a cumulative
  lifetime ceiling;
- persisted active claims obey that lifetime ceiling on restore;
- API-minted retry delay is bounded;
- changing lease mutations compare the complete prior row and publish through
  one re-attested SQLite cutpoint;
- a no-op heartbeat does not advance generation;
- process death during renewal restores the prior deadline; and
- TEMP-trigger mutation cannot escape precommit re-attestation.

The release evidence records exact compiler, sanitizer, static-analysis, stress,
registered-test, audit, lineage, patch-replay, manifest, directory, and ZIP
checks. Those checks do not establish authenticated remote behavior, full
formal verification, production performance, hardware durability, or privacy.

## Bottom line

Rev0871 turns the dispatch deadline from a replacement hint into a real local
authority boundary and adds the bounded heartbeat needed to keep legitimate
long-running work alive. The most important refactor is not merely fewer lines:
all changing lease transitions now pass through one exact publication and
re-attestation path, while unnecessary entropy latency has been moved outside
SQLite's one-writer interval.

The cube is becoming a credible local correctness oracle for evidence and sender
intent. It is not yet a synchronization product. The next decisive mission step
is an authenticated, attempt-bound, two-process receiver protocol with
idempotent durable effect ownership, followed by a narrow incremental path that
is continuously checked against this full-history oracle.

## Publication validation and correction history

The published tree was reconstructed into an isolated path from the sealed
rev0870 parent and exactly nine intended active-file replacements. This was not
cosmetic. During validation, a delayed, unintegrated delivery-protocol side
branch rewrote the earlier worktree after an initial residue scan. It added
unexercised wire APIs, protocol files, and CMake registrations, then left an
owner declaration/definition mismatch once those files were removed. Shipping
that state would have widened the authority surface without a coherent tested
vertical slice. The publication tree therefore does not descend from that
contaminated directory; it is an exact parent-plus-patch reconstruction. A
full active-projection replay proves all 337 active files byte-for-byte.

Validation on that isolated final source records:

- a clean GCC 14 Debug all-target build, followed by a zero-step dependency
  closure rebuild;
- all 174 registered tests covered with no failure: the main command window
  observed 173 passes and had started the declared serial test when the tool
  window ended, and that exact remaining test then passed in isolation. A
  single uninterrupted 174-test invocation is deliberately not claimed;
- 53/53 registered source and structure audits;
- 2,232/2,232 focused runtime checks under GCC Debug;
- 2,232/2,232 focused runtime checks under Clang 17 Release with warnings as
  errors;
- 2,232/2,232 focused runtime checks under GCC 14 ASan/UBSan with leak
  detection, including instrumented bundled SQLite;
- 20/20 repeated SQLite-owner runs, totaling 2,260 checks;
- 21/21 pure lease source-audit checks and 40/40 SQLite-owner source-audit
  checks;
- zero diagnostics for three production translation units under Clang's
  default interprocedural analyzer and for the SQLite owner under an explicitly
  bounded shallow, no-IPA analyzer scope; and
- exact patch replay from the verified rev0870 archive across all 337 active
  files, with nine modified files, no additions, and no removals.

These results validate the stated C++ correctness slice and packaging lineage.
They do not convert the remaining nonclaims into production guarantees.
