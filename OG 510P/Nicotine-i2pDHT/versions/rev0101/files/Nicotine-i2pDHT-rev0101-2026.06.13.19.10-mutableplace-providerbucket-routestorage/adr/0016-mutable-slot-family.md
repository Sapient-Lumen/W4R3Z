# ADR-0016 — Mutable records are a validator family

## Status

Accepted as a rev0004 design guess.

## Decision

Mutable DHT records should be designed as a family of validator types: single-writer, delegated, Merkle-feed, and CRDT-registry.  The single-writer BEP44-like record remains the first implementation target.

## Rationale

A generic DHT above I2P should not need redesign every time a consumer wants an update feed, delegated publisher, or multiwriter directory.  Storage-node validation can remain simple while application semantics live above it.

## Consequences

- Namespace and validator naming become core protocol surface.
- Mutable values stay small; large state roots point elsewhere.
- Multiwriter semantics are future research, not rev0004 implementation.
