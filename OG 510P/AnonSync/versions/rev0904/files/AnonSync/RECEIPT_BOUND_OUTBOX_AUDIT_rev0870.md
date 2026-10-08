# AnonSync rev0870: receipt-bound outbox authority audit

## Executive diagnosis

The heart of AnonSync is **authority-preserving convergence**. Exact canonical
operation bytes and exact immediate causal edges are durable facts. Visible
state, active state, counters, capacity summaries, leases, retries, worker
ownership, and acknowledgements are interpretations or capabilities derived
from those facts. The system remains correct only when a crash, timeout,
duplicate, stale response, schema mutation, pressure decision, or optimization
cannot grant a derived record more authority than its exact durable cutpoint.

Rev0869 established the first SQLite cutpoint that jointly owns canonical
evidence, causal projection, local mint authority, policy, and lightweight
sender intents. Its outbox settlement API, however, identified only the logical
intent `(destination, operation)`. That identifier remains stable across every
retry. Once multiple workers and lease expiry are introduced, a stable logical
identifier is not enough to prove that a response belongs to the current
attempt.

Rev0870 makes dispatch attempts explicit durable authority. Each claim mints a
fresh receipt bound to the exact prior cutpoint and the exact new lease. The
receipt—not the passage of time—authorizes settlement or retry release. Expiry
only permits replacement. This is the same categorical separation used
elsewhere in AnonSync: a summary may locate a fact, but only the exact authority
record may change ownership of that fact.

## The stale-settlement failure

The dangerous schedule is small:

1. durable intent `I=(D,O)` exists;
2. worker A claims `I` and sends operation O to destination D;
3. A's response path stalls or A crashes after the remote side acts;
4. A's lease expires;
5. worker B claims the same logical intent and starts a replacement attempt;
6. A's delayed response reaches the sender;
7. an ACK API keyed only by `(D,O)` deletes the intent currently owned by B.

The old response may report a real remote success. It is nevertheless stale with
respect to *sender settlement authority*. The sender no longer knows whether B
has sent, whether B's receiver result differs, or whether the delayed response
belongs to the same authenticated channel and payload. Treating the logical
intent key as an attempt receipt lets historical scheduling state retire current
work.

This audit does not claim that rev0869 had a demonstrated production data-loss
incident. It identifies a protocol-authority gap that becomes reachable as soon
as retry leases or concurrent workers are added. Rev0870 closes the local sender
side before those features are exposed through a transport.

## Correct authority model

One immutable logical intent can have a sequence of attempts:

```
intent I = (destination, operation, enqueue generation)
A1 = claim(I, prior cutpoint, worker A, time, deadline, entropy)
A2 = claim(I, cutpoint containing A1, worker B, time, deadline, entropy)
...
```

At any cutpoint, at most one attempt receipt is current. The rules are:

- an unclaimed, non-backed-off intent may be claimed;
- a backed-off intent may be claimed only at or after its retry time;
- an active intent may be replaced only at or after its lease deadline;
- replacement mints a new receipt and increments attempt count;
- only the exact current receipt may settle the intent;
- only the exact current receipt may clear ownership and install backoff;
- expiry by itself never settles, releases, or deletes anything;
- missing and stale receipts are no-ops, not aliases for success; and
- malformed identities fail before transaction work.

This separates three concepts that are often accidentally conflated:

1. **logical identity:** which immutable destination/operation intent exists;
2. **liveness ownership:** which worker is currently expected to act, and until
   when; and
3. **settlement capability:** which exact attempt response may retire or release
   the intent.

## Pure C++ lease authority

`SyncReplicaOutboxLeaseState` names every durable attempt field:

- `dispatch_attempts`;
- `claim_id`;
- `worker_id`;
- `claimed_at_epoch`;
- `lease_expires_at_epoch`; and
- `retry_not_before_epoch`.

The pure validator rejects partial ownership. Claim ID, worker, claim time, and
lease deadline are all present or all absent. An active claim must have a prior
attempt count, a lowercase SHA-256 claim ID, a valid worker ID, a deadline
strictly after claim time, and no retry backoff. An unclaimed intent with zero
attempts cannot carry backoff because that would invent retry history with no
attempt provenance.

