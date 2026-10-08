# CELL-097 — Flow-Latent Continuous Thought Mini

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0097`  
Sources: SRC-0156

## Cheap first run

Train tiny flow over continuous thought positions.

## Baselines

- deterministic latent
- gaussian latent
- normalizing flow latent
- explicit CoT

## Metrics

- likelihood
- task_success
- sample_diversity
- cost

## Stop condition

If flow adds no exploration/calibration, demote.
