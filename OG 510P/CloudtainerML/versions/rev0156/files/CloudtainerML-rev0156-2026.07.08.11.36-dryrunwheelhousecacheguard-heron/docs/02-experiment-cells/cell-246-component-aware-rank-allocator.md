# CELL-246 — Component-Aware Rank Allocator

Priority: **P0**  
Status: **candidate-with-runnable-native-probe**

## Cheap first run

Runnable C++ probe exists at experiments/component_rank_allocator/component_rank_allocator.cpp; smoke output under artifacts/probe-results/REV0022_COMPONENT_RANK_ALLOCATOR_SMOKE.json.

## Metrics

- functional_error
- byte_cost
- score
- winner counts
- nonoracle winner counts

## Required baselines

- uniform_equal_rank
- parameter_weighted
- raw_energy_greedy
- oracle_exhaustive

## Stop condition

If component-functional/HPO allocation does not beat uniform or raw-energy allocation in fragility regimes, stop before trained compression work.
