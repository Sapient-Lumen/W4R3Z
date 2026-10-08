# Revision notes: AnonSync rev0871

## Mission increment

Rev0871 completes the local lease-authority model introduced in rev0870.
Rev0870 made dispatch attempts receipt-bound, so an old attempt could not settle
a replacement. It still allowed the exact stored receipt to settle or release
at and after its own deadline until replacement occurred. That made expiry a
reclaim hint rather than revocation.

Rev0871 makes the deadline authoritative. Settlement, retry release, and lease
renewal all require the exact current receipt and `claimed_at_epoch <= now_epoch
< lease_expires_at_epoch`. At the exact deadline the receipt is expired.

A bounded heartbeat can now extend a live attempt without changing its receipt,
worker, attempt count, or original claim time. Renewal never shortens an
existing deadline and cannot extend one claim beyond the fixed cumulative
lifetime ceiling.

This advances the central AnonSync invariant:

> Exact durable evidence is fact. Projection, counters, leases, retry schedules,
> receipts, and optimizations are subordinate records. No timeout, stale
> response, crash, helper function, or storage shortcut may silently promote
> them beyond the exact cutpoint that authorized them.

## Principal C++ changes

1. Added public hard ceilings in `src/sync_replica_outbox_lease.hpp` for a single
   lease, cumulative claim lifetime, and API-minted retry delay.
2. Added `SyncReplicaOutboxClaimStatus::{Current,Stale,Expired}` and one pure
   classifier shared by settlement, renewal, and release.
3. Defined an exclusive deadline: `now_epoch >= lease_expires_at_epoch` is
   expired.
4. Added `renew_sync_replica_outbox_lease_or_throw`.
5. Heartbeat preserves claim ID, worker ID, attempt count, and original claim
   time; it never shortens an existing deadline.
6. Added a cumulative lifetime limit measured from the original claim time.
7. Extended persisted-state validation so restart rejects an active claim that
   exceeds the same lifetime ceiling.
8. Changed retry release to require explicit `now_epoch`, a retry time no earlier
   than now, and a bounded delay.
9. Added `LeaseAlreadyCovered` and `ExpiredClaim` to the SQLite owner's typed
   receipt results.
10. Changed SQLite settlement to require `now_epoch` and an exact unexpired
    receipt.
11. Added `SyncReplicaSqliteOwner::renew_outbox_lease_or_throw`.
12. Moved the 32-byte OpenSSL CSPRNG draw before `BEGIN IMMEDIATE`. The exact
    loaded cutpoint and selected intent are still bound after the write
    transaction begins.
13. Replaced repeated linear exact-intent scans in settlement, renewal, and
    release with one canonical `std::lower_bound` helper.
14. Factored claim, renewal, and release through one exact prior-row update,
    generation/digest publication, independent staged restore, and commit
    helper.

## Audit/refactor corrections

The primary correctness defect was a split lease definition: claimability used
time, while terminal receipt authority did not. SQLite serialization prevented
torn state but allowed lock order to decide whether an already-expired worker
could settle. All receipt-authorized paths now use one classifier.

The audit also corrected or rejected:

- runtime policy that could refuse an overlong renewal while restore accepted an
  overlong active claim;
- unbounded caller-supplied retry delay;
- unnecessary CSPRNG latency inside SQLite's single-writer interval;
- three duplicate linear key scans;
- duplicate lease publication and re-attestation sequences; and
- an unintegrated delivery-protocol side branch, removed before publication
  rather than shipped without codec, receiver, authentication, and end-to-end
  tests.

One deliberate micro-waste remains: entropy is acquired before the transaction,
so a draw can be discarded when no intent is ready or the later transaction
fails. This trades inexpensive entropy for less writer-lock occupancy.

The dominant remaining waste is full-history restore/reprojection on every
owner operation plus another full staged restore before each changing commit.
This remains a deliberate correctness oracle, not a production scaling claim.

## Runtime coverage

`tests/sync_replica_outbox_lease_test.cpp` now reports 31 checks. New coverage
includes:

- exact current/stale/expired boundaries;
- matching-receipt clock rollback rejection;
- heartbeat identity preservation;
- already-covered no-op renewal;
- no shortening;
- expiry rejection;
- cumulative lifetime rejection;
- restore-time rejection of an overlong active claim;
- retry-before-now rejection; and
- maximum retry-delay enforcement.

`tests/sync_replica_sqlite_owner_test.cpp` now reports 113 checks. New coverage
includes:

- heartbeat extension and restart persistence;
- generation-stable already-covered heartbeat;
- invalid renewal/retry bounds with exact state preservation;
- settlement, release, and renewal rejection at the exact deadline;
- replacement claim and stale old-receipt fencing;
- TEMP-trigger mutation during renewal with rollback;
- process death after the heartbeat row update but before commit; and
- exact retry of renewal after crash recovery.

The existing migration, malformed legacy state, competing claimer, lease
tamper, claim-trigger, and claim-crash cases remain covered.

