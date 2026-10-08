# Revision notes: AnonSync rev0870

## Mission increment

Rev0870 closes a sender-authority gap in the SQLite replica cutpoint introduced
in rev0869. The durable outbox previously named only a destination and an
operation. That was enough to express an unsettled intent, but not enough to
identify *which dispatch attempt* had the authority to retire it once retries,
lease expiry, process crashes, or competing workers were admitted.

The correction is receipt-bound settlement. Every claim now mints a fresh,
durable attempt receipt. Expiry permits a replacement worker to claim the same
immutable intent, but an old receipt can neither settle that replacement nor
install retry state over it. Time controls liveness and duplicate-send exposure;
it does not create settlement authority.

This is part of the central AnonSync invariant:

> Exact durable evidence is fact. Projection, counters, leases, retries, and
> acknowledgements are derived authority or ownership records. No crash,
> timeout, stale response, optimization, or caller-local memory may silently
> promote one of those records beyond the exact cutpoint that authorized it.

## Principal C++ changes

1. Added `src/sync_replica_outbox_lease.hpp/.cpp`, a pure C++20 state machine for
   durable dispatch-attempt authority.
2. Added `SyncReplicaOutboxLeaseState` with exact persisted fields for attempt
   count, claim ID, worker ID, claim time, lease deadline, and retry-not-before
   time.
3. Added fail-closed state validation. Active claim fields are all-or-none;
   active leases require a positive attempt count, valid identities, a strictly
   positive duration, and no simultaneous backoff. A never-dispatched intent
   cannot carry retry history.
4. Added exact claimability boundaries. An unclaimed intent is eligible only
   when backoff has elapsed. An active intent is eligible for replacement only
   at or after its lease deadline.
5. Added bounded timing arithmetic: `now_epoch` must be positive, lease duration
   is restricted to 1..86400 seconds, and deadline overflow is rejected before
   token minting.
6. Added a domain-separated claim digest that binds folder, destination,
   operation, enqueue generation, current SQLite cutpoint, prior attempt state,
   worker, new attempt number, exact claim/deadline times, and exactly 32 bytes
   of injected entropy.
7. Kept randomness outside the pure policy. `SyncReplicaSqliteOwner` obtains
   checked 256-bit entropy with OpenSSL `RAND_bytes`; deterministic tests inject
   fixed entropy.
8. Added exact release semantics. Release requires the current claim ID, clears
   active ownership, preserves the attempt count, and persists caller-supplied
   absolute retry backoff.
9. Replaced the rev0869 unversioned outbox ACK/delivery API with:
   `claim_next_outbox_or_throw`, `settle_outbox_or_throw`, and
   `release_outbox_for_retry_or_throw`.
10. Added typed receipt results: `Applied`, `IntentMissing`, and `StaleClaim`.
    Missing or stale receipts are durable no-ops; malformed identities are
    rejected.
11. Extended every outbox digest and the schema-v2 cutpoint digest to bind all
    dispatch-attempt and backoff fields.
12. Added exact full-row compare-and-update/delete SQL. A lease mutation or
    settlement must match the complete prior intent, not merely its primary
    key.
13. Retained complete pre-commit re-attestation. Claim, settle, and release
    update metadata, reload the whole staged cutpoint through the independent
    restore path, and commit only when the observed state exactly matches the
    intended state.
14. Added a strict schema-v2 outbox contract while retaining the complete
    rev0869 schema as the sole accepted schema-v1 migration source.
15. Added an atomic v1-to-v2 migration. The owner first performs a full exact
    v1 restore, then replaces only metadata/outbox protocol surfaces, copies
    canonical evidence and lightweight intents, re-attests the complete v2
    cutpoint, and commits. Malformed legacy state rolls back without partial
    migration.

## Why the old acknowledgement was unsafe

The old API retired an intent by `(destination_device_id, operation_id)`. Once a
retry system exists, that pair identifies the logical work but not the current
attempt. Consider:

