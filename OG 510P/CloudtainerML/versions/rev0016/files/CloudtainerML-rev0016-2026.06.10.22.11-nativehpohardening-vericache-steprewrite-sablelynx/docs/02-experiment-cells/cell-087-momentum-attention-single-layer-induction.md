# CELL-087 — Momentum Attention Single-Layer Induction

Priority: **P2**
Status: **candidate**

## Cheap first run

Add momentum/high-pass QK feature to one-layer induction task.

## Sources

SRC-0144

## Baselines

- one-layer attention
- momentum attention
- two-layer baseline

## Metrics

- induction accuracy
- attention pattern
- frequency response
- params

## Stop condition

If momentum helps only by adding capacity, require matched controls.