The strict `deadline > claimed_at` rule was added during the audit. A
zero-duration active lease was structurally complete but unreachable through
the public claim API, which requires 1..86400 seconds. Persisted-state validation
must reject unreachable states; otherwise a local edit can create a semantic
condition no legitimate transition can explain.

Claimability uses inclusive boundaries. Backoff ending at `T` permits a claim at
`T`. A lease expiring at `T` permits replacement at `T`. Zero time is rejected,
lease arithmetic is checked for overflow, and attempt count cannot wrap.

## Receipt construction

The owner obtains exactly 32 bytes from OpenSSL `RAND_bytes` and verifies the
return status. The pure policy receives those bytes as input; it performs no
hidden randomness or clock access. This makes the transition reproducible under
unit tests and leaves process-local entropy ownership visible in the SQLite
boundary.

The claim ID is a SHA-256 digest with domain
`anonsync-sync-replica-outbox-claim-v1`. Its framed material binds:

- folder identity;
- destination identity;
- operation identity;
- enqueue generation;
- current SQLite cutpoint digest;
- prior dispatch-attempt count;
- prior claim ID;
- prior retry-not-before value;
- new worker identity;
- new attempt count;
- exact claim time;
- exact lease deadline; and
- the 256-bit entropy input.

The current cutpoint digest already binds the full prior outbox row, including
prior worker and lease times. The additional explicit prior fields make token
intent legible and resist accidental weakening if cutpoint composition changes.
The receipt is a local capability token, not an actor signature or proof from the
receiver.

## Durable SQLite cutpoint

Schema v2 extends each lightweight intent with exact attempt state. Numeric
values are fixed-width big-endian BLOBs. Claim ID and worker ID are text with
semantic validation on restore. The outbox digest frames every field, and the
schema version is bound into the cutpoint digest.

Every claim performs one IMMEDIATE transaction:

1. prove typed write authority;
2. load and fully attest the current schema-v2 cutpoint;
3. scan canonical outbox order for the first eligible intent, optionally within
   one destination;
4. obtain fresh CSPRNG entropy;
5. apply the pure claim transition;
6. update the exact prior outbox row;
7. retrieve the canonical operation from the restored model;
8. increment state generation and recompute metadata/digests;
9. reload and independently re-attest the complete staged cutpoint; and
10. commit.

Settlement and release follow the same old-cutpoint/staged-cutpoint discipline.
The SQL `WHERE` clause names the primary key, enqueue generation, and every
previous lease/backoff field. `sqlite3_changes()` must report exactly one row.
A connection-local TEMP trigger or competing writer cannot silently retarget a
claim transition while preserving its logical key.

No-ready, missing-intent, and stale-receipt paths commit durable no-ops without
advancing generation. They still perform the global restore because this owner
is the correctness oracle. That cost is intentional and must not be confused
with a production point-read implementation.

## Exact schema-v1 migration

Rev0869's complete eight-object schema is retained verbatim as
`kLegacySchema`. Migration is accepted only when `main.sqlite_schema` exactly
matches that contract and the full legacy cutpoint independently restores:
canonical operation bytes, parent edges, local counter mapping, model state,
projection rows, limits, counters, outbox rows, and all structural digests.

Only after that proof does the same IMMEDIATE transaction drop the legacy meta
and outbox surfaces, create schema v2, insert the preserved intents with empty
lease state, increment state generation, recompute v2 digests, reload the entire
staged v2 cutpoint, and commit.

This ordering prevents migration from becoming a repair or laundering path. The
malformed-v1 test changes an enqueue generation to an impossible value. Owner
construction rejects the legacy cutpoint, and rollback leaves schema version 1
and no schema-v2 schedule index. A valid fixture migrates, preserves evidence,
local mint authority, and policy, then supports claim persistence and exact
settlement across restart.

## Crash and concurrency boundaries

The owner test covers two distinct process crash frontiers:

- rev0869's crash after outbox insertion but before commit; and
- rev0870's crash after lease-row update but before metadata publication and
  commit.

Both probes enter the project's pinned self-exec process owner rather than
running SQLite in a raw post-fork child. The parent reopens and fully attests the
database. It sees either the old committed cutpoint or the complete new one,
never a lease row whose metadata/digest generation did not advance with it.

