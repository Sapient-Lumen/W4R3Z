# CELL-101 — Extreme Low-Bit Reasoning Axis

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0101`  
Sources: SRC-0163, SRC-0072

## Cheap first run

Extend token precision frontier with activation/weight bits.

## Baselines

- KV-only
- weight-only
- activation-only
- mixed bits
- oracle

## Metrics

- final_error
- drift
- bytes
- scratchpad_length

## Stop condition

If same as KV-only, fold back.
