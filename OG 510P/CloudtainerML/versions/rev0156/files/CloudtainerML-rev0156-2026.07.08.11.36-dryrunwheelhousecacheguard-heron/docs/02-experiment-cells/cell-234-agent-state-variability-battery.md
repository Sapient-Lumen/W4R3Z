# CELL-234 — Agent State Variability Battery

Priority: **P2**  
Status: **candidate**  
Idea: `IDEA-0233`  
Sources: SRC-0260

## Cheap first run

Run identical symbolic agents with different memory update and sampling seeds; measure divergence and false-success tails.

## Metrics

- trajectory_divergence
- false_success_rate
- state_replay_stability
- utility_variance

## Required baselines

- stateless
- same_memory_different_sampling
- same_sampling_different_memory
- oracle_replay

## Stop condition

If variability is trivial or uninformative, merge into DFS/TRACE.
