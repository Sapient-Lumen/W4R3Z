# CELL-261 — Subspace-Aware MoE Router Wind Tunnel

Priority: **P0**  
Status: `runnable-native`  
Sources: SRC-0281, SRC-0282

## Question

Can principal-subspace routing beat shallow or balanced routing at tiny scale without starving rare domains?

## Cheap first run

Run `experiments/subspace_moe_router/subspace_moe_router.cpp` and inspect rare-domain / shift / load-balance slices.

## Metrics

- `score`
- `task_error`
- `imbalance`
- `instability`
- `dispatch_cost`

## Required baselines

- `uniform_balanced_router`
- `shallow_linear_router`
- `aux_loss_balanced_router`
- `oracle_domain_router`

## Stop condition

Promote if STAR-style online subspace wins beyond clean clusters without rare-domain collapse.
