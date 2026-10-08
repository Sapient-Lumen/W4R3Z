# CELL-152 — Centaur HPO State Sharing Toy

Priority: **P0**  
Status: **candidate-with-runnable-probe**

## Question

When does domain knowledge help HPO only after it can see optimizer state?

## Cheap first run

Runnable Python smoke test emits REV0013_CENTAUR_HPO_STATE_SMOKE.json.

## Metrics

- mean best score
- OOM rate
- seed variance
- landscape win count

## Stop condition

If stateless domain proposals or plain CMA-ish search dominate the hybrid across seeds, the lane is meta-only, not a P0 experiment.
