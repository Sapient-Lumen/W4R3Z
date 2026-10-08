# Outbox Dispatch Guard Audit — rev0881

## Executive finding

AnonSync's sender path had a narrow but serious time-of-check/time-of-use gap.
`claim_next_request_or_throw()` durably minted an exact outbox attempt and then
called arbitrary payload-source code. If that callback returned normally after
releasing, settling, replacing, renewing, or merely aging the attempt, the
service still constructed a frame from the stale claim object captured before
the callback.

The prior pre-dispatch exception handler was useful but insufficient: it could
release a claim when callback, channel, validation, encoding, or digest work
*threw*. It did not prove that a normally returning callback had left the same
claim authoritative.

Rev0881 closes that local construction gap with a scope-bound C++ capability:
`SyncReplicaSqliteOutboxDispatchGuard`. After arbitrary payload code returns,
the SQLite owner re-restores the complete cutpoint, proves exact claim identity,
observes owned time, proves the retained canonical operation, independently
re-attests staged state, and keeps a `BEGIN IMMEDIATE` transaction alive while
the service performs only bounded local request construction. Competing SQLite
writers cannot release, settle, renew, or replace the row during that interval.

This is not described as network exactly-once or atomic database-plus-socket
dispatch. The returned frame can still be delayed after guard commit. A later
transport owner must re-attest immediately before first-byte dispatch or use a
separate durable frame/attempt state machine.

## The failed authority sequence

Before this correction, the sender sequence was effectively:

1. durably claim one outbox intent;
2. copy the claim into ordinary C++ storage;
3. invoke arbitrary payload code;
4. re-check channel liveness;
5. construct and return a frame from the copied claim.

The copied object was evidence of what had once been authorized, not a live
capability. The callback had access to the same owner and could legally perform
other public transitions. A normal return therefore did not imply the attempt
was still current.

Concrete contradictions included:

| Callback action | Durable state after callback | Incorrect old behavior |
| --- | --- | --- |
| exact retry release | same intent, empty claim ID, retry deadline | return frame naming revoked claim |
| exact settlement | intent deleted | return frame for work no longer owed |
| expiry by clock advance | matching claim, deadline reached | return frame after local revocation time |
| replacement claim | same intent, new claim ID/attempt | return frame naming superseded receipt identity |
| valid renewal | same claim ID, later deadline | either use stale row or reject a legitimate heartbeat |
| connection-local trigger corruption | staged rows differ from intended state | risk publishing/using a corrupted cutpoint without independent reload |

The dangerous cases are not hypothetical concurrency only. They are possible by
same-thread reentrancy because the payload source is application-owned code.

## Corrected ownership sequence

### 1. Arbitrary work remains outside the writer capability

Payload acquisition can involve disk I/O, decompression, application callbacks,
or other unbounded work. It remains outside the dispatch guard. Failure still
uses one centralized exact-release helper that preserves the original exception
only after the owner confirms the exact live attempt was moved to bounded retry.

### 2. Exact identity precedes time

`guard_outbox_claim_for_dispatch_or_throw()` starts a typed
`BEGIN IMMEDIATE` transaction and completely restores the causal owner. It then
looks up destination plus operation and compares the current claim ID.

Missing and stale results return without sampling the clock. This ordering is
intentional: an obsolete caller has no authority to ratchet durable liveness
state merely by presenting an old receipt identity.

### 3. Renewal is the only tolerated row change

A valid heartbeat can extend `lease_expires_at_epoch` without changing receipt
identity. The guard therefore accepts only a nondecreasing deadline difference.
Every other intent and lease field must exactly match the originally returned
claim. The owner model and full-state restore still validate the renewed row.

### 4. Owned time decides expiry

Only after exact identity is established does the owner sample its injected
clock source. A matching attempt at or beyond its deadline returns
`ExpiredClaim` and commits the accepted clock observation as durable revocation
evidence. It does not fabricate retry-release provenance.

### 5. Canonical evidence is re-proved

The retained operation is loaded from the canonical evidence model and must
exactly equal the operation carried by the expected claim. A claim ID alone is
not enough to authorize a frame for different bytes or operation metadata.

### 6. Staged state is independently re-attested

The existing pre-commit logic was refactored into
`attest_staged_cutpoint_or_throw()`, which performs the full independent reload
without committing. The normal publication helper now calls that function and
then commits. The dispatch path calls the same function and lets the guard own
the still-live transaction.

This catches connection-local TEMP triggers that can run after an owner update
and silently rewrite the clock or another row inside the same transaction.
Destruction rolls the transaction back.

### 7. Only bounded construction occurs under the guard

While the guard is active, the service:

