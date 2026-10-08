# CELL-278 — Task-Conditioned Layerwise State Probe

- priority: P1
- status: future-trained-tiny
- idea: IDEA-0277
- sources: SRC-0298

## Cheap first run

Train tiny sequence models on parity/Dyck/copy and map linearly readable state by layer.

## Metrics

- probe_accuracy
- ablation_effect
- length_generalization
- profile_reversal

## Required baselines

- Transformer
- Mamba-ish
- GRU
- oracle_state

## Stop condition

Promote if state profiles reverse by task in tiny runs.
