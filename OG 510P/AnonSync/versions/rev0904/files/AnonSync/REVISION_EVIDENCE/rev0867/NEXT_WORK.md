# Next work after rev0867

## 1. Production evidence/projection/outbox cutpoint

Move the reference invariant into one SQLite owner. A local transaction should
reserve the actor counter, insert exact operation bytes, insert exact parent
edges, update the deterministic projection/head cut, and append outbox intent
before commit. Restore must rebuild or attest all derived state and reject
TEMP-schema shadowing, stale outbox rows, partial migrations, and recycled file
identities. Busy/wait authority must be explicit, bounded, and owned by the same
lifetime as the connection.

## 2. Capacity is not validity

Introduce an admission result that separates malformed evidence from valid
evidence rejected only by local retention policy. Propagate bounded backpressure
through transport and anti-entropy. Never convert local exhaustion into a global
quarantine fact. Add exact per-peer/per-actor reservations and tests for
starvation, duplicate storms, and recovery after capacity becomes available.

## 3. Authentication and identity economics

Bind operation IDs to signatures over the canonical envelope. Define folder
membership, actor key enrollment, epoch rotation, revocation, device loss,
compromise recovery, durable anti-rollback state, and replay rules. Apply quotas
after authentication; cap unauthenticated identity discovery separately. A
single global evidence budget does not defeat Sybil amplification.

## 4. Incremental bounded convergence

Replace full-map reprojection with dependency-indexed incremental updates whose
work is charged to an explicit budget. Replace complete-evidence exchange with
summaries, deltas, compact fork proofs, and checkpoint certificates while
retaining a slow full-evidence differential oracle in tests.

## 5. Stability, compaction, and payload accounting

Specify when evidence can be discarded without erasing fork knowledge or
reviving deleted state. Bind compaction certificates to exact authorization.
Meter actual database pages, WAL growth, indexes, allocator/RSS pressure,
payload chunks, decompression, and network bytes separately from canonical
envelope size.

## 6. Release harness isolation

Investigate the CTest wrapper stall observed when the integration-scale serial
owner is launched immediately after the 167-test parallel lane. Preserve the
current split evidence until a reproducible harness cause is removed. Add a
watchdog that records process trees and open descriptors without weakening the
actual integration test.
