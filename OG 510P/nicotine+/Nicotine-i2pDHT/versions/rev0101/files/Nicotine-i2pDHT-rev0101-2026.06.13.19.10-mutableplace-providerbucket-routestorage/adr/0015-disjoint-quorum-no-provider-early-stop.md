# ADR-0015 — Disjoint quorum and no default provider early stop

## Status

Accepted as a rev0004 design guess.

## Decision

Lookups should preserve multiple path queues and require path-diverse evidence before accepting values.  Provider lookups should not stop merely because a fixed number of providers was returned, unless an explicit fast/unsafe mode is selected.

## Rationale

Semantic falsehood is more dangerous than silence.  A malicious cluster can return plausible provider records early and cause a client to stop before honest paths are explored.

## Consequences

- Lookup code is more complex than a simple candidate heap.
- Some lookups cost more round trips.
- The DHT gains a testable hook for eclipse/sybil chaos simulations.
