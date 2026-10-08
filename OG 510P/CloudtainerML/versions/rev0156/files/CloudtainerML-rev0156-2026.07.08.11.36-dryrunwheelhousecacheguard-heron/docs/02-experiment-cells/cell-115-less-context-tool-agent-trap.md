# CELL-115: Less-Context Tool-Agent Trap

Priority: **P1**
Idea: `IDEA-0114`
Status: **candidate**

## Cheap first run

Tool-log simulator with stale outputs and verbose observations; compare full history vs last-k vs summary.

## Required baselines

- full history
- last-k
- last-k+summary
- selective retention

## Metrics

- current-state exact match
- stale error count
- token budget

## Stop / demote condition

If full history always wins under exact scorer, wait for real LLM tests.
