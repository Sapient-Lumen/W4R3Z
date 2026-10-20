# Immutable synchronization object scheduler v1

This document describes the first Gate 3 scheduling boundary. It is intentionally independent of
toxcore file numbers and file-transfer callback timing.

## Identities

An object identity is the canonical tuple:

```text
(artifact | manifest, SHA-256 digest, exact byte count)
```

An assignment identity is a fresh nonzero 64-bit attempt ID plus the exact signed-inventory route
key and current worker incarnation. Attempt IDs cannot be reused while their tombstones are retained.
Paths, friend numbers, file numbers, and transfer-vector positions are never scheduler identities.

## State and effects

```text
object:   pending --assign--> assigned --verify--> verified --commit--> committed
             ^                    |                    |
             `------ fence -------+--------------------+

attempt:  active ----verify----> verified ----commit----> committed
             |                       |
             `-------- fence --------+------------------> fenced
```

- `assign` first creates the attempt record, then reserves one capacity unit through a bounded
  transport adapter and the object's full byte count from the namespace staging budget. The normal
  adapter accepts only an exact ready coordinator bulk worker; the single-route Agent slice can use
  the same scheduler without fabricating route proofs. Reservation failure leaves no attempt or
  transport effect.
- `fence_route` withdraws every active or verified attempt for the exact route incarnation before
  those objects can be assigned elsewhere.
- `fence_attempt` withdraws only one active or verified attempt. It is used when one live file fails
  without falsely fencing unrelated objects on the same authenticated route.
- `complete` accepts only the frozen digest and byte count. A mismatch releases capacity and fences
  the attempt. A fenced completion is counted and rejected as stale.
- `commit` accepts only the object's current verified attempt. Exact retries are idempotent and do
  not release route or byte capacity twice. Verification retains both reservations.
- `close` fences live attempts, releases their capacity, and rejects future registration or
  assignment.

The coordinator may have already withdrawn work when authentication is lost. That is accepted as a
completed release only for the same worker when it is not ready and its admitted-work count is zero.
Any disagreement while the route remains ready fails closed.

## Bounds and owner-thread contract

The scheduler retains a configured maximum number of objects and attempt tombstones. Subscriber
construction takes the attempt bound from the validated host-local namespace
`maximum-outstanding-requests` quota, the same ceiling used by its durable active-attempt journal.
Exhaustion is explicit; it never evicts a fence that could still classify a late completion. The
current class is serialized by its owner and is not a concurrent queue (ADR 0237).

## Worker bridge

The filesystem prerequisite now derives one private attempt path and can commit its independently
size/digest-verified bytes to the object store under `SyncNamespaceTransaction`. The scheduler also
reserves aggregate in-flight staging bytes. `SyncTransferCoordinator` now binds an active attempt to
one exact authenticated worker/file handle only after staging preparation. A reserved terminal event
drives object commit first and scheduler completion second; every failed or corrupt outcome discards
and fences. A parent event dispatcher can route individual events without allowing one namespace to
consume another namespace's terminal truth.

The corresponding sender path accepts one application-chosen nonzero Tox FileId, verifies that the
provider returns the exact same ID, and retains its terminal outcome under the same preallocated
worker bound. `protocol-sync-wire-v1.md` uses that token to join one signed object request to one
otherwise filename-independent Tox offer. File numbers remain ephemeral handles.

## Not yet claimed

The scheduler remains process-local, and its allocator uses the signed attempt journal's durable
high-water entrance. The bridge journals active immutable object/route identities before receive;
startup recovery commits valid stranded bytes or fences incomplete work. The default-off Agent now
dispatches the fixed request/offer codec for an authorized single source, commits both objects,
accepts the signed HEAD last, and leaves activation independent.

When the global receive ledger is full, ADR 0166 keeps the exact attempt and its scheduler/staging
reservation while removing only provisional staging and durable active-transfer truth. The paused
offer is retried outside callbacks in bounded cyclic passes and can be cancelled before admission.

Authenticated auxiliary application-frame dispatch and live immutable-object reassignment now pass
the deterministic Agent boundary and genuine direct-UDP/forced-TCP two-guest fault qualification.
The accepted seam fences after positive receive progress, reissues the missing whole object on a
different ready worker, rejects old-incarnation terminals, and restores the stopped route without
changing object, HEAD, or activation identity. Fixed-versus-adaptive scheduling remains open beyond
the first topology row: ADR 0171 proves fixed carrier reuse versus adaptive idle-carrier admission on
genuine direct UDP and forced TCP, and counterbalanced policy order also passes. ADR 0176 qualifies
both exact corresponding auxiliary readiness orders without changing scheduler identities. These do
not prove throughput, fairness, random startup/fault delays, startup under fault, scheduler-phase
resources, cancellation tails, or relay diversity. Neither raw toxcore file numbers nor terminal
frames become scheduler identities in those later slices.

ADR 0177 additionally proves the scheduler's terminal fence in the opposite deterministic fault
order. Once ordinary cancellation has settled and released signed work, stopping the cancelled
pull's retained carrier increments route-loss accounting but performs zero reassignment. Recovery
restores capacity under a fresh worker incarnation; it does not revive the job, reissue an object
request, accept a HEAD, or activate a revision. ADR 0178 then drives ordinary cancellation and one
exact worker stop from the same observable arm edge. Both accepted carriers linearize as
cancel-first: the terminal pull retains its stopped carrier, reassignment remains zero, and one
idempotent cleanup retry settles typed transport unavailability without repeating the effect. The
verifier also recognizes the bounded one-reassignment loss-first outcome. Randomized timing and
multiple affected pulls on one failed carrier remained open at that boundary. ADR 0179 then live-qualifies that second
branch on UDP and TCP: one old-route fence, one fresh assignment, and cancellation of the replacement
before route-capacity recovery. ADR 0180 qualifies four affected jobs from one fixed-policy carrier.
Every replacement selection requires the job's complete remaining object count to fit before any
assignment debit; recovery waits for every exact remembered job to become terminal.

Agent now has an explicit fixed/adaptive carrier selector above this scheduler. It operates only
before `assign` or after `fence_route`, uses current signed-capacity accounting, and cannot mutate an
active scheduler attempt. Candidate eligibility takes the complete requested work set, not a
one-object probe; zero required work is invalid. The adaptive algorithm and decision counters are frozen by ADR 0170; its
two-guest topology qualification is accepted by ADR 0171, while larger randomized performance and
fairness qualification remains Gate 4 work.
