# ADR 0034 — chaos harness before live transport

## Decision

The next design pressure should come from deterministic fake adversarial transcripts before live SAM/I2P transport.

## Consequences

- Stale, forked, silent, and empty replies are testable without network noise.
- Seed-capture reports become cheap to iterate.
- Transport code can later inherit tested invariants instead of hiding design holes behind connection complexity.
