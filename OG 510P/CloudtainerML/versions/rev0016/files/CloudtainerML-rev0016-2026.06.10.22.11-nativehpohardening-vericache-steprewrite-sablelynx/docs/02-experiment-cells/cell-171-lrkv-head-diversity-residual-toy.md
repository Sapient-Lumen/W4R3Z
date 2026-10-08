# CELL-171 — LRKV Head-Diversity Residual Toy

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0170` — LRKV head-diversity residual toy

## Core question

How much head diversity can a low-rank residual recover over shared KV in a tiny synthetic attention task?

## Source anchors

- `SRC-0209` — Low-Rank Key Value Attention (https://arxiv.org/abs/2601.11471)

## Cheap first run

No runnable probe yet; synthetic head roles with shared and orthogonal components.

## Metrics

- attention output error
- head-role recovery
- rank-vs-error frontier
- bytes saved

## Required baselines

- full MHA
- shared KV
- GQA-like
- K=V
- low-rank residual KV

## Falsifier / stop condition

If low-rank residuals do not rescue head-specific roles, demote.

## Rev0013 note

This cell was added during the native-frontier pass. C++ is preferred when the inner loop is deterministic, high-volume, and framework-free; Python remains preferred for training, plotting, and orchestration.
