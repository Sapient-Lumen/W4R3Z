# CELL-196 — Tensor Memory Fixed-State Frontier

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0195`  
Sources: SRC-0229

## Cheap first run

No runnable probe yet; implement moving-object/fact grid with occlusion and delayed queries.

## Metrics

- recall under occlusion
- state bytes
- update cost
- query success

## Required baselines

- sliding window KV
- Tensor Cache L2
- fixed tensor grid
- oracle grid

## Stop condition

If spatial memory only wins when coordinates are leaked, narrow it to vision/video tasks.
