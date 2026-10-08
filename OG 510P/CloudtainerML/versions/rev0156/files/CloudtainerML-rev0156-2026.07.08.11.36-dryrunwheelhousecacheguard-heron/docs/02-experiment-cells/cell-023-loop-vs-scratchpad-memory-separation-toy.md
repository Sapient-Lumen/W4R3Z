# CELL-023 — Loop vs Scratchpad Memory Separation Toy

Priority: **P0**
Status: `candidate`

## Cheapest first run

Build a symbolic looped-state solver and scratchpad solver before neural training; then swap in tiny networks.

## Baselines

- random or identity baseline
- strong simple heuristic
- matched-budget architecture baseline

## Metrics

- accuracy/exact match
- loss/error
- memory bytes
- runtime
- failure mode count
- seed variance

## Stop condition

If synthetic tasks fail to separate finite latent state from explicit scratchpad, redesign the task.

## Source ids

SRC-0023, SRC-0064, SRC-0065, SRC-0062
