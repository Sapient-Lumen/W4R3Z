# CELL-108: Observability-Safe Retention MDP Probe

Priority: **P0**
Idea: `IDEA-0107`
Status: **candidate-with-runnable-probe**

## Cheap first run

Runnable scaffold exists in experiments/observability_safe_retention/osmr_probe.py; smoke output under artifacts/probe-results/.

## Required baselines

- random
- recency
- online salience
- offline oracle

## Metrics

- retention score
- future utility fraction
- stale penalty
- reacquire penalty
- topic coverage

## Stop / demote condition

If online salience wins all dormant/stale/redundant regimes, demote risk-aware retention.