1. worker A obtains an intent and sends it;
2. A loses connectivity long enough for its lease to expire;
3. worker B reclaims the intent and begins a new attempt;
4. A's delayed success response arrives.

Without a per-attempt receipt, A's stale response is indistinguishable from B's
current response and can delete B's unsettled intent. The defect is not that a
retry can duplicate a send—at-least-once systems must tolerate that boundary.
The defect is that old scheduling state could exercise current settlement
authority.

Rev0870 makes the distinction explicit. B receives a fresh claim ID. A's claim
ID remains well-formed but is no longer current, so settlement and release
return `StaleClaim` without changing the generation or durable outbox.

## Schema and migration discipline

Schema v2 stores six new exact lease/backoff columns on every lightweight
outbox intent. Unsigned values remain eight-byte big-endian BLOBs, so the full
`uint64_t` domain is represented without SQLite signed-integer truncation or
affinity reinterpretation. The exact `main.sqlite_schema` SQL remains protocol
evidence, including the outbox lookup and schedule indexes.

Migration is not a repair routine. The constructor accepts only:

- an empty database, which is initialized directly as v2;
- the exact v2 schema, which is fully restored and attested; or
- the exact rev0869 v1 schema, which is fully restored before migration.

A malformed v1 row, digest, projection, policy, parent graph, local counter map,
or outbox intent prevents migration. The transaction rollback leaves the v1
schema and data unchanged. A successful migration increments state generation
because the durable protocol surface changes, while preserving evidence,
projection, local mint authority, policy generation, and every unsettled
logical intent.

## Audit and refactor findings

The implementation audit corrected more than the stale-ACK surface:

- **Unreachable persisted leases:** the first validator accepted an active lease
  whose deadline equaled its claim time, although the API can mint only positive
  durations. Restore now rejects `lease_expires_at_epoch <= claimed_at_epoch`.
- **SQL primary-key comparison was insufficient:** a trigger or competing writer
  could leave the same logical key while changing attempt authority. Updates and
  deletes now compare every previous outbox field and require exactly one row.
- **Randomness was initially at risk of becoming hidden policy:** entropy is
  injected into the pure transition instead. This keeps boundary behavior
  deterministic and makes CSPRNG ownership auditable in one place.
- **Legacy migration could have become state laundering:** migration begins only
  after the exact v1 schema and complete v1 cutpoint pass the same canonical
  restore discipline used for normal operation.
- **Old APIs invited accidental bypass:** unclaimed delivery and unversioned ACK
  methods were removed rather than retained as convenience wrappers.
- **Release package drift:** the package verifier now requires the pure lease
  policy, runtime test, structural audit, and this design record from rev0870,
  while continuing to accept an exact sealed rev0869 parent.

The pure state-machine split is also a maintainability refactor. Timing,
claimability, token construction, stale-release fencing, and overflow behavior
can now be tested without SQLite setup or process timing. The SQLite owner is
left responsible for transaction authority, CSPRNG acquisition, exact durable
rows, canonical operation lookup, and commit attestation.

## Tests and structural audits

Added `tests/sync_replica_outbox_lease_test.cpp` with 19 checks covering fresh
claim, exact expiry, reclaim, stale release, durable backoff, deterministic
fixed-entropy construction, entropy separation, partial state, unreachable
zero-duration state, active-plus-backoff state, retry history without a prior
attempt, attempt-counter exhaustion, short entropy, invalid worker identity,
deadline overflow, and zero clock.

Expanded `tests/sync_replica_sqlite_owner_test.cpp` to 91 checks. New coverage
includes:

- exact schema-v1 fixture creation and successful schema-v2 migration;
- preservation of canonical evidence, local mint authority, policy, and outbox;
- malformed-v1 rejection with no partial v2 publication;
- claim persistence across restart;
- exact stale-receipt fencing after expiry and replacement;
- current-receipt settlement after restart;
- release and retry-not-before behavior;
- competing workers with exactly one current claim;
- persistent lease-field tamper rejection;
- a valid-looking TEMP-trigger mutation detected before commit; and
- real process death after lease update but before metadata publication/commit,
  restoring the old cutpoint.

