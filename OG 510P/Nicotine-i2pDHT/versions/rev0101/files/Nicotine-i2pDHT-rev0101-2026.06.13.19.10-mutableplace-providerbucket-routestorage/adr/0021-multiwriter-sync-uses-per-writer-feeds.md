# ADR-0021: Multiwriter sync uses per-writer feeds

## Decision

Future multiwriter sync over the DHT should use owner/root rosters plus per-writer append-only feeds.  The DHT should publish feed tips as mutable heads.

## Rationale

A single shared mutable write slot is attractive but fragile.  Per-writer feeds preserve authorship, allow offline operation, make revocation clearer, and expose conflicts without silently resolving them.

## Consequences

- The DHT must support many small mutable heads per collection.
- Garden nodes can watch feed tips and roster heads.
- Conflict handling moves to application policy.
