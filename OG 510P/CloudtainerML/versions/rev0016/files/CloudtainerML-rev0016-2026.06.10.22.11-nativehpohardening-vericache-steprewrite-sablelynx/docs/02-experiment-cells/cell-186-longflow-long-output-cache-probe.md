# CELL-186: LongFlow Long-Output Cache Probe

Priority: P1

Status: candidate

Idea: IDEA-0185

Source: SRC-0041

Cheap first run: No runnable probe yet; synthetic long-output scratchpad trace with current-query-only importance.

Metrics:
- output error
- importance update cost
- phase-shift regret

Baselines:
- frozen scores
- current-query flow
- periodic recompute
- oracle

Stop condition: If flow scores lag phase shifts, merge with step-boundary rewrite.
