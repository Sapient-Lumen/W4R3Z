# ADR 0108: coordinate routes above Tox

- Status: accepted architecture direction; product coordinator pending
- Date: 2026-08-21
- Scope: multi-route identity, Ratox continuity, synchronization, and bulk scheduling
- Depends on: ADR 0002, ADR 0030, ADR 0059, ADR 0061, ADR 0093, ADR 0094, ADR 0106, and ADR 0107

## Context

One forced-TCP Tox instance did not service every member of a 32-transfer population inside the
construction bound. Four independently keyed instances, each limited to eight transfers, advanced
all 32 while Ratox remained exact. A later gate recovered an auxiliary route process from unchanged
savedata before admitting the same workload.

These observations show that independent Tox instances can escape a practical single-instance
service boundary on the founding host. They do not show packet bonding, proportional aggregate
throughput, physical-path diversity, or safe migration of an active transfer.

## Decision

1. IoTox coordinates multiple routes above Tox. It does not present several `Tox*` instances as one
   transparent socket or modify frozen Ratox framing to simulate packet bonding.
2. Every member route has a distinct Tox identity and must prove its binding to the same stable IoTox
   device principal and route-set coordinator. Tox friendship remains transport, never authority.
3. Ratox control and byte frames remain on one protected route for an attachment. IoTox may resume a
   fenced application session over a newly authenticated route in the future, but it never silently
   stripes, duplicates, or migrates live terminal frames.
4. Immutable, digest-verified synchronization objects are the first eligible production units for
   multi-route scheduling. Tox file numbers and process-local transfer positions are not durable
   object identities.
5. The product remains single-route by default until the coordinator, route binding, live-loss
   semantics, resource accounting, and operator evidence are implemented and qualified. Auxiliary
   routes are explicit policy, not ambient capacity.
6. A required route set has explicit `connecting`, `authenticated`, `ready`, `recovering`, and
   `unavailable` states. Missing required capacity fails closed; it cannot silently overload the
   remaining routes or move Ratox.

## Consequences

- The stable device principal is the authority anchor above replaceable transport identities.
- Sync and OTA can eventually retry immutable work on another route after fencing the old attempt
  and verifying final bytes. Generic path-based live transfers cannot assume that behavior.
- A protected interactive route and per-route bulk budgets become scheduler invariants.
- One process versus supervised route workers remains an implementation choice; one product binary
  and one authority coordinator remain mandatory.
- UDP, relay diversity, throughput scaling, power, memory, and connection-establishment cost require
  separate evidence. The current four-route TCP result is not generalized into a universal default.

The implementation and evidence order is maintained in `../multi-route-plan.md`.
