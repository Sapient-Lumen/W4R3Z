# AnonSync rev0873 — retry-release provenance audit

## Executive finding

AnonSync's sender-side outbox already retained a retry deadline, but through
rev0872 it discarded the accepted time observation that minted that deadline.
The live API checked `retry_not_before_epoch - now_epoch <= 86400` and then
persisted only `retry_not_before_epoch`. After restart, the durable row could
still delay work, but it could no longer prove whether the original release was
within policy. The database retained the consequence and discarded the fact
that authorized it.

That is the opposite of the project's central rule:

> Exact history is authority; summaries are acceleration.

Rev0873 repairs this boundary. Every newly released retry now retains the exact
accepted release observation and a durable provenance tag. Exact rows can be
revalidated after restart. Older v2/v3 rows are migrated without fictional
history: their deadline remains exact, while the missing observation is labeled
`LegacyUnproven`. A new claim clears that marker; a later release can mint exact
provenance. Schema v4, the outbox digest, the cutpoint digest, exact conditional
updates/deletes, migration, staged precommit restoration, tests, structural
audits, and sanitizer target coverage all recognize the new authority bytes.

This is a narrow sender-side correctness advance. It does not create trusted
physical time, authenticated receipts, exactly-once effects, a receiver owner,
or a production retry scheduler.

## Heart of the mission

AnonSync is an evidence-authorized, crash-consistent, bounded convergence engine
under construction. The mission is not merely to copy current files. It is to
make every state transition answer four questions without hand-waving:

1. What exact bytes or observation authorize this transition?
2. Which owner is allowed to interpret those bytes?
3. At what crash-consistent cutpoint does the authority become durable?
4. Which limits prevent hostile or accidental work from growing without bound?

The architectural chain remains:

1. **Canonical operation identity.** Freeze exact canonical operation bytes
   before deriving the immutable operation ID.
2. **Exact causality.** Retain immediate parent identities. Summary clocks and
   indexes may locate work but may not replace parent evidence.
3. **Actor and membership authority.** Bind operations to authenticated key,
   actor, membership, rotation, revocation, and recovery epochs.
4. **Crash-consistent publication.** Publish evidence, projections, counters,
   payload commitments, sender intent, dispatch state, and effect state at
   explicit atomic cutpoints.
5. **Deterministic projection.** Equivalent authorized evidence and trust state
   must produce equivalent active and visible state.
6. **Bounded dissemination.** Bound identities, evidence, dependencies, bytes,
   CPU, retries, attempts, storage, clock movement, and wake work.
7. **Receiver effect ownership.** Bind terminal receiver evidence to exactly one
   idempotent, crash-consistent visible effect.
8. **Privacy with a stated adversary.** Define observable metadata and key
   lifecycle before claiming anonymity, unlinkability, or traffic resistance.

A compact form is:

> No untrusted input, missing fact, crash frontier, duplicate, stale receipt,
> schema shortcut, time movement, retry decision, resource claim, or local
> pressure response may silently gain authority.

Rev0873 addresses one missing fact in item 6: the accepted observation that
minted durable retry delay.

## The defect in exact terms

Suppose a live claim is released at accepted epoch 500 with a requested delay of
30 seconds. The old transition validated the request and wrote:

```
retry_not_before_epoch = 530
```

After restart, the row did not retain `500`. It therefore could not distinguish
among these histories:

- released at 500 with delay 30 — valid;
- released at 1 with delay 529 — invalid under the 24-hour ceiling;
- migrated from an old schema that never retained release time;
- directly rewritten and rehashed by an attacker outside the unkeyed-store
  threat model.

The deadline was exact, but its policy provenance was not. Reconstructing
`release = deadline - max_delay` would only create a lower bound. Calling that
value the original observation would invent history. Accepting every restored
row merely because the deadline exists would make the maximum retry delay a
one-time input check rather than a durable invariant.

## Authority taxonomy

Rev0873 distinguishes values that were previously conflated.

