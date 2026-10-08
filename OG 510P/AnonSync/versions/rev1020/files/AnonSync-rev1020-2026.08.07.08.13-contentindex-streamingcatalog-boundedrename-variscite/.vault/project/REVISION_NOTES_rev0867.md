# Revision notes: AnonSync rev0867

## Mission increment

Rev0867 makes the exact-evidence convergence oracle materially harder to exhaust
and cheaper to replay. Rev0866 bounded individual operation envelopes but still
permitted the product of the operation-count and per-envelope maxima. At the
defaults, that was 39.0625 GiB of canonical operation material before C++
container, allocator, projection, database, or payload overhead.

This revision introduces exact cumulative budgets across every retained
evidence state and publishes their counters atomically with deterministic graph
projection. It also removes two hidden repeated-allocation paths and repairs a
brittle audit that confused an accidental test count with the property being
defended.

The implementation remains a bounded in-memory reference model. It does not
claim that the production SQLite, transport, recovery, or filesystem path yet
uses these semantics.

## Principal C++ changes

1. Added independent aggregate limits to `SyncReplicaModelLimits` for canonical
   envelope bytes, causal-context entries, and predecessor IDs. Defaults are
   256 MiB, 1,000,000 entries, and 1,000,000 IDs.
2. Added `sync_replica_operation_canonical_size_or_throw`, which applies the
   canonical semantic and per-envelope checks and returns the exact versioned
   envelope size without materializing the encoded string.
3. Added one validate-and-measure internal path so remote admission and restore
   obtain exact byte charge from the same full identity validation that checks
   the SHA-256 operation ID.
4. Added exact live counters to `SyncReplicaModel` and overflow-safe prospective
   total calculation using subtraction-before-addition.
5. Charged active, pending, and every quarantined envelope alike. Duplicate
   replay does not consume retained budget.
6. Preflighted all three aggregate totals before local insertion, remote
   insertion, or restore publication. Counters commit only in the same no-throw
   section as active IDs, evidence states, causal heads, and local authority.
7. Changed restore to consume durable state by value. Rvalue callers transfer
   operation vectors and local operation IDs instead of cloning the full graph.
8. Added an exact duplicate fast path before canonical encoding and hashing.
   Byte-identical retry is already authorized by the immutable retained owner;
   a same-ID but different value still takes full validation and collision
   handling.
9. Replaced per-entry copies of the previous causal actor with a non-owning
   pointer during sorted-context validation, removing repeated `device_id`
   string allocations from encode/decode/measure/admit/restore traversals.

## Tests and audits

Added `tests/sync_replica_aggregate_budget_test.cpp` with 25 checks for:

- exact canonical size versus actual encoding;
- invalid aggregate/per-envelope limit contracts;
- exact mixed active, pending, and quarantined charging;
- duplicate idempotence;
- canonical-byte, context-entry, and predecessor-ID ceilings;
- atomic rejection with unchanged durable semantics;
- move-based restore and restore-time budget rejection; and
- local mint rollback at an exact aggregate boundary.

Extended `tests/sync_replica_allocation_atomicity_test.cpp` so every injected
`std::bad_alloc` cutpoint verifies all retained counters. It now reports 688
checks over 180 local and 158 remote throwing cutpoints. It additionally proves
that exact duplicate admission makes zero global allocations and changes no
durable state.

Added `tools/audit_sync_replica_aggregate_budget.py`, registered hermetically in
CTest, with 20 source-boundary checks covering limits, exact measurement,
move-based restore, overflow safety, admission ordering, rollback, tests,
sanitizer participation, CMake registration, and revision-scoped package
requirements.

Refactored `tools/audit_sync_sqlite_sidecar_snapshot.py` to require the historic
minimum and hermetic coverage of every Python CTest command rather than an exact
magic count. This prevents unrelated legitimate audit additions from breaking a
false structural invariant.

`tools/verify_release_package.py` now requires the aggregate-budget runtime and
source audit from rev0867 onward without invalidating sealed parents.

## Validation

The final source passes:

- all 168 registered GCC tests: 167/167 in the parallel registry lane plus the
  serial integration-scale domain selftest in isolation (611/611 internal
  assertions);
- 2,068 focused runtime checks under GCC;
- the same four focused executables under Clang 17 with `-Werror`;
- the same four focused executables under GCC ASan/UBSan with leak detection and
  halt-on-error; and
- Clang static analysis of four changed production/test translation units with
  zero diagnostics.

The full GCC all-target build completes, followed by a no-work Ninja rebuild.
The aggregate source audit passes 20/20 and the updated SQLite sidecar audit
passes 105/105.

Exact commands, logs, projection, lineage, and release evidence are under
`REVISION_EVIDENCE/rev0867/`.

## Corrected severe or wasteful behavior

- The effective retained canonical-byte authorization fell from a theoretical
  39.0625 GiB product at defaults to one explicit 256 MiB cumulative ceiling.
- Pending and quarantined envelopes can no longer evade aggregate accounting.
- Aggregate counters cannot partially publish when allocation or projection
  fails.
- Durable restore cannot reconstruct a model that exceeds current cumulative
  policy.
- Exact duplicate anti-entropy replay no longer re-encodes and rehashes an
  already-owned envelope.
- Canonical context validation no longer clones actor strings merely to compare
  adjacent entries.
- Restore can move complete durable graphs rather than always copying them.
- A source audit now defends hermetic Python registration rather than a stale
  exact count.

## What remains missing

The new budgets are a fail-closed safety boundary, not a retention lifecycle.
The highest-priority missing work is still a production vertical slice that
atomically commits local counter reservation, exact authenticated operation
bytes, parent edges, deterministic projection/head changes, and outbox intent
in SQLite, then restores and transports that state through a real two-process
path.

Other major gaps are authenticated actor and membership epochs; key rotation,
revocation, and recovery; valid-but-capacity-blocked protocol state; per-peer or
per-principal fairness; bounded identity admission; causal stability,
checkpoint certificates, compaction, and tombstone collection; actual
RSS/disk/WAL/payload accounting; incremental projection; compact exact-node
anti-entropy; payload materialization bound to operation identity; and a
privacy/anonymity threat model.

A local capacity rejection must not be mistaken for global semantic invalidity.
Peers with different limits or pressure may retain different evidence sets, so
product convergence cannot be claimed until transport, persistence, and
backpressure make that distinction explicit.

## Research update

The detailed audit incorporates CRDT surveys, delta-state anti-entropy,
Byzantine hash-graph work, Blocklace, and a new 16 July 2026 preprint describing
memory exhaustion through fresh identities and eagerly retained Byzantine
evidence. The latter strongly reinforces the need for authenticated identity
scope, fairness, and interest-driven admission beyond a global byte ceiling,
but is treated as a recent research warning rather than implementation
authority.

See `RETAINED_EVIDENCE_BUDGET_AUDIT_rev0867.md` and
`REVISION_EVIDENCE/rev0867/RESEARCH.md` for URLs, cautions, and the staged next
architecture.
