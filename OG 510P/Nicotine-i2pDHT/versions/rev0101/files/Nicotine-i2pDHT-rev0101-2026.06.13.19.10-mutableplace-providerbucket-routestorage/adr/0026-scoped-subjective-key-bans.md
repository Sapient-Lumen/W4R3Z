# ADR 0026 — Scoped subjective key bans

## Decision

Represent maintainer/developer bans as signed policy capsules with scoped entries, not as DHT protocol truth.

## Rationale

Official builds and public bridges need abuse controls.
But decentralized protocol validity should remain cryptographic and user-replaceable.

## Consequences

- Maintainers can ban keys from official seeds, bridges, and defaults.
- Users can disable/replace policy authorities.
- Protocol storage does not globally erase keys.
- Policy capsules must expire and be visible.
