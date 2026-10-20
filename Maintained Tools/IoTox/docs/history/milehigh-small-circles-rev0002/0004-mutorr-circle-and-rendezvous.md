# ADR 0004: Namespace circles and rendezvous custodians

**Status:** accepted for rev0002

## Context

Using one Tox group as the database bus would couple namespace membership to chat membership and can create unnecessary all-peer relationships. IoT devices need bounded connections, selective subscription, deterministic reorganization, and durable replication without a central coordinator.

## Decision

Each mutable namespace receives an independent Cube built from its authorized member IDs.

- Sort unique 256-bit IDs into a ring.
- Connect each member to an even, bounded number of symmetric ring neighbors; default four.
- Gossip small head/inventory announcements across those neighbors with future message deduplication.
- Select durable custodians using highest-random-weight placement; default replication factor three.
- Keep immutable object transfer separate from announcements.
- Represent the mutable pointer as a linked, canonical, separately signable fixed-size head.

## Consequences

Thirty peers use 60 overlay edges instead of 435 full-mesh pairs. The default graph has an eight-hop diameter, so updates trade a small propagation delay for bounded per-device connectivity and distributed upload work.

Every peer must have a sufficiently consistent membership snapshot. Temporary disagreement can produce different neighbors or custodians, so the later membership protocol needs epochs and anti-entropy. The current fast placement mixer is not suitable as a defense against adversarial identity grinding.
