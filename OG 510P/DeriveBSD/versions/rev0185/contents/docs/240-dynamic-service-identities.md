# Dynamic service identities (ephemeral UIDs/GIDs) and state directories

Most UNIX-like systems end up with a slow-growing pile of “system users”:
one per daemon, hand-created, drift-prone, and hard to audit.

Some ecosystems introduced a better idea: **allocate an execution identity at start-time**,
and tear it down when the service stops — without requiring an operator to pre-provision users.

DeriveBSD can bake this in early, and connect it to the evidence spine.

## Why this is worth baking in

Static system users create failure modes:

- forgotten users linger after services are removed
- UID/GID reuse becomes dangerous across reinstalls
- “who owns this state directory?” becomes unclear over time
- least-privilege is avoided because user management is annoying

Dynamic identities address this by turning “service identity” into an *allocator + lease* problem.

## Baseline: what we steal (conceptually)

The concept to steal is **DynamicUser-style identities**:

- a supervisor allocates an unused UID/GID from a reserved range for a service at start
- the identity is released when the service stops
- state directories are created and gated by the supervisor so persistence is explicit

DeriveBSD doesn’t need to adopt any particular implementation wholesale — only the ergonomics.

## DeriveBSD direction

### 1) Prefer compartments first

For high-value isolation, prefer:
- microVM services
- jail services

Inside a compartment, the service can use a stable UID that is *not shared with the host*.
This avoids host UID churn entirely.

### 2) Host services: identity leases

For host services (where a compartment is overkill), introduce a small primitive:

- **identity lease**: `(service_id, instance_id) → (uid, gid, lease_id)`
- leases are created by the restarter at activation time
- leases are revoked at stop (with a configurable policy for cleanup)

Leases should be represented as evidence (receipt/event), so incident bundles can answer:
“what identity was this service running as when it failed?”

### 3) State directories are explicit

A service with a dynamic identity must declare its state needs, e.g.:

- `StateDirectory=/var/lib/derive/fetchd` (persist)
- `RuntimeDirectory=/run/derive/fetchd` (volatile)
- `CacheDirectory=/var/cache/derive/fetchd` (persist or policy-defined)

DeriveBSD direction: model these as:
- declared paths in `svcdb`
- created by the restarter at start
- recorded in `svc.snapshot` (optional)
- optionally wiped on lease revoke

### 4) Evidence hooks (minimal day-0)

- record `uid/gid` in `svc.event.meta` for start transitions
- optional typed object later: `identity.lease.receipt` (future RFC)

This keeps the initial cut small while making the forensics story strong.

## Interactions

- Promise profiles (`docs/232-service-promise-profiles.md`): dynamic identities should be the default for “unprivileged” profiles.
- Activation (`docs/238-portal-activated-services-and-socket-activation.md`): activator + restarter can ensure endpoints are owned by a stable broker while service runs with a leased UID.
- Fault/incident bundles (`docs/213-*`, `docs/229-*`): identity leases become part of “what happened” evidence.

## Open questions

- Do we require stable mapping across reboots for persistent state? (If yes, leases become “allocations” persisted per generation.)
- Should leases be per-service, per-instance, or per-start?
- How do we make UID reuse safe without bloating the host namespace?

See RFC: `rfcs/RFC-0172-dynamic-service-identities.md`.
