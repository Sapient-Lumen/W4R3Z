# ADR-0022: Garden sync services cache and witness, not author

## Decision

Garden nodes may watch mutable heads, mirror manifests, cache encrypted blocks, relay feed entries, hold tombstones, and witness rollback attempts.  They must not author collection changes unless explicitly granted as normal writers.

## Rationale

Garden nodes are giving supernodes.  They should help leaves and increase availability without becoming cloud owners or consensus authorities.

## Consequences

- Garden service offers are signed and locally selected.
- Garden reports are evidence, not truth.
- The sync control plane keeps authorization on writer/owner signatures.
