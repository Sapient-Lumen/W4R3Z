# CELL-099 — Structural Attention Grokking Intervention

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0099`  
Sources: SRC-0162

## Cheap first run

Inject attention support hints on dependency graph.

## Baselines

- no hint
- KL support
- oracle support
- MLP-only control

## Metrics

- grokking_time
- support_recall
- label_leakage_check

## Stop condition

If hints leak labels, invalid.
