# ADR 0071 — Region ledger before high-volume garden reprovide

## Decision

Put a region ledger in front of garden reprovide work.

## Rationale

Region sweep is only useful if garden nodes can schedule, suppress, batch, and refuse work predictably. FIFO provider reannounce queues do not preserve keyspace locality and can amplify source-family floods.

## Consequence

`regionledger.py` becomes the local memory surface for due advertisements, source-family pressure, tombstone suppression, and region-weighted batches.
