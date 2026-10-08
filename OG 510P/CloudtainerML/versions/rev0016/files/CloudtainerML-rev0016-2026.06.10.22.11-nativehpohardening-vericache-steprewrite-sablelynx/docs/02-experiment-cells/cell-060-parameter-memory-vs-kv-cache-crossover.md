# CELL-060 — Parameter Memory vs KV Cache Crossover

Priority: P1

Status: candidate

Source IDs: SRC-0108, SRC-0113

## Cheap first run

Synthetic document QA with low-rank adapter/soft-token memory plus cache-retention sweep.

## Baselines

- full cache
- evicted cache only
- adapter only
- cache plus adapter
- soft-token only

## Metrics

- exact answer
- compression ratio
- adapter rank
- tokens retained
- crossover point

## Stop condition

If adapters only memorize training questions, switch to generated held-out queries.
