# AnonSync rev0872 revision notes

## Durable time fence: expiry cannot revive after rollback

Rev0871 made an outbox receipt invalid at its exclusive deadline. Rev0872 makes
that revocation observation durable.

Before this revision, the SQLite owner accepted caller-supplied `now_epoch` but
did not retain the greatest valid observation. A matching receipt observed
expired at epoch 115 could later be presented at epoch 114 and appear current
again. The transaction mechanics were atomic, but the authority model forgot
its own liveness history.

Rev0872 adds one exact schema-v3 outbox clock row. Valid scheduler observations
and exact matching current or expired receipts may advance the high-water mark.
A lower later observation is rejected. Expired receipt paths commit the clock
observation before returning `ExpiredClaim`, so restart cannot revive the
receipt.

The clock is separate from canonical evidence and `state_generation`. A
no-ready queue observation may advance liveness without falsely claiming that
operation evidence, projection, outbox intent, or policy changed.

This advances the central invariant:

> Exact history is authority; summaries and liveness records are subordinate.
> Time may revoke local attempt authority, but a clock rollback may not recreate
> authority the owner has already observed as expired.

## Principal C++ changes

1. Added `advance_sync_replica_outbox_time_high_water_or_throw`, a pure positive,
   equal-idempotent, forward-only liveness policy.
2. Added `outbox_time_high_water_epoch` and `outbox_clock_digest` to the exact
   SQLite snapshot surface.
3. Advanced the owner schema from v2 to v3 with one STRICT singleton
   `sync_replica_outbox_clock` table.
4. Bound the clock digest to folder ID, local device ID, actor epoch, and exact
   eight-byte high-water value under a separate domain.
5. Added exact conditional clock updates that compare the previous value and
   digest and require one changed row.
6. Included the clock row in complete staged precommit restoration and
   comparison.
7. Made claim scheduling observe time atomically, including the no-ready path.
8. Made exact current and expired settlement, renewal, and release paths observe
   time atomically.
9. Kept missing intents and stale receipts from ratcheting the clock.
10. Made exact expired receipt results commit the revocation observation before
    returning.
11. Preserved clock-only observations without changing evidence state
    generation or cutpoint digest.
12. Added exact schema-v2 restoration and transactional v2-to-v3 migration.
13. Derived a conservative v2 migration fence from retained active claims and
    retry authority without pretending to recover observations v2 never stored.
14. Retained exact v1-to-v3 migration with a zero initial fence.

## Audit/refactor corrections

The primary defect was a history-loss problem at the liveness boundary. Rev0871
could decide that a receipt was expired, but that decision left no durable trace
unless another lease transition happened. Rev0872 gives the decision its own
atomic authority row.

A separate state-machine audit found that restore accepted a row with dispatched
history but neither an active claim nor retry authority. No public transition
can create that shape, yet it was immediately claimable after restore. The pure
validator now rejects it, and a malformed exact-v2 migration test proves it is
not laundered into v3.

The implementation refactor also:

- centralized v2/v3 cutpoint field encoding in one ordered authority appender,
  reducing version drift while preserving exact domains;
- kept all clock SQL explicitly bound to `main.` against TEMP shadowing;
- added a clock-specific staged re-attestation path rather than overloading
  evidence generations;
- added a clock-only process-crash frontier rather than assuming lease-row crash
  tests covered the new table; and
- revised structural audits and the release verifier for the new authority
  surface.

## Exact authority behavior

For valid local scheduling, `now_epoch` is checked against the durable
high-water mark before claimability is used. Equal time is idempotent; larger
time advances; smaller time fails closed.

Receipt paths first establish whether the intent and exact current claim exist.
This order is deliberate:

- missing intent: `IntentMissing`, no clock authority;
- stale receipt: `StaleClaim`, no clock authority;
- exact live receipt: may advance time, then apply or no-op;
- exact expired receipt: advances and commits time, then returns
  `ExpiredClaim`.

A stale worker therefore cannot supply a far-future timestamp to expire or
postpone unrelated current work through this API.

## Schema-v3 migration

The constructor accepts only an empty database, exact current v3, exact rev0871
v2, or exact rev0869 v1. Unknown schema text is rejected rather than repaired.

V1 has no retained time information, so migration seeds zero.

V2 can prove only lower bounds:

- active claim: at least `claimed_at_epoch`;
- released attempt: at least one and no earlier than retry time minus the fixed
  maximum retry delay; and
- untouched intent: zero.

Migration uses the maximum proven bound. It does not claim to recover a prior
expiry observation because v2 never persisted that fact.

## Runtime coverage

