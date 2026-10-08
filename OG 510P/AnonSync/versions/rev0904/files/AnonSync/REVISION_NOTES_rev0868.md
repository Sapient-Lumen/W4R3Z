# Revision notes: AnonSync rev0868

## Mission increment

Rev0868 makes **local capacity a protocol state rather than evidence
invalidity**. Rev0867 introduced exact cumulative retained-evidence budgets but
remote exhaustion still surfaced as a throwing failure. That boundary could
invite a transport to discard a valid operation, classify a peer as malicious,
or quarantine evidence merely because one receiver was temporarily full.

This revision adds an explicit retryable `CapacityBlocked` result after full
canonical and folder validation, with no evidence, projection, authority,
counter, or durable-state mutation. It then refactors the simulator so duplicate
and capacity decisions happen before copying a complete destination graph.
Blocked messages remain queued; exact duplicates retire without graph cloning,
rehashing, reprojection, durable rewrite, or allocation.

The implementation remains an in-memory reference oracle. It does not claim
that a production SQLite or remote transport path yet preserves this result
across crash.

## Principal C++ changes

1. Added `SyncReplicaAdmission::CapacityBlocked` and a separate
   `SyncReplicaRemoteReadiness` preflight algebra.
2. Added exact read-only resource vectors for operation count, canonical bytes,
   context entries, and predecessor IDs. Every vector exposes overflow-safe
   subtraction-before-addition `would_exceed()` logic.
3. Added `preflight_remote_admission_or_throw`, which detects exact retained
   duplicates first, otherwise performs full canonical identity/semantic
   validation, folder binding, collision handling, exact measurement, and local
   budget classification without mutation.
4. Kept malformed and cross-folder envelopes throwing even at full capacity.
   A full receiver therefore does not bypass validity checks for new evidence.
5. Added a private admissible-preflight consumer that rechecks owner counters,
   limits, operation count, readiness, and operation-ID absence before atomic
   insertion/projection publication.
6. Let the network simulator preflight the immutable live owner before cloning.
   Exact duplicates now retire from the queue without cloning the destination
   graph or rewriting durable state. Capacity-blocked messages remain queued
   without cloning.
7. Avoided a second canonical encode/hash validation after the simulator copies
   an admissible destination model.
8. Replaced partition lookup through temporary owned string pairs with an owning
   key, non-owning `string_view` lookup key, and transparent logarithmic
   comparator. Delivery, drain, query, and heal no longer allocate temporary
   direction strings.
9. Changed drain scheduling to remember capacity-blocked message IDs for one
   pass, skip them, and continue attempting later work in oldest-first or
   newest-first order. A blocked head can no longer spin or starve a later
   duplicate/admissible message.

## Tests and audits

Added `tests/sync_replica_capacity_backpressure_test.cpp` with 19 checks for:

- exact duplicate preflight and zero incoming charge at full capacity;
- exact capacity vectors for a valid new envelope;
- complete state and durable-state immutability on pressure;
- no accidental quarantine of blocked evidence;
- malformed and cross-folder rejection while full;
- successful admission of the same valid envelope under a larger local policy;
- allocation-free duplicate delivery with the next global allocation forced to
  fail;
- no durable rewrite on duplicate retirement;
- queue ownership and exact semantic-byte preservation on capacity block;
- progress past blocked messages during oldest-first drain; and
- termination without spin during newest-first drain.

Updated the aggregate budget test to require explicit `CapacityBlocked` for
remote pressure and to inspect exact preflight canonical-byte charge. Local mint
and over-budget durable restore remain fail-closed throwing paths.

Added `tools/audit_sync_replica_capacity_backpressure.py`, registered
hermetically in CTest, with 19 structural checks over the result algebra,
validation order, duplicate zero charge, no-mutation returns, stale owner-plan
checks, atomic rollback, preflight-before-copy, no second public admission,
transparent partition lookup, drain progress, runtime coverage, sanitizer
scope, CMake registration, and revision-scoped package requirements.

The aggregate-budget source audit now reports 22 checks and explicitly guards
the validity/capacity separation and owner-plan publication boundary.

`tools/verify_release_package.py` requires the new runtime and source audit in
rev0868+ packages without invalidating rev0867.

## Validation

The final source passes:

- all 170 registered GCC tests:
  169/169 in the parallel registry lane plus the
  serial integration-scale domain owner in isolation;
- 2,088 focused runtime checks under GCC: 67 network/model, 1,288
  codec/hash-graph/projection, 688 allocation-atomicity, 26 aggregate-budget,
  and 19 capacity/backpressure checks;
- the same five focused executables under Clang 17 with `-Werror`;
- the same five focused executables under GCC ASan/UBSan with leak detection and
  halt-on-error; and
- Clang static analysis of four changed production/test translation units with
  zero diagnostics.

The full GCC all-target build completes, followed by a no-work Ninja rebuild.
Exact commands, logs, projection, lineage, and release evidence are under
`REVISION_EVIDENCE/rev0868/`.

## Corrected severe or wasteful behavior

- Valid remote evidence blocked by one receiver's local budget is no longer
  represented as invalid input or quarantine.
- A blocked transport message remains owned for retry; the simulator does not
  silently discard it.
- Exact duplicate delivery no longer clones the destination evidence graph or
  rewrites its durable snapshot.
- Capacity classification no longer clones the destination evidence graph.
- Admissible simulator delivery validates and hashes the envelope once rather
  than once before and once after cloning.
- Negative partition checks no longer construct temporary owned strings.
- A capacity-blocked oldest/newest message can no longer monopolize a drain loop
  or consume the pass without later attempts.
- The allocation failpoint now proves the whole duplicate delivery path, not
  merely model-level duplicate admission, is allocation-free.

## What remains missing

`CapacityBlocked` is not yet durable or interoperable. The highest-priority next
work is a production SQLite-backed vertical slice that atomically owns exact
authenticated operation bytes, parent edges, resource charge, deterministic
projection/head changes, local counter authority, and sender outbox intent. It
must restore and carry validity, trust, applicability, and retention verdicts
through a real two-process retry path.

Other major gaps are authenticated actor and membership epochs; key rotation,
revocation, and recovery; per-principal fairness and bounded unknown-identity
work; durable retry/backoff and wake conditions; causal stability, checkpoint
certificates, compaction, and tombstone collection; actual RSS/disk/WAL/payload
accounting; incremental projection; compact exact-ID anti-entropy; payload
materialization bound to operation identity; and a privacy/anonymity threat
model.

A receiver pressure response can itself leak load or activity. No rich resource
vector should cross a real wire until authentication, rate limiting, coarsening,
and privacy implications are designed.

## Research update

The audit compares the new boundary with explicit blocked/overload states in
QUIC and HTTP, then reviews recent CRDT anti-entropy and memory-exhaustion work.
A 16 July 2026 Blocklace-related preprint reinforces the risk of fresh identities
and eager adversarial evidence; delta synchronization and digest-driven set
reconciliation reinforce that whole-set anti-entropy is a test oracle rather
than a viable final protocol.

These are design analogies and speculative leads, not implementation authority.
See `CAPACITY_BACKPRESSURE_AUDIT_rev0868.md` and
`REVISION_EVIDENCE/rev0868/RESEARCH.md` for primary-source URLs, cautions, and
the staged architecture.
