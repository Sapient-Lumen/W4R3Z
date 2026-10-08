# CELL-169 — Exact Kernel Linear-Attention Dilution Probe

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0168` — Exact/kernel linear-attention dilution probe

## Core question

Which kernel constraints actually prevent token-attention dilution in content-addressed recall?

## Source anchors

- `SRC-0207` — Exact Linear Attention (https://arxiv.org/abs/2605.18848)

## Cheap first run

No runnable probe yet; exact/kernel linear attention on adversarial associative recall.

## Metrics

- recall accuracy
- dilution slope
- near-neighbor failure rate
- state norm stability

## Required baselines

- softmax
- normalized outer-product memory
- random features
- oracle support

## Falsifier / stop condition

If exact kernels do not beat simple normalized memory, demote.

## Rev0013 note

This cell was added during the native-frontier pass. C++ is preferred when the inner loop is deterministic, high-volume, and framework-free; Python remains preferred for training, plotting, and orchestration.
