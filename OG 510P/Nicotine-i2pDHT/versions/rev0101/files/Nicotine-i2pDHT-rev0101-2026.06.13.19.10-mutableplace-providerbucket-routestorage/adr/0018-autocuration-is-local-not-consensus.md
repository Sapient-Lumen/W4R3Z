# ADR 0018: Autocuration is local, not consensus

## Decision

Garden and leaf nodes maintain local encounter salience ledgers.  These ledgers guide local peer/garden selection but are not uploaded by default and are not a global reputation system.

## Rationale

Local peer-profile style memory is useful.  Global reputation creates new authority, privacy, and gaming problems.  The first DHT should remember what helped or harmed *this node* and should select diverse gardens based on that memory.

## Consequences

- Salience scores are per-service and decay over time.
- Semantic lies cost more than latency.
- Graceful refusal can be a positive signal.
- Future code should avoid UI language like "trusted" unless trust is narrowly scoped.
