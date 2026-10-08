# ADR 0033 — capabilities before application polish

## Decision

Delegated capabilities and revocation heads are part of the DHT control-plane foundation, not an application afterthought.

## Consequences

- Garden services can be bounded by verb, resource, audience, time, and caveats.
- Revocation heads become a first-class mutable-head family.
- Revocation remains eventual and evidence-based, not magic deletion.
