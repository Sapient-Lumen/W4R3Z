# CELL-030 — Dormant-Token Sponsorship Simulator

Priority: **P0**  
Status: `runnable`  
Idea: `IDEA-0030`  
Sources: SRC-0069

## Question

Can any score-only retention policy keep value tokens that are deliberately attention-dormant until the final query?

## Cheap first run

Already runnable: dormant_sponsorship_probe.py --quick. Test target value retention at tiny budgets.

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
- target_value_retention_rate
- false-positive overhead

## Stop condition

If attention_topk keeps dormant values without sponsorship, the trap is not hard enough.
