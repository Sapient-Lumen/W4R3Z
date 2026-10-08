# AnonSync rev0870 audit summary

## Finding

Rev0870 closes a reachable settlement-authority gap in the durable sender
outbox. Rev0869 could identify an intent by destination and operation, but that
identity did not distinguish one dispatch attempt from a later reclaim. Once
retries or competing workers were added, a delayed result from an older attempt
could therefore retire newer work. The correction makes every dispatch attempt
mint an exact receipt capability and requires the current capability for both
settlement and retry release.

The receipt is part of the same SQLite cutpoint as canonical operation evidence,
projection, local mint authority, destination intent, attempt count, worker,
lease interval, retry schedule, schema generation, and cutpoint digests. Lease
expiry changes claimability only. It never grants settlement authority and does
not invalidate the persisted current receipt until a replacement claim commits.

## Refactor

Retry and lease transitions were extracted into a pure C++ authority component:
`SyncReplicaOutboxLeaseState`. It validates representable states, determines
claimability, derives a new claim from injected entropy and exact prior state,
and releases an exact claim into bounded retry backoff. The component performs
no I/O, reads no clock, and mints no randomness internally. This keeps protocol
rules deterministic and directly testable while the SQLite owner retains
transaction, entropy, persistence, and global re-attestation authority.

The SQLite schema advances from exact version 1 to exact version 2. A v1 store
is migrated only after complete legacy restore and attestation. The migration is
one transaction, preserves canonical evidence and policy, publishes empty lease
state for existing intents, re-attests the staged v2 database, and then commits.
Malformed legacy state is rejected before any v2 publication.

## Severe defects and waste corrected

1. **Stale settlement authority.** Destination and operation identified durable
   work but not the attempt authorized to retire it. Exact receipt comparison
   now fences delayed workers after reclaim.
2. **Policy hidden in SQL.** Claim, expiry, release, backoff, overflow, and state
   reachability rules were becoming persistence-side control flow. A pure C++
   state machine now owns those rules.
3. **Unreachable persisted state.** Active leases with zero duration passed an
   early restore shape check even though the API can never mint them. Restore
   and the pure validator now reject them.
4. **Migration temptation.** A permissive `ALTER TABLE` path could have treated
   malformed v1 state as migration input. Exact v1 inventory and full legacy
   attestation are prerequisites to the transactional v2 rewrite.
5. **Ambiguous ACK language.** Documentation and APIs now distinguish a local
   dispatch-attempt receipt from an authenticated end-to-end receiver
   acknowledgement. Rev0870 implements the former only.

## Invariants defended

- a claim binds folder, destination, operation, enqueue generation, cutpoint,
  prior attempt state, worker, attempt number, lease times, and 32 injected
  entropy bytes;
- only the exact current claim can settle or release an intent;
- expiry permits replacement but never settlement;
- stale receipts are durable no-ops and cannot mutate metadata;
- retry release preserves attempt history and installs an absolute not-before;
- competing writers serialize through one `BEGIN IMMEDIATE` owner;
- each claim/settle/release mutation matches the complete prior row;
- every staged mutation is fully restored and re-attested before commit;
- process death after lease-row update and before metadata/commit restores the
  old cutpoint; and
- exact rev0869 schema-v1 state migrates transactionally, while malformed
  legacy state rolls back unchanged.

## Validation result

- GCC 14 Debug final-source all-target build completed; final rebuild reported
  no work.
- All 174 registered tests were covered with no failures across the main run
  through test 146 and an isolated 147–174 tail run. No single uninterrupted
  174-test invocation is claimed.
- Registered source/structure audits: 53/53.
- Focused GCC, Clang 17 Release `-Werror`, and GCC 14 ASan/UBSan lanes: 7/7
  executables and 2,198/2,198 checks in each lane.
- Bundled SQLite is included in the sanitizer lane.
- Owner stress: 20/20 iterations and 1,820/1,820 repeated checks.
- Lease audit: 18/18. SQLite owner audit: 36/36.
- Clang analyzer: three production translation units under default
  interprocedural analysis and the SQLite owner under bounded shallow analysis,
  with zero diagnostics. Completion of the owner-test analyzer command is not
  observed and is not claimed.
- The active-source patch replays exactly from rev0869 across all 337 final
  active files; ten active files changed, four were added, and none removed.

## Scope and nonclaims

This remains a correctness oracle, not a production transport. The owner still
performs O(history) restore and projection rewrite for hot operations. Its
schedule index is maintained but not yet used to make claiming asymptotically
cheaper. Duplicate delivery remains possible after timeout or crash until a
receiver-side idempotency owner exists. Claim IDs are local unkeyed
capabilities, not authenticated remote receipts and not protection against an
attacker able to rewrite and rehash the database. Caller-supplied wall time can
harm liveness under rollback or jump. There is no lease heartbeat, remote peer
authentication, operation signature lifecycle, payload transfer, causal
stability, compaction, physical-resource model, or anonymity protocol.

See `RECEIPT_BOUND_OUTBOX_AUDIT_rev0870.md` for the detailed design, research,
attack traces, and staged architecture.