## Structural audits and release gate

`tools/audit_sync_replica_outbox_lease.py` is revisioned to format
`anonsync-sync-replica-outbox-lease-audit-v2` and checks 21 structural
invariants.

`tools/audit_sync_replica_sqlite_owner.py` is revisioned to format
`anonsync-sync-replica-sqlite-owner-audit-v3` and checks 40 structural
invariants, including pre-lock entropy, canonical binary lookup, the shared
publication helper, heartbeat no-op semantics, exact expiry handling, trigger
and process-crash probes, and release-verifier coverage.

`tools/verify_release_package.py` now requires
`LEASE_HEARTBEAT_AUTHORITY_AUDIT_rev0871.md` for revision 871 and later without
invalidating rev0870 packages.

Exact final test counts, compiler lanes, sanitizer scope, static-analysis scope,
stress results, parent verification, source patch replay, active projection,
manifest, and package verifier results are recorded in `RELEASE_GATE.json` and
`REVISION_EVIDENCE/rev0871/`.

## Online research incorporated

The design audit uses primary documentation from:

- Amazon SQS receipt handles, deletion, and visibility-timeout extension;
- Google Cloud Pub/Sub acknowledgement validity and lease management;
- OASIS AMQP 1.0 unsettled delivery tags; and
- SQLite transaction and WAL concurrency behavior.

These are design analogies only. AnonSync does not claim compatibility or the
managed services' guarantees.

Full URLs, interpretation, and nonclaims are in
`LEASE_HEARTBEAT_AUTHORITY_AUDIT_rev0871.md`.

## Deliberate nonclaims

Rev0871 does not provide an authenticated receiver receipt, a remote transport,
a receiver-side idempotent filesystem-effect owner, or end-to-end exactly-once
delivery. Duplicate sends remain possible around timeout and crash.

The caller still supplies epoch time. A matching receipt with time before its
claim is rejected, but no trusted monotonic clock owner or persisted time
high-water mark exists. No automatic heartbeat scheduler calls the new API.

The retry delay is bounded when created through the public release API. Because
the schema does not persist release time separately, restart cannot
independently reconstruct and re-prove the original delay ceiling.

The 24-hour ceilings are implementation safety limits, not validated production
defaults. No exponential backoff, jitter ownership, attempt-age policy, poison
state, dead-letter state, batch heartbeat, or batch settlement is implemented.

The SQLite owner remains O(history) and O(outbox) to restore, even though exact
post-restore intent lookup is now logarithmic. No point-read claim owner,
incremental affected-subgraph projector, physical WAL/disk/RSS accounting, or
production performance claim is made.

Cutpoint and claim digests are unkeyed. They do not authenticate an attacker who
can rewrite the local store and recompute hashes. Actor signatures or MACs,
membership/key epochs, transport identity, rotation, revocation, recovery,
forward secrecy, rollback-resistant storage, and post-compromise behavior are
missing.

No claim is made for payload/chunk materialization, atomic filesystem-visible
effects, causal stability, history compaction, tombstone collection, old-replica
rejoin, Sybil-resistant fairness, anonymity, unlinkability, traffic-analysis
resistance, metadata hiding, secure erasure, hardware power-loss durability,
full-project sanitizer coverage, ThreadSanitizer, Windows runtime behavior, or
formal proof.

## Highest-leverage next steps

1. Define a canonical attempt-bound wire request and authenticated terminal
   receiver record. Capacity/backpressure must be nonterminal.
2. Make retained operation evidence and filesystem-visible effect publication a
   receiver-side idempotency owner with a two-process crash matrix.
3. Add a trusted clock/high-water policy and an owned heartbeat/wake scheduler.
4. Move retry calculation into bounded pure policy with attempt/age limits,
   explicit jitter entropy, poison handling, and restart-verifiable scheduling
   provenance.
5. Introduce point-read scheduling and incremental projection while retaining
   this full restore path as a differential oracle and repair authority.
6. Bind payload chunks and atomic file publication to the canonical operation.
7. Add authenticated actor/membership epochs and an explicit privacy threat
   model before making security or anonymity claims.

## Final validation record

Publication uses an isolated reconstruction from the sealed rev0870 parent,
not the earlier mutable worktree. A delayed unintegrated delivery-protocol
branch was detected during validation and excluded because it introduced an
untested authority surface and temporarily left mismatched declarations and
definitions. The retained rev0871 patch modifies exactly nine active files.

Final-source evidence records a clean GCC 14 all-target build and no-work
closure; all 174 registered tests covered with no failure across a 173-pass
main lane plus the one declared serial test in isolation; 53/53 registered
audits; 2,232 focused checks in each of GCC Debug, Clang 17 Release `-Werror`,
and GCC 14 ASan/UBSan; 20 owner-stress passes totaling 2,260 checks; 21/21 and
40/40 revision source audits; zero diagnostics in the stated Clang analyzer
scope; and byte-exact active-source patch replay from rev0870. No single
uninterrupted 174-test command is claimed.
