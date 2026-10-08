# CELL-133 — Evidence-Target Noise Sensitivity

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0132`  
Sources: SRC-0179

## Cheap first run

Sweep false-positive retrieval in EASE toy.

## Metrics

- accuracy vs false positives
- overadaptation rate
- evidence mass

## Required baselines

- hard top-k
- soft target
- oracle target
- random target

## Stop condition

If noise tolerance is flat, redesign target.
