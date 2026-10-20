# ADR 0167: Bound auxiliary synchronization object frames

Status: accepted at the process-local construction boundary, 2026-08-25.

## Context

Gate 3 already has canonical sync object request/result records, an authenticated auxiliary-worker
inventory, exact route-incarnation file send/receive seams, terminal outcome retention, and a
transport-neutral immutable-object scheduler. The worker service loop nevertheless discarded every
application type after HELLO, CAPABILITIES, and route binding. Enabling all synchronization messages
there would wrongly move signed HEAD discovery, activation, range negotiation, authority, or
scheduler effects into a transport child.

An unbounded parent queue is also rejected. A valid remote peer can send lossless records faster than
the parent applies filesystem or scheduler work, and route loss must not leave already-drained records
looking current merely because their payload is canonical.

## Decision

`WorkerSupervisor` gains a default-off synchronization-frame construction gate. Only when enabled
before start does an auxiliary session advertise `state-sync-v1`. The only admitted application
types are canonical `sync_object_request` and `sync_object_result`; HEAD, range, activation, command,
terminal, and every other record remain unavailable on this path.

Outbound calls require the exact reciprocally authenticated bulk route key and random worker
incarnation, negotiated state sync, and a fully valid canonical object frame before using the bulk
owner-queue class. Protected, stale, merely connected, disabled, and semantically malformed calls
fail before transport.

Inbound frames require the same confirmed reciprocal binding and negotiated feature. Each accepted
record enters a pre-reserved bounded FIFO tagged with the local route key, worker incarnation,
auxiliary friend number and online epoch, remote route-set generation, and proven remote stable
principal. Saturating accepted/rejected counters and queued depth are content-free. Capacity
exhaustion drops no existing record and creates no application effect. Disconnect, friend removal,
or primary-trust replacement purges still-queued records for that exact incarnation before clearing
authentication.

The parent owns draining and must match the complete incarnation fence before any publisher,
subscriber, scheduler, or file effect. This ADR does not enable Agent dispatch; advertising remains
off until that route-aware parent integration exists.

## Consequences

- Auxiliary workers can carry the fixed immutable-object negotiation vocabulary without gaining
  authority, namespace, HEAD, activation, or scheduling ownership.
- An application record cannot retarget a replacement worker merely because toxcore reused a friend
  or file number.
- Queue pressure is bounded and visible; the established record is retained ahead of later excess
  traffic.
- The existing single-route product and enabled route workers advertise no new feature by default.
- Cross-route authority context, publisher replay identity, object assignment, live-loss fencing,
  and reassignment remain parent work.

## Verification

The mock-provider integration drives an exact bulk worker through HELLO, CAPABILITIES, reciprocal
stable-principal route binding, and `state-sync-v1` negotiation. It sends a canonical object result
through the real transport, receives the provider's reciprocal packet, and requires every event
fence field. A one-record queue retains the first frame, rejects the second without eviction, drains
exactly once, and purges a later retained frame when primary trust is withdrawn. Wrong worker IDs,
disabled workers, and non-object types fail before effect. GCC Debug and Clang ASan/UBSan suites pass;
GCC TSan passes after making its unrelated one-slot required-event backpressure fixture deterministic.
