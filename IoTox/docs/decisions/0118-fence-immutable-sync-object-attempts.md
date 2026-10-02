# ADR 0118: fence immutable synchronization object attempts

Status: accepted

Date: 2026-08-21

## Decision

Multi-route synchronization schedules a canonical immutable object record—kind, digest, and exact
byte count—rather than a toxcore file number, friend number, pathname, or terminal frame. An object
has at most one current attempt. Every assignment receives a unique nonzero attempt identifier that
remains retained as a bounded tombstone after failure or commit.

Assignment is permitted only to the exact worker incarnation of a `ready` bulk route. It reserves
one unit through the route coordinator's existing admission boundary. The protected route is never
eligible. Reassignment requires the old attempt to become fenced and its reservation to be released
first. A completion for a fenced attempt is stale and cannot verify or commit the replacement.

Completion verifies the caller-observed digest and byte count against the frozen record. A mismatch
fences the attempt and returns the object to pending. Exact verification is distinct from commit;
commit succeeds only for the object's current verified attempt, releases capacity exactly once, and
is idempotent thereafter.

Route authentication loss may atomically zero coordinator work before scheduler cleanup runs. The
scheduler recognizes capacity as already withdrawn only when the exact route/worker incarnation is
no longer ready and reports zero admitted work. A ready route with inconsistent accounting remains a
hard failure. Explicit scheduler close fences all active and verified attempts, releases their live
reservations, and permanently closes admission.

## Consequences

Late toxcore callbacks cannot acquire a new meaning after reassignment, bulk work cannot consume the
Ratox reservation, and normal scheduler teardown cannot strand coordinator capacity. State is
bounded and fails closed when object or attempt-tombstone limits are exhausted.

This is a transport-neutral, process-local state machine. Its completion call does not hash a file,
its state is not yet reconstructed after process restart, and it does not publish or activate a
signed HEAD. Gate 3 remains open until an attempt owns a private staging target, staged bytes are
hashed independently, state is durable, and the existing namespace transaction commits each object
before accepted-HEAD and activation transitions.
