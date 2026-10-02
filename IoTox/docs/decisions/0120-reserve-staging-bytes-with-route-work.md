# ADR 0120: reserve staging bytes with route work

Status: accepted

Date: 2026-08-21

## Decision

Each `SyncObjectScheduler` is scoped to one synchronization namespace. Product construction must set
its `maximum_staging_bytes` from that namespace's local policy. Assigning an immutable object
atomically consumes both one coordinator work unit on the exact ready bulk worker and the object's
full byte count from the scheduler staging budget.

The complete object size is reserved even before its first byte arrives. Verification does not free
the reservation because the staged or newly committed bytes still belong to an unfinished attempt.
Fence, verification mismatch, successful commit, and scheduler close release both route and byte
reservations exactly once. Authentication loss may have withdrawn route work first, but it does not
withdraw scheduler-owned bytes; fencing still releases those bytes after confirming the exact closed
worker state.

Zero-length synchronization objects are invalid. Admission checks subtraction before addition and
fails with resource exhaustion without allocating an attempt ID or touching coordinator capacity.
Snapshots expose aggregate reserved staging bytes and whether each retained attempt still owns its
byte reservation.

## Consequences

Several bulk routes cannot each consume the namespace's complete staging allowance. A verified object
continues applying conservative pressure until its scheduler commit, and all terminal paths return
the budget. This is process-local admission accounting, not disk quota enforcement.

Restart reconstruction remains necessary so a process cannot forget completed staging files or old
attempt fences. Live file-transfer binding must also order destination preparation, route/byte
reservation, transfer admission, object commit, and terminal scheduler transition without exposing a
gap. Gate 3 remains closed to product traffic until those paths are implemented and tested.
