# ADR 0075 — sibling broadcast before store success

## Decision

A storage operation is not locally healthy merely because one close node accepted it. The cube will model sibling-broadcast receipt pressure before live STORE RPC design.

## Consequences

Accepted receipts need count, family diversity, and close-window coverage. Useful refusals are preserved as capacity evidence but do not count as replication success. Contradictory same-node receipts quarantine the local decision.
