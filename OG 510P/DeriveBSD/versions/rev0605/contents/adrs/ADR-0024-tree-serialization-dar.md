# ADR-0024: Use a canonical tree encoding for store objects (proposed)

- Status: proposed
- Date: 2026-02-23

## Decision
DeriveBSD defines a canonical filesystem-tree encoding (DAR) for computing digests and for cache replication.

## Consequences
- enables stable digests for tree objects
- simplifies verification pipelines
- requires explicit policy for metadata tiers
