# CELL-191: KV Quantization Scale Search

Priority: P1

Status: candidate

Idea: IDEA-0190

Source: SRC-0145, SRC-0001

Cheap first run: No runnable probe yet; extend KV/token precision probes with scale selectors.

Metrics:
- output error
- scale error
- winner-region shift

Baselines:
- MSE scale
- percentile scale
- KVarN-like normalized scale
- task-output scale
- oracle

Stop condition: If scale choices do not move phase boundaries, demote.
