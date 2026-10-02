# ADR 0110: sign route inventory with the stable device

- Status: accepted and implemented admission core; live worker integration pending
- Date: 2026-08-21
- Scope: multi-route membership, downgrade boundary, lifecycle, and budgets
- Depends on: ADR 0030, ADR 0034, ADR 0108, and ADR 0109

## Context

The four-route laboratory proved that independent Tox identities can create useful service domains,
but a collection of friendships is not a device. Without an application artifact, an unknown key
could replace a failed route, workers could disagree about generation and capacity, and independent
agents could accidentally become independent authorities.

## Decision

IoTox route membership is one canonical binary route set signed by the existing stable device
identity. It binds the device principal, coordinator Tox identity, generation, protocol floor, and
2..16 lexically ordered member policies. Every member has one Tox key, protected/bulk role,
connection class, active-work budget, restart budget, and optional expiry. Exactly one member is
protected.

The authority-owning coordinator admits a worker only after exact membership and a confirmed IoTox
transcript prove the same stable principal, generation, protocol floor, and connection class.
Unknown, duplicate, stale, foreign, downgraded, expired, or policy-mismatched claims fail closed.
Workers never own a separate authority ledger merely because they own a route key.

Lifecycle is explicit: `configured`, `connecting`, `authenticated`, `ready`, `recovering`, and
`unavailable`. Only ready routes receive work. Recovery clears admitted capacity and consumes the
signed restart budget before a replacement worker can claim the member.

## Consequences

- Tox keys can rotate through signed route-set generations without changing device ownership.
- A route-set signature authenticates membership only; authority capabilities remain independent.
- The protected route's budget is now a signed policy fact, but ADR 0109 still forbids bulk there by
  default.
- The binary contract and coordinator core are implemented and unit-qualified. Agent configuration,
  process supervision, transcript plumbing, durable generation high-water state, and the public
  `routes`/`routes-watch` projection remain required before Gate 2 is complete.
- No configured policy means no route inventory is loaded and preserves current single-route
  behavior.
