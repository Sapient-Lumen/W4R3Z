# CELL-029 — Region-Wipeout Retention Simulator

Priority: **P0**  
Status: `runnable`  
Idea: `IDEA-0029`  
Sources: SRC-0061

## Question

When does token-level global top-k delete entire reasoning regions even when it keeps many high-score tokens?

## Cheap first run

Already runnable: region_wipeout_probe.py --quick. Sweep global top-k vs region quotas under fixed budgets.

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
- required_region_coverage
- empty_region_fraction

## Stop condition

If mass_segmented does not separate from global_topk in the controlled region task, revise simulator assumptions.