1. re-proves live channel authority;
2. reconstructs the request from the guard's current claim;
3. moves already-resolved payload bytes into the request;
4. validates the complete file request;
5. encodes the bounded frame;
6. computes its structural digest;
7. constructs the complete outbound value; and
8. commits the guard.

No caller callback and no network I/O occurs in this interval. Static assertions
bind the post-commit return path to no-throw move construction, including the
`std::optional` wrapper, so a frame-construction exception cannot occur after
clock/guard commit and before the outbound value escapes.

Any exception before commit destroys the guard first, rolling back its staged
clock observation and releasing the SQLite writer slot. The centralized helper
then attempts the exact durable retry release.

## Why `BEGIN IMMEDIATE` is appropriate—and insufficient by itself

SQLite documents that only one write transaction can exist at a time and that
`BEGIN IMMEDIATE` starts the write transaction immediately, failing with
`SQLITE_BUSY` when another writer is active:

- https://sqlite.org/lang_transaction.html
- https://sqlite.org/isolation.html

SQLite also describes its write isolation as serializable because writers take
turns. That supports the narrow claim made here: while the guard's transaction
is active, another connection cannot commit a competing outbox transition.

It does not make a SQLite transaction atomic with a socket or a remote
receiver. Holding the database writer while performing network I/O would also
be operationally hazardous. Linux's `send(2)` documentation states that no
failure-to-deliver indication is implicit in a successful send, and send can
block when socket buffers are full:

- https://man7.org/linux/man-pages/man2/send.2.html

Thus even a successful first-byte or full-frame local send would not prove
receiver durability. Receiver idempotency, terminal effect receipts, retry, and
ambiguous-response recovery remain necessary.

## Runtime evidence

The service test now executes five post-callback cases:

- callback-owned exact release is detected as stale and its retry state remains
  byte-for-byte authoritative;
- callback-owned settlement is detected as missing and the intent is not
  recreated;
- exact-boundary expiry commits only the clock revocation and requires a fresh
  attempt ID;
- a valid same-claim renewal is carried into the outbound claim and frame; and
- a wrong payload digest fails under the guard, rolls back the guard, and
  exact-releases the original attempt.

The owner test independently proves:

- the guard is noncopyable and nonmovable;
- a valid intervening renewal is the only accepted row variation;
- a second database connection receives a lock failure while the guard is live;
- commit permanently deactivates the capability;
- stale and missing identities do not sample or advance owned time;
- exact expiry durably advances only the clock cutpoint;
- later attempts require fresh claim IDs; and
- a TEMP trigger corrupting the clock digest is caught before guard escape and
  the whole transaction rolls back.

These are semantic runtime checks. The companion Python audit is explicitly
lexical hygiene, not proof of lock, clock, exception, or syscall behavior.

## Refactor assessment

Two duplications were removed rather than expanded:

- pre-dispatch release/error combination now has one implementation instead of
  repeated catch blocks; and
- staged full-cutpoint re-attestation is a reusable noncommitting primitive,
  with normal publication layered on top.

This matters because authority code tends to drift when the same state matrix is
hand-copied. The refactor makes the dispatch guard reuse the owner's strongest
existing corruption boundary instead of creating a second, weaker verifier.

## Deliberate nonclaims and remaining work

Rev0881 does **not** claim:

- the returned outbound frame remains current indefinitely after guard commit;
- SQLite and transport dispatch form one atomic transaction;
- local `send()` success proves peer receipt, durable evidence, payload
  publication, or terminal effect;
- a receiver will observe exactly one network delivery;
- the current service is production-scale or integrated into `anonsync_core`;
- queued frames receive automatic lease renewal, cancellation, jitter,
  dead-letter handling, or wake scheduling; or
- arbitrary payload sources are bounded, authenticated content stores.

The next coherent transport milestone is one of two designs:

1. **Immediate transport re-attestation.** A transport-owned method accepts the
   outbound frame plus exact claim identity, acquires a short guard immediately
   before the first socket write, and rejects an expired/superseded attempt.
   Ambiguity after any bytes escape still relies on receiver idempotency.
2. **Durable frame ownership.** The sender stores a canonical frame digest and
   attempt binding in an indexed transport outbox. A separate transport worker
   claims that durable frame, renews while queued, and settles only from a
   channel-bound terminal receipt. This is more complex but scales and crashes
   more honestly than retaining an in-memory frame.

A content-addressed payload owner could also resolve and verify payload bytes
before minting a dispatch attempt, shrinking callback reentrancy and lease age.
It must not turn local payload availability into canonical operation identity.

## Mission fit

The correction follows AnonSync's core mission: **historical evidence is not
live authority**. A copied outbox claim, like a copied channel context or a
cached filesystem path, can describe a prior state but cannot authorize a new
side effect without re-observing its owner. The dispatch guard gives that rule a
small C++ type and a tested SQLite serialization boundary.
