# CELL-273 — Group-Shared Sparse Tail Kernel Guard

- priority: P0
- status: implemented-native-rev0025
- idea: IDEA-0272
- sources: SRC-0295

## Cheap first run

Test dense-head/sparse-tail and group-shared fan-in under long-tail and kernel-overhead regimes.

## Metrics

- precision_at_k
- wall_proxy
- memory_proxy
- kernel_penalty
- score

## Required baselines

- dense_output
- random_fixed_fanin
- group_shared_fanin
- dense_head_sparse_tail
- oracle_group_sparse

## Stop condition

Promote if group-sharing wins with realistic kernel penalties and noisy tail labels.