A competing-worker test opens independent owners. The IMMEDIATE write
transaction serializes claim authority, and exactly one worker receives the
current attempt. This proves local single-database serialization. It does not
claim a distributed lease service or cross-host clock safety.

The stale-receipt test then lets one claim expire, creates a replacement, and
submits the first receipt to both settlement and retry release. Both return
`StaleClaim`; state generation and the replacement row remain unchanged. The
current receipt can still settle.

## Audit/refactor results

### Corrected now

- logical-intent ACK used as attempt authority;
- expiry accidentally positioned to become implicit settlement authority;
- partial and unreachable persisted lease states;
- primary-key-only mutation comparison;
- caller-local retry state that would disappear on restart;
- hidden randomness inside a policy transition;
- migration before exact legacy attestation;
- convenience APIs capable of bypassing receipt fencing; and
- package verification that did not yet require the new authority slice.

### Still intentionally expensive or wasteful

- claim selection loads and validates all retained evidence and all outbox rows;
- every outbox mutation globally rederives model and projection;
- every mutation rewrites complete metadata and may rewrite other projection
  surfaces through the reference owner;
- the schedule index is maintained but the current correctness path does not use
  it to avoid O(history) work;
- CSPRNG acquisition occurs while an IMMEDIATE transaction is open;
- no batched claim/settlement API amortizes full-cutpoint verification; and
- no checkpointed proof permits a narrow point read to stand alone.

The schedule index is therefore future query shape, not a current speedup. If a
point-read design is delayed, removing the unused index would reduce write
amplification at the cost of another schema migration later. The preferable
next step is to use it in a bounded candidate query while comparing the result
against the global oracle in tests and periodic audit.

### Remaining authority gaps

- claim IDs are not carried by an authenticated wire protocol;
- no receiver terminal result is cryptographically bound to claim, destination,
  operation, payload, membership epoch, or channel identity;
- no receiver-side idempotency ledger owns duplicate effects;
- no heartbeat or lease-extension transition exists;
- retry backoff is caller-supplied absolute time, not a persisted bounded policy;
- no wake scheduler or poison/dead-letter state exists;
- caller clock rollback can delay liveness;
- the local cutpoint and receipt digests are unkeyed;
- no rollback-resistant monotonic local authority exists; and
- the owner remains reference-scale O(history).

## Online primary-source synthesis

The sources below are design analogies and storage semantics, not compliance
claims. Accessed 2026-07-21.

### AMQP 1.0 transport

OASIS AMQP 1.0 Part 2 describes assigning a delivery tag to track a delivery
while it is unsettled. The tag must be unique among deliveries that either end
could still consider unsettled. Settlement is the point at which the endpoint
forgets the delivery association; recovery exchanges unsettled state. The
standard also explains that at-least-once recovery can resend and therefore
produce duplicate processing.

Source:
https://docs.oasis-open.org/amqp/core/v1.0/csprd01/amqp-core-transport-v1.0-csprd01.html

AnonSync inference: a logical operation ID should not double as the identity of
every dispatch attempt. The local claim ID serves an analogous attempt-level
tracking role. Rev0870 does not implement AMQP framing, link recovery,
dispositions, transactions, or its delivery guarantees.

### Amazon SQS receipt handles and visibility timeout

The SQS `DeleteMessage` API documents that each receive returns a unique receipt
handle, repeated receives of the same message return different handles, and
deletion should use the handle from the most recent receive. The visibility
Timeout documentation separates temporary invisibility from explicit deletion
and notes that an expired timeout makes a message available for another attempt;
standard queues remain at-least-once and applications should tolerate duplicate
delivery.

Sources:
https://docs.aws.amazon.com/AWSSimpleQueueService/latest/APIReference/API_DeleteMessage.html
https://docs.aws.amazon.com/AWSSimpleQueueService/latest/SQSDeveloperGuide/sqs-visibility-timeout.html

AnonSync inference: lease expiry should permit another attempt, while the
current attempt receipt should control retirement. Rev0870 is not an SQS clone;
it uses a single local SQLite owner and intentionally returns `StaleClaim`
rather than inheriting SQS's exact API behavior.

### SQLite transactions and WAL

