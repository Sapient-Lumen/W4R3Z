# CELL-140 — Agentic DFS/backtracking tiny environment

Priority: **P0**  
Status: **candidate-with-runnable-probe**

## Cheap first run

Runnable scaffold exists in experiments/agentic_dfs_search/dfs_search_probe.py; smoke output in artifacts/probe-results/.

## Metrics

- success rate
- steps used
- efficiency
- failure-trace rate
- backtrack rate

## Stop condition

If symbolic DFS succeeds trivially, next test must train a tiny policy and inspect whether two heads specialize as predicted.
