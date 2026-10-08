# CELL-263 — Tensor-vs-Matrix Decomposition Sanity Probe

Priority: **P0**  
Status: `runnable-native`  
Sources: SRC-0290

## Question

When, if ever, should we chase tensor decompositions rather than componentwise matrix baselines?

## Cheap first run

Run `experiments/tensor_matrix_decomp_sanity/tensor_matrix_decomp_probe.cpp` and treat tensor wins outside shared-subspace regimes as the surprise to seek.

## Metrics

- `score`
- `recon_error`
- `downstream_loss`
- `overhead`

## Required baselines

- `matrix_svd_layerwise`
- `componentwise_svd_qk_ov_mlp`
- `tucker_tensor_shared`
- `tensor_train_shared`
- `oracle_component_budget`

## Stop condition

Demote tensorization if matrix/componentwise baselines dominate heterogeneous regimes.
