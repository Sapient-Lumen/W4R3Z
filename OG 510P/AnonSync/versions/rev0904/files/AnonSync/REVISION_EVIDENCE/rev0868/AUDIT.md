# AnonSync rev0868 audit summary

## Finding

Rev0868 repairs the semantic and work-amplification boundary created when
rev0867 made retained-evidence budgets exact. A valid remote envelope that is
blocked only by one receiver's local capacity now returns explicit retryable
`CapacityBlocked` state. It is neither invalid nor quarantined, and it cannot
mutate retained evidence, projection, local authority, aggregate counters, or
durable state.

The network simulator resolves exact duplicate and capacity state against the
immutable live owner before copying the complete destination graph. Duplicate
retirement performs no canonical rehash, model clone, projection, durable
rewrite, or allocation. A blocked message remains queued without model clone.
Admissible delivery consumes the already validated plan in an exact model copy,
avoiding a second canonical validation/hash pass.

A fault probe exposed temporary owned strings in partition lookup. The
partition index now supports transparent logarithmic lookup through non-owning
`string_view` direction keys. Drain scheduling tracks capacity-blocked messages
for one pass so they cannot spin or starve later work.

## Invariants defended

- Exact duplicates report zero incoming charge in all four resource dimensions.
- New remote evidence is canonically validated and folder-bound before local
  capacity classification.
- Malformed and cross-folder envelopes still fail while the model is full.
- `CapacityBlocked` publishes no evidence, quarantine, projection, authority,
  counters, or durable snapshot.
- Preflight resource arithmetic is subtraction-based and overflow safe.
- The private insertion path rejects a preflight inconsistent with the copied
  owner's count, counters, limits, readiness, or existing operation IDs.
- Duplicate and capacity decisions precede graph cloning.
- Duplicate queue retirement and partition lookup are allocation-free in the
  failpoint witness.
- A drain pass attempts later messages after one message is locally blocked and
  terminates when all remaining transport-deliverable messages have been tried.

## Validation result

- GCC Debug all-target build: passed.
- CTest registry: 170/170 across 169 parallel tests and one isolated declared
  serial owner.
- Registered audits: 51/51.
- Focused GCC runtime: 2,088/2,088 checks across five executables.
- Aggregate-budget source audit: 22/22.
- Capacity/backpressure source audit: 19/19.
- Clang 17 Release `-Werror`, Clang static analyzer, and GCC ASan/UBSan evidence
  are recorded in `validation/`.

## Scope and nonclaims

The implementation is a bounded in-memory reference model and deterministic
fault harness. It is not a production SQLite operation owner, transport,
authenticated peer protocol, durable retry scheduler, fairness mechanism,
retention lifecycle, physical memory/disk bound, or privacy protocol.

The private preflight consumer is a trusted internal optimization boundary for
one immutable single-threaded owner and its byte-for-byte copy. It is not a
serializable admission token. A production ticket would need exact operation,
policy epoch, storage generation, and expiry binding, or should never leave one
transaction owner.

See `CAPACITY_BACKPRESSURE_AUDIT_rev0868.md` for the full mission analysis,
state-transition table, complexity correction, research review, and staged next
architecture.