### Exact retry deadline

`retry_not_before_epoch` is the exact earliest accepted claim time for the next
attempt. It remains operative for both exact and migrated rows.

### Exact release observation

`retry_released_at_epoch` is the accepted owner-time observation used by the
current release transition. It is retained only when the current implementation
actually observed it.

### Provenance state

`SyncReplicaOutboxRetryReleaseProvenance` has explicit durable numeric values:

- `None = 0`: no retry schedule is active;
- `Exact = 1`: release observation and deadline are both retained; and
- `LegacyUnproven = 2`: an older schema retained the deadline but discarded the
  exact release observation.

The enum values are protocol bytes, not incidental compiler layout.

### Clock high-water

The rev0872 singleton clock records the greatest accepted liveness observation
for the local owner. It prevents rollback of accepted time. It is related to,
but not a substitute for, the exact per-release observation. One is a global
anti-rollback fence; the other explains the minting of one retry schedule.

### Caller input

`now_epoch` remains caller-supplied. The owner can reject rollback and preserve
what it accepted, but it cannot prove that an accepted far-future value
corresponds to trustworthy physical time. Rev0873 deliberately does not relabel
input as a trusted clock.

## State-machine invariants

The pure lease validator now accepts only reachable shapes.

### Untouched intent

- `dispatch_attempts == 0`
- no claim fields
- retry deadline and release observation are zero
- provenance is `None`

### Active claim

- dispatch attempts are positive;
- claim, worker, claim time, and exclusive deadline are all present;
- retry deadline and release observation are zero;
- provenance is `None`; and
- the cumulative claim lifetime is bounded.

### Exact released retry

- dispatch attempts are positive;
- active claim fields are absent;
- retry deadline is nonzero;
- release observation is positive;
- provenance is `Exact`;
- deadline is not earlier than release; and
- `deadline - release <= 86400`.

### Migrated legacy retry

- dispatch attempts are positive;
- active claim fields are absent;
- the retained deadline is nonzero;
- release observation is zero; and
- provenance is `LegacyUnproven`.

A legacy marker carrying a nonzero exact release time is rejected because it
would claim simultaneously that the observation is unknown and known. An exact
marker with zero time, reverse time, or over-budget delay is rejected. Unknown
enum values fail closed.

## API correction: relative delay, not caller-computed deadline

The release API now takes `retry_delay_seconds`, not an absolute deadline. The
pure owner performs the authoritative arithmetic:

1. classify the exact receipt as current, stale, or expired;
2. reject stale or expired authority;
3. bound the delay by 24 hours;
4. reject unsigned addition overflow;
5. compute `retry_not_before_epoch = now_epoch + retry_delay_seconds`;
6. retain `retry_released_at_epoch = now_epoch`; and
7. mark provenance `Exact`.

This removes duplicate caller-side arithmetic and makes the stored provenance
and deadline one transition result. A zero delay is allowed and becomes
claimable at the same epoch; it is still represented as an exact release.

## Claim-domain change

A new claim clears retry state, but its token must still bind the exact prior
row from which it was minted. Claim digest domain v2 therefore binds:

- prior dispatch count;
- prior claim ID;
- prior retry deadline;
- prior release observation;
- prior provenance tag;
- current cutpoint digest;
- intent identity and enqueue generation;
- worker, new attempt count, claim time, deadline; and
- 32 injected CSPRNG bytes.

Without this domain change, an exact and a legacy-unproven retry row with the
same deadline could mint the same token under otherwise identical inputs.

The digest remains an unkeyed structural token. It is not a signature or MAC.

## Schema v4

The exact v4 outbox schema adds:

```sql
retry_released_at_epoch_be BLOB NOT NULL
  CHECK(length(retry_released_at_epoch_be)=8),
retry_release_provenance INTEGER NOT NULL
  CHECK(retry_release_provenance BETWEEN 0 AND 2)
```

