# CELL-268 — TwinQuant Decomposed-Subspace Quant Toy

Priority: **P1**  
Status: `future-native`  
Sources: SRC-0287

## Question

Can reparameterizing low-rank/residual/activation components reduce quantization error beyond rotation-only tricks?

## Cheap first run

Add a quantization matrix probe with low-rank/residual/activation components and reparameterization choices.

## Metrics

- `output_mse`
- `tail_error`
- `bits`
- `score`

## Required baselines

- `naive_int4`
- `hadamard_rotation`
- `mixed_precision`
- `oracle_transform`

## Stop condition

Keep if learned/decomposed transforms beat simple rotations after equal calibration budget.
