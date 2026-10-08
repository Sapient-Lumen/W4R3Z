# CELL-031 — Value-Outlier Eviction Simulator

Priority: **P0**  
Status: `runnable`  
Idea: `IDEA-0031`  
Sources: SRC-0077

## Question

Is protecting large value-norm tokens plus diversity sampling a better default than attention top-k under reasoning-like cache traps?

## Cheap first run

Already runnable: value_outlier_probe.py --quick. Compare attention, value norm, stochastic, segment-diverse, and vase_toy policies.

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
- critical_retention_rate
- segment_diversity

## Stop condition

If value protection does not improve low-attention critical retention, demote.
