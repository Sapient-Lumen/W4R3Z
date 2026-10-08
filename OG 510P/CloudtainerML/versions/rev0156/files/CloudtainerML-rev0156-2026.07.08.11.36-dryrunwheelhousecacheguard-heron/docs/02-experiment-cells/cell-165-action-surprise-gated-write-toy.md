# CELL-165 — Action-Surprise Gated Write Toy

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0164` — Action-surprise gated writes

## Core question

Can a write gate based on action/value surprise preserve useful memory with far fewer writes than periodic policies?

## Source anchors

- `SRC-0203` — AURA: Action-Gated Memory for Robot Policies at Constant VRAM (https://arxiv.org/abs/2606.02775)

## Cheap first run

No runnable probe yet; synthetic control traces with action-change labels.

## Metrics

- task success
- write rate
- state bytes
- delayed recall accuracy

## Required baselines

- write every step
- periodic write
- random write
- novelty gate

## Falsifier / stop condition

If action surprise does not beat simpler gates, demote.

## Rev0013 note

This cell was added during the native-frontier pass. C++ is preferred when the inner loop is deterministic, high-volume, and framework-free; Python remains preferred for training, plotting, and orchestration.