The owner retains exact schema definitions for v1, v2, v3, and v4. It does not
use a permissive “close enough” migration. `sqlite_schema` object type, name,
attachment target, and stored SQL must match the full accepted historical
contract before rows are interpreted.

The current outbox digest domain advances from v2 to v3 and binds both fields.
The current cutpoint domain advances from v3 to v4. Historical digest functions
remain separate so old rows can be attested using the bytes and domains they
actually published.

All current insert, exact update, and exact delete statements include the two
new fields. A trigger or competing writer cannot alter only provenance while
allowing the owner to report success: the affected row is compared exactly and
then the entire staged cutpoint is independently restored before commit.

## Migration without invented history

The v3-to-v4 path is the important case. Exact rev0872 v3 state already contains
the clock row but not release observations.

Migration runs inside the constructor's `BEGIN IMMEDIATE` transaction:

1. exact v3 schema is attested;
2. meta and cutpoint v3 are attested;
3. canonical operations, parent edges, local map, projections, outbox rows, and
   clock row are independently restored;
4. each inactive dispatched row is labeled `LegacyUnproven` with release epoch
   zero;
5. the old outbox/meta/clock protocol surfaces are replaced by exact v4
   surfaces;
6. the original clock high-water is reinserted unchanged;
7. a v4 outbox digest and cutpoint are derived over the explicit marker; and
8. full staged restoration must equal the intended migrated state before
   commit.

V1 and v2 migrate through the same destination. They retain only the facts their
old rows prove. For a legacy released row, the migration clock floor uses the
strongest conservative lower bound reconstructible from the deadline and the
fixed maximum delay, never a guessed exact release. Exact rows use their exact
retained observation.

The marker is self-erasing through normal progress: the next successful claim
clears all retry state, and the next release records exact provenance.

## Crash, tamper, and restart audit

The focused tests cover:

- exact release observation and deadline retained in memory;
- exact provenance survives SQLite restart;
- a new claim clears prior exact or legacy provenance;
- an over-budget exact row is rejected on restore;
- a retry schedule without provenance is rejected;
- a legacy marker with a guessed nonzero release time is rejected;
- exact v3 schema and cutpoint fixture migration to v4;
- v3 clock high-water preserved byte-for-byte in meaning;
- v3 released deadline preserved while the history gap is labeled;
- claimability immediately before and at the retained deadline;
- post-migration exact release and restart;
- direct zeroing of an exact release observation rejected;
- exact-to-legacy provenance downgrade rejected;
- TEMP-trigger mutation after the owner's UPDATE caught by staged
  re-attestation; and
- the failed precommit publication rolls back both row and clock prefix.

The separate time-fence primitive has its own production translation unit and
runtime test. An audit found that its test had been registered with CTest but
was omitted from the sanitizer target lists. Rev0873 adds both the library and
test to the sanitizer compile graph and the executable to the sanitizer link
graph. This is a build-evidence correction, not only a code organization change.

## Refactor: make the time fence one owner

The rev0872 anti-rollback function lived in the lease implementation even though
it has no claim, worker, retry, token, or digest semantics. Rev0873 moves it to:

- `src/sync_replica_outbox_time_fence.hpp`
- `src/sync_replica_outbox_time_fence.cpp`
- `tests/sync_replica_outbox_time_fence_test.cpp`

The lease library depends on the time-fence library. The separation reduces the
chance that future clock acquisition, boot identity, or anomaly policy becomes
entangled with receipt minting. The primitive still has deliberately tiny
semantics: positive observations only, equality is idempotent, forward movement
is accepted, rollback is rejected.

## Waste corrected

Several forms of avoidable waste are reduced.

### Discarded evidence

The system no longer spends I/O to persist a deadline while throwing away the
observation needed to revalidate its policy bound.

### Duplicate arithmetic

Callers no longer compute absolute retry deadlines that the policy owner then
checks. The owner receives a duration and creates the exact pair atomically.

### Migration fiction

