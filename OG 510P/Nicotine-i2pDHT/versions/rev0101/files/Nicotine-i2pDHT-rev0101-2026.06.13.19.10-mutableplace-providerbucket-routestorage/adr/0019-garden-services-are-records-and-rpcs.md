# ADR 0019: Garden services are records and RPCs

## Decision

Represent garden capacity as signed advertisements in the DHT record plane and future garden actions as DHT RPCs, not as a separate privileged network.

## Rationale

A separate garden network would quickly become central infrastructure.  Garden nodes should be discoverable and useful through the same substrate they help maintain.  Their advertisements are menus, not proof.

## Consequences

- Garden advertisements need a validator.
- Garden RPC transcripts need canonical fixtures in rev0006.
- Leaves must cross-check garden answers through normal DHT paths.
