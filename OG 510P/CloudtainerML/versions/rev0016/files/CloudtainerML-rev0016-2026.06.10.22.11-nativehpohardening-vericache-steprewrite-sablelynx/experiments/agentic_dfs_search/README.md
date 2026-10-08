# Agentic DFS search probe

A cheap stochastic tree-search environment for testing whether DFS/backtracking
is the right tiny task before training a transformer/RL policy. Policies include
single-capability ablations meant to mimic missing action-trace or failure-trace
heads.

Run:

```bash
python experiments/agentic_dfs_search/dfs_search_probe.py
```