`tests/sync_replica_outbox_lease_test.cpp` reports 34 checks. Added coverage
includes positive/equal/forward/rollback high-water semantics and rejection of
unreachable inactive dispatched state.

`tests/sync_replica_sqlite_owner_test.cpp` reports 141 checks. Added coverage
includes:

- clock-only advancement with stable evidence generation and cutpoint;
- durable expiry revocation followed by rollback rejection;
- stale/missing non-ratcheting behavior;
- restart persistence;
- exact v1 and independently constructed v2 migration;
- preservation of a live v2 receipt through migration and restart;
- transactional rejection of malformed v2 state;
- TEMP clock-table shadow resistance;
- TEMP-trigger digest corruption and rollback;
- direct durable clock tamper detection; and
- process death after clock UPDATE but before COMMIT.

Exact compiler, sanitizer, static-analysis, stress, full-registry, lineage,
patch-replay, projection, manifest, and verifier results are recorded in
`RELEASE_GATE.json` and `REVISION_EVIDENCE/rev0872/`.

## Online research incorporated

The design audit uses primary material from:

- Linux `clock_gettime(3)` clock semantics;
- Gray and Cheriton's lease analysis and bounded-drift requirement;
- SQLite transaction behavior;
- Amazon SQS visibility timeout and redelivery semantics;
- Google Cloud Pub/Sub attempt-specific acknowledgement validity;
- etcd logical revisions and durable completion; and
- the Hybrid Logical Clock paper.

The synthesis supports three distinctions:

1. logical publication order is not physical time;
2. monotonic-within-boot is not automatically persistable across reboot; and
3. an attempt receipt, a liveness interval, and terminal receiver evidence are
   different authorities.

Full URLs, interpretation, speculation, and nonclaims are in
`DURABLE_TIME_FENCE_AUDIT_rev0872.md`.

## Deliberate nonclaims

The high-water row prevents rollback of accepted local observations. It does not
make caller-supplied time trustworthy. A far-future value can still ratchet the
owner and cause denial of service. There is no maximum forward-step policy,
uncertainty model, trusted clock source, boot binding, automatic scheduler, or
operator recovery protocol.

A raw Linux monotonic or boottime value should not be persisted as a stable
cross-reboot epoch without boot identity and explicit recovery semantics.

The sender owner still lacks an authenticated receiver request/receipt,
receiver-side idempotent effect owner, payload/chunk materialization, and atomic
filesystem-visible publication. Duplicate sends remain possible around expiry,
crash, and ambiguous network response. No exactly-once claim is made.

The owner remains O(history) and O(outbox). It restores and reprojects all
retained evidence and performs another full staged restore for each changing
publication. This remains a correctness oracle, not a production performance
claim.

Clock, cutpoint, outbox, and claim digests are unkeyed. They do not authenticate
an attacker who can rewrite and rehash the store. Actor/membership signatures or
MACs, key rotation, revocation, recovery, forward secrecy, rollback-resistant
storage, and post-compromise behavior remain missing.

No claim is made for causal stability, compaction, tombstone collection,
old-replica rejoin, Sybil resistance, complete physical resource accounting,
privacy, anonymity, unlinkability, metadata hiding, secure erasure, hardware
power-loss durability, full-project sanitizers, ThreadSanitizer, Windows runtime
behavior, or formal proof.

## Highest-leverage next steps

1. Replace naked caller epoch values with a trusted local time owner that binds
   wall time, boot/session identity, monotonic observation, uncertainty, and a
   maximum forward-step policy.
2. Add explicit clock anomaly quarantine and an operator- or epoch-authorized
   recovery protocol; never silently reset the fence.
3. Build the owned wake/heartbeat scheduler on the exact receipt and clock
   boundaries.
4. Define a canonical authenticated sender request and receiver terminal record.
5. Implement receiver-side idempotent operation retention and crash-consistent
   filesystem effect publication.
6. Add a two-process sender/receiver crash matrix.
7. Introduce an indexed point-read outbox path and incremental projector while
   retaining full restoration as a differential oracle and repair authority.
8. Add authenticated actor/membership epochs and an explicit privacy threat
   model before making security or anonymity claims.

## Bottom line

Rev0872 turns an ephemeral expiry decision into durable local liveness history.
Once the owner has accepted time `t`, a smaller later value cannot revive a
receipt, even after restart. The new clock remains explicitly subordinate to
canonical evidence and explicitly untrusted as physical time.

The audit also closes an unreachable persisted lease state and reduces v2/v3
cutpoint encoder duplication. The next architectural priority is a trusted time
owner, followed by an authenticated receiver effect owner—not more sender-side
queue decoration.
