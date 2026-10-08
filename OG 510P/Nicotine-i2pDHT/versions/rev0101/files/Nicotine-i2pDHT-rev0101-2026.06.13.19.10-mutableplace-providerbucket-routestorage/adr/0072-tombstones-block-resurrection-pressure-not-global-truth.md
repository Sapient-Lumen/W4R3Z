# ADR 0072 — Tombstones block resurrection pressure, not global truth

## Decision

Add signed tombstone records and local tombstone-cache analysis.

## Rationale

Mutable systems need deletion, withdrawal, revocation, and compromise evidence. Without tombstone memory, stale provider/witness caches can resurrect old state.

## Consequence

Tombstones do not create global deletion consensus. They are local evidence that blocks convenient stale-alive answers and forces cross-checking.