Migration does not populate a plausible-looking timestamp merely to avoid a
nullable concept. The explicit provenance enum is cheaper than carrying a lie
through every future audit.

### Audit drift

The structural audits previously encoded rev0872 token expectations. Rev0873
updates them to require all new state, digest, schema, SQL, migration, runtime,
verifier, and build-graph surfaces. The audits now fail if the provenance fields
are removed from any one of those places.
Malformed v1/v2 migration test identifiers and messages that still said
`into_v3` were corrected to `into_v4`; stale version labels are an audit
hazard because they can make a valid failure point look like the wrong
protocol boundary.

### Instrumentation gap

The independently compiled time-fence test is now included in sanitizer lanes,
closing a gap between CTest registration and instrumented-build claims.

## Online primary-source research

Research was checked on 2026-07-21 against primary documentation.

### SQLite schema changes and transactions

SQLite documents a limited `ALTER TABLE` surface and a generalized table-rebuild
procedure for other schema changes. It also documents that `BEGIN IMMEDIATE`
starts a write transaction immediately and that only one write transaction may
exist at a time. Those properties support AnonSync's explicit full-surface
replacement inside one transaction rather than an opportunistic partial
migration.

- https://www.sqlite.org/lang_altertable.html
- https://sqlite.org/lang_transaction.html

The inference is AnonSync-specific: exact historical schema attestation before a
transactional rebuild is stricter than SQLite itself requires, but it is
appropriate when schema text is protocol evidence.

### SQS visibility and retry ownership

Amazon SQS treats visibility as a bounded processing lease: an un-deleted
message becomes visible again after the timeout; applications can heartbeat the
timeout; and the total visibility horizon is bounded. SQS also distinguishes
visibility timeout from initial delivery delay and provides dead-letter queues.

- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html
- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/best-practices-processing-messages-timely-manner.html
- https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-delay-queues.html

AnonSync should copy the separation, not the service API: immutable work
identity, one attempt's receipt, its lease, retry scheduling, and terminal
effect evidence should remain different protocol objects.

### Pub/Sub acknowledgment, lease, retry, and dead-letter semantics

Google Pub/Sub documents acknowledgement deadlines, lease extensions,
redelivery, exactly-once acknowledgement behavior, retry policy, and dead-letter
forwarding as separate mechanisms. Exactly-once delivery support concerns
message delivery/acknowledgement semantics; it does not by itself make an
arbitrary external filesystem side effect transactional.

- https://docs.cloud.google.com/pubsub/docs/exactly-once-delivery
- https://docs.cloud.google.com/pubsub/docs/lease-management
- https://docs.cloud.google.com/pubsub/docs/subscription-retry-policy
- https://docs.cloud.google.com/pubsub/docs/dead-letter-topics
- https://docs.cloud.google.com/pubsub/docs/pubsub-basics

The design implication is that AnonSync still needs a receiver-side effect owner
and terminal authenticated receipt. Sender-side claim settlement cannot create
exactly-once visible files by itself.

### Linux time

Linux documents that `CLOCK_REALTIME` can change and absolute times based on it
are affected, while monotonic clocks have different semantics. Boot-relative
clocks are not automatically stable persisted epoch identifiers.

- https://man7.org/linux/man-pages/man3/clock_gettime.3.html

Rev0873 therefore retains accepted caller epoch observations honestly but does
not claim a trusted cross-reboot clock.

## What is still severely missing

### Owned time acquisition and anomaly recovery

The caller still supplies epoch time. A far-future accepted value can ratchet the
clock into persistent denial of service. A future owner should likely bind:

- wall-clock sample;
- boot-relative monotonic/boottime sample;
- boot identity;
- prior durable anchor;
- maximum forward-step policy;
- uncertainty and suspend semantics;
- anomaly quarantine reason; and
- explicit operator or quorum recovery.

Persisting raw `CLOCK_MONOTONIC` or `CLOCK_BOOTTIME` values without boot identity
would be wrong. A hybrid logical clock can order events but does not prove
physical lease expiry.

