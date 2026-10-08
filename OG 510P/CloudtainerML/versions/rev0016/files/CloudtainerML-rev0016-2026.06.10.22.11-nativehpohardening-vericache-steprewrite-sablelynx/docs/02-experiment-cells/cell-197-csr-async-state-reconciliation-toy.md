# CELL-197 — CSR / Async State Reconciliation Toy

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0196`  
Sources: SRC-0230

## Cheap first run

No runnable probe yet; C++ discrete-event scheduler with prefix stability and async eviction cycles.

## Metrics

- latency spike rate
- recall
- eviction debt
- stale-state errors

## Required baselines

- synchronous eviction
- sliding window
- async reconciliation
- oracle eviction schedule

## Stop condition

If async only shifts spikes off-metric while degrading recall, demote.
