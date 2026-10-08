# CELL-163 — Residual Stream KV Object Frontier

Priority: **P0**  
Status: **runnable-native-probe**  
Idea: `IDEA-0162` — Residual checkpoints as cache object

## Core question

When is storing residual checkpoints plus recomputing K/V a better cache object than storing full KV?

## Source anchors

- `SRC-0201` — The Residual Stream Is All You Need: On the Redundancy of the KV Cache in Transformer Inference (https://arxiv.org/abs/2603.19664)

## Cheap first run

experiments/residual_stream_kv/residual_stream_kv.cpp emits REV0013_RESIDUAL_STREAM_KV_SMOKE.json.

## Metrics

- state_mb
- relative_bytes_vs_full_kv
- estimated_decode_us
- exact_reconstruction_mse

## Required baselines

- full KV
- residual checkpoint recompute
- sliding window KV

## Falsifier / stop condition

If exactness fails or residual never wins plausible byte regimes, demote.

## Rev0013 note

This cell was added during the native-frontier pass. C++ is preferred when the inner loop is deterministic, high-volume, and framework-free; Python remains preferred for training, plotting, and orchestration.