### Complete retry provenance

Rev0873 preserves release time and deadline, but a production retry owner should
also retain or derive under an exact policy version:

- failure classification and whether it is retryable;
- attempt number and first-attempt age;
- base delay, multiplier, cap, and jitter algorithm;
- exact random jitter input or deterministic derivation domain;
- next wake index/key;
- maximum attempts and maximum age;
- poison/dead-letter/quarantine terminal state; and
- policy-generation migration semantics.

A bare deadline is not enough to explain *why* work is delayed.

### Receiver-side protocol

There is no authenticated canonical delivery request, receiver request ID,
receiver-side idempotency ledger, exact payload/chunk materializer, prepared
visible effect, atomic rename/publication owner, or signed terminal receipt.
Network ambiguity can still cause duplicate sends and effects. The next major
vertical slice should make a receiver terminal record the only authority that
settles sender work.

### Cryptographic authority

Claim, outbox, clock, and cutpoint digests are unkeyed. They detect accidental
or unauthoritative structural mismatch only when the attacker cannot rewrite
and rehash the whole store. Actor signatures/MACs, trust anchors, key rotation,
revocation, recovery, forward secrecy, and post-compromise rules remain absent.

### Production scaling

`SyncReplicaSqliteOwner` intentionally reloads full retained history, reprojects
state, scans the outbox, and performs a full staged restore before changing
commits. That is valuable as a reference oracle, migration verifier, periodic
auditor, and repair authority. It is not a production-scale projector. The
incremental path should be built beside it and continuously compared against it,
not replace it prematurely.

### Privacy

The project still lacks a complete adversary model. Encryption alone would not
hide peer graph, timing, volume, retry cadence, file count, operation lineage,
or access pattern. “Anon” remains a mission target, not a demonstrated property.

## Recommended next sequence

1. **Receiver request and terminal receipt owner.** Canonical request bytes,
   receiver idempotency, prepared/applied effect states, crash tests, and an
   authenticated receipt trust anchor.
2. **Owned clock observation.** Boot identity, dual-clock anchor, bounded
   forward movement, anomaly quarantine, and recovery.
3. **Retry policy object.** Exact policy generation, deterministic jitter,
   attempt age, poison/dead-letter state, and indexed wake scheduling.
4. **Incremental SQLite sender path.** Point reads and exact conditional
   updates, continuously differential-tested against the full reference owner.
5. **Payload materialization.** Chunk commitments, bounded staging, fsync/rename
   protocol, and effect receipt binding.
6. **Key and membership lifecycle.** Signatures/MACs, rotation, revocation,
   recovery, rejoin, and compromised-actor semantics.
7. **Causal stability and compaction.** Only after membership and rejoin rules
   can prove when evidence is safe to retire.
8. **Privacy threat model and mitigations.** Define the adversary before making
   anonymity or metadata claims.

## Deliberate nonclaims

Rev0873 does not claim:

- trusted physical time or cross-reboot monotonic time;
- bounded forward clock movement or anomaly recovery;
- authenticated local storage;
- keyed cutpoint, claim, clock, or outbox seals;
- authenticated sender or receiver identities;
- authenticated terminal receiver receipts;
- receiver-side idempotent effects or exactly-once filesystem publication;
- complete retry policy, exponential backoff, jitter, maximum age, or
  dead-letter state;
- production transport or two-process sender/receiver integration;
- production-scale incremental projection;
- arbitrary Byzantine convergence or Sybil-resistant fairness;
- causal stability, compaction, or tombstone collection;
- complete physical resource bounds;
- confidentiality, anonymity, unlinkability, or metadata hiding;
- secure erasure, forward secrecy, or post-compromise security;
- formal proof, ThreadSanitizer coverage, Windows runtime behavior, or hardware
  power-loss guarantees.

The exact publication authority for claims is `RELEASE_GATE.json` and
`REVISION_EVIDENCE/rev0873/`, not this narrative.