SQLite's transaction documentation states that `BEGIN IMMEDIATE` starts a write
transaction immediately and may fail with `SQLITE_BUSY` if another writer is
active. A read transaction sees one historical snapshot until it ends.

Source:
https://sqlite.org/lang_transaction.html

SQLite's WAL documentation states that readers can proceed with a writer, but
there can be only one writer at a time. Commit is represented by a WAL commit
record, while checkpointing, synchronous mode, VFS behavior, power loss, and
multi-database scope remain distinct durability concerns.

Source:
https://sqlite.org/wal.html

AnonSync inference: one IMMEDIATE transaction is an appropriate local
serialization/publication unit for claim state and metadata, but it does not
prove authenticated storage, cross-host lease safety, or a particular physical
power-loss profile.

## Speculative architecture from this cutpoint

### 1. Authenticated receiver receipt

Carry `claim_id` over an authenticated channel. The receiver should return a
terminal record binding at least folder, destination, operation, exact canonical
operation digest, payload commitment, claim ID, receiver actor/key epoch,
outcome, and protocol version. The sender should settle only after validating
that record under current membership and key policy.

### 2. Receiver idempotency authority

Before applying filesystem effects, the receiver needs a durable ledger keyed by
an authenticated operation/effect identity. Duplicate attempts may repeat
transport work but must not duplicate visible effects. The receiver commit
should atomically bind verified payload materialization, effect state, and the
terminal response it can reproduce after crash.

### 3. Lease extension and scheduler ownership

Add an exact current-receipt lease-extension transition, bounded maximum
lifetime, persisted retry policy, attempt ceiling, jitter source, wake
generation, poison disposition, and clock rollback handling. A scheduler should
own when work becomes runnable; individual workers should not invent durable
policy from process-local timers.

### 4. Point-read acceleration under an oracle

Use the schedule index to select a bounded candidate without loading all history.
Then prove that candidate against narrow signed/digest-bound metadata. In tests,
periodically and under fault injection, compare point-read results and
incremental projection against the current complete restore. The global path
should remain the specification oracle until the accelerated proof is mature.

### 5. End-to-end crash matrix

A two-process sender/receiver test should kill processes at sender claim commit,
mid-transfer, receiver payload commit, receiver terminal-record commit, ACK
transit, sender settlement commit, and lease expiry/reclaim. Each restart should
show that evidence is never lost, stale receipts never retire current work, and
duplicate transfer never duplicates the final effect.

### 6. Security and privacy authority

Bind operations and receipts to actor and membership epochs. Define rotation,
revocation, recovery, old-epoch treatment, rollback detection, forward secrecy,
and post-compromise behavior. Separately model metadata leakage from membership,
path identifiers, dependency graph shape, capacity responses, lease timing,
retries, and traffic volume before claiming anonymity or unlinkability.

## Validation interpretation

Rev0870's focused seven-executable runtime total is 2,198 checks:

- network model: 67;
- hash-graph projection: 1,288;
- allocation atomicity: 688;
- aggregate retained-evidence budget: 26;
- capacity/backpressure: 19;
- pure outbox lease: 19; and
- SQLite owner: 91.

The same executables pass GCC Debug, Clang 17 Release with `-Werror`, and GCC
ASan/UBSan. The owner passes 20 repeated iterations. All 174 registered tests
are covered with no failures, and all 53 registered audits pass. The main CTest
invocation was split at the cloud command boundary, so no claim is made for one
uninterrupted 174-test invocation.

Clang's default interprocedural analyzer completed the pure lease policy and two
core model translation units with zero diagnostics. Shallow, no-IPA analysis
completed the production SQLite owner with zero diagnostics. The much larger
owner test exceeded the command window; syntax and warning-clean compilation,
runtime, sanitizers, and source audits cover it, but a completed static-analyzer
pass is not claimed.

## Bottom line

Rev0870 turns retry settlement from an unversioned logical-key deletion into an
exact durable capability transition. It preserves the rev0869 global oracle,
adds a transactional migration instead of abandoning durable state, and makes
stale responses harmless after lease replacement. The work is still local and
reference-scale. The next mission-critical boundary is to carry this authority
through an authenticated receiver protocol and idempotent payload/effect commit
without weakening the exact evidence cutpoint.
