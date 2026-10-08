# Staleness and tombstones for parameter and witness-set migrations

**Track:** A (Deployable core)


## Goal
Prevent clients from accepting **stale election parameters** or **stale witness sets** during outages, partitions, or migration events.

This document introduces a tombstone mechanism for “this namespace has moved” and defines strict client behavior.

## Tombstone object
A `Tombstone` indicates that a label/namespace (e.g., witness set ID, EPB label) MUST no longer be considered authoritative in the old location.

Tombstones MUST be:
- signed by the governance authority and/or witness quorum
- anchored into the transparency log

## Client rules
- Clients MUST check the most recent checkpoint before trusting any cached parameter or witness set.
- If a tombstone is present, clients MUST follow the migration policy; they MUST NOT accept stale values even if the new location is unreachable.

## Migration policy
A migration policy MUST specify:
- which old labels are tombstoned
- which new labels replace them
- rollback safety constraints
