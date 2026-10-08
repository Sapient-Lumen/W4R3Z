# CELL-262 — Oracle Sparse Prefill Gap Decomposition

Priority: **P0**  
Status: `runnable-native`  
Sources: SRC-0283

## Question

Is sparse prefill limited by support budget, learned indexer error, or runtime block-sharing realization?

## Cheap first run

Run `experiments/oracle_sparse_prefill_gap/oracle_sparse_prefill_gap.cpp` and separate oracle budget gap from indexer and realization gaps.

## Metrics

- `score`
- `recall`
- `oracle_gap`
- `indexer_gap`
- `realization_gap`
- `read_cost`

## Required baselines

- `dense_full_prefill`
- `oracle_token_topk`
- `oracle_block_shared`
- `fixed_local_global`
- `random_support`

## Stop condition

Promote if indexer/local repair closes much of the oracle gap at useful read fractions.