Added `tools/audit_sync_replica_outbox_lease.py` with 18 fail-closed structural
checks. Expanded the SQLite owner audit to 36 checks. Both are registered in
CTest; the package verifier requires the new authority slice.

## Validation

The final C++ source was validated with:

- GCC 14.2 Debug, `-Werror`, all targets built successfully;
- all 174 registered tests covered with no failures, split only because the
  cloud command window ended during the first invocation;
- all 53 registered source audits;
- 2,198 focused runtime checks across seven replica executables under GCC;
- the same seven executables under Clang 17 Release with `-Werror`;
- the same seven executables under GCC ASan/UBSan, including bundled SQLite,
  leak detection, and halt-on-error;
- 20/20 repeated final-source SQLite-owner stress iterations, totaling 1,820
  owner assertions;
- Clang default interprocedural analysis of the pure lease policy and two core
  replica model translation units, with zero diagnostics;
- bounded shallow Clang analysis of the SQLite owner, with zero diagnostics;
  the enlarged owner-test analyzer exceeded the command window and is not
  claimed as a completed pass;
- exact rev0869 ZIP and directory verification; and
- final active projection, manifest, directory, ZIP, and source-replay checks
  recorded under `REVISION_EVIDENCE/rev0870/`.

## Deliberate nonclaims and remaining work

The owner remains an O(history) reference authority. Every public operation
reloads canonical evidence and rederives projection; mutations rewrite complete
head/visible tables. The schedule index is maintained but is not yet used to
avoid the full scan, so it must not be described as a current performance win.
The next performance revision should introduce a point-read candidate path and
an incremental affected-subgraph projector, then differential-check both
against this global oracle.

Receipt-bound settlement is local sender authority, not a complete transport
protocol. There is no authenticated receiver ACK, two-process sender/receiver
integration, retry wake scheduler, heartbeat/lease extension API, dead-letter
policy, payload/chunk transfer, or receiver-side idempotency ledger. A crash or
network partition can still produce duplicate sends; receiver processing must
be idempotent until a stronger end-to-end protocol is implemented.

Caller-provided epoch time is trusted for liveness. Clock rollback can delay a
retry, and a far-future backoff can suppress work, although neither condition
can authorize a stale receipt. A production scheduler needs a documented clock
source, rollback policy, bounded backoff calculation, and wake ownership.

The cutpoint and claim digests are unkeyed. They detect torn or casual mutation
but do not authenticate a local database attacker that can rewrite state and
recompute hashes. Actor signatures or MACs, membership/key epochs, transport
identity, rotation, revocation, recovery, forward secrecy, rollback-resistant
local storage, and post-compromise behavior remain missing.

No claim is made for production-scale persistence, physical SQLite/WAL/disk/RSS
bounds, causal stability, history compaction, tombstone collection, old-replica
rejoin, Sybil-resistant fairness, anonymous transport, metadata hiding, secure
erasure, Windows runtime behavior, full-project sanitizer coverage, or formal
proof.

## Highest-leverage next steps

1. Carry the claim ID through an authenticated sender/receiver wire exchange and
   bind the receiver's terminal result to destination, operation, payload
   commitment, and exact attempt.
2. Add a receiver-side idempotency owner so duplicate attempts cannot duplicate
   filesystem-visible effects.
3. Add bounded lease extension, retry/backoff policy, wake scheduling, poison
   handling, and explicit clock rollback behavior.
4. Introduce point-read outbox selection and incremental projection, retaining
   the current full restore as a differential oracle and periodic audit.
5. Bind payload chunks and atomic file publication to the canonical operation
   before calling the path end-to-end synchronization.
6. Define authenticated actor/membership epochs and a privacy threat model
   before making security claims implied by the project name.
