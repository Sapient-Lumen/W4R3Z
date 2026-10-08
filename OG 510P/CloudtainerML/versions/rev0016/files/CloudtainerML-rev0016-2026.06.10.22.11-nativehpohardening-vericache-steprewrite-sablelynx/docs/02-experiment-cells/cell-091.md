# CELL-091 — PCAF Sparse Successor Memory Probe

Priority: **P0**  
Status: **runnable**  
Idea: `IDEA-0091`  
Sources: SRC-0153

## Cheap first run

Run hash/successor candidate retrieval under collision/update/noise scenarios.

## Baselines

- full attention
- local window
- semantic top-k oracle
- pcaf hash
- pcaf hash gate
- random

## Metrics

- exact_success
- target_in_candidates
- output_rel_error
- read_fraction

## Stop condition

If semantic oracle is the only strong non-full method, add learned hash/index or demote.
