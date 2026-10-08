# ADR-0014 — Provider/mutable reannouncements should use keyspace-region sweep

## Status

Accepted as a rev0004 design guess.

## Decision

High-volume provider and mutable-head reannouncements should be grouped by keyspace region and swept over a full interval, rather than processed by FIFO key list with one lookup per key.

## Rationale

I2P round trips are expensive.  Many advertisements will share nearby storage nodes.  Grouping by high-order key bits lets a power user discover a region once and batch records to the same neighborhood.

## Consequences

- The DHT needs local queues indexed by region.
- Reannounce work becomes smooth and inspectable.
- Region size must be tuned by live network size and churn.
