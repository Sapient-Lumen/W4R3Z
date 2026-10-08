# ADR 0032 — history-aware mutable heads

## Decision

Mutable-record validation must be separated from mutable-head history validation. A signed, valid mutable record can still be stale or part of a same-sequence fork.

## Consequences

- Clients and gardens keep local highest-seen sequence memory.
- Same-sequence forks are preserved as evidence.
- Stale/rollback observations can generate witness receipts.
- No global consensus or global transparency log is claimed.
