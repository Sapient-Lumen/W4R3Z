# CELL-229 — Curvature-Conditioned Readout Probe

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0228`  
Sources: SRC-0256

## Cheap first run

Extend spectral associative recall with query-side curvature features and target-dilution regimes.

## Metrics

- recall_accuracy
- dilution_error
- state_bytes
- read_cost

## Required baselines

- additive_linear_memory
- delta_memory
- curvature_query
- attention_oracle

## Stop condition

If curvature conditioning cannot rescue diluted targets, prefer write-side memory sparsity.
