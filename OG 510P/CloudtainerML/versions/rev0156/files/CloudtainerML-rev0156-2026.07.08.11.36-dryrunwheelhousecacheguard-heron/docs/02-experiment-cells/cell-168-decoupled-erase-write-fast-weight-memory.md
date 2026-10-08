# CELL-168 — Decoupled Erase/Write Fast-Weight Memory

Priority: **P0**  
Status: **runnable-native-probe**  
Idea: `IDEA-0167` — Decoupled erase/write fast-weight memory

## Core question

Is tying erase and write gates a real failure mode in tiny associative memory, or does decoupling require learned gates to help?

## Source anchors

- `SRC-0206` — Gated DeltaNet-2: Decoupling Erase and Write in Linear Attention (https://arxiv.org/abs/2605.22791)

## Cheap first run

experiments/gated_delta_memory/gated_delta_memory_probe.cpp emits REV0013_GATED_DELTA_MEMORY_SMOKE.json.

## Metrics

- mean_retrieval_rel_error
- mean_cosine
- winner_counts
- write_rate

## Required baselines

- no erase/write all
- tied scalar delta
- write gate only
- decoupled channel gates
- oracle changed channels

## Falsifier / stop condition

If decoupled hand gates lose, require trained gates before further architecture claims.

## Rev0013 note

This cell was added during the native-frontier pass. C++ is preferred when the inner loop is deterministic, high-volume, and framework-free; Python remains preferred for training, plotting, and orchestration.
