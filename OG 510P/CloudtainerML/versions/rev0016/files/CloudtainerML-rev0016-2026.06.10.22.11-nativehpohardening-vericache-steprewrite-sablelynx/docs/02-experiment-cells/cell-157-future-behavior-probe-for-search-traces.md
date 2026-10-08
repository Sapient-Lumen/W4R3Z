# CELL-157 — Future Behavior Probe for Search Traces

Priority: **P1**  
Status: **candidate**

## Question

Are prediction features for future behavior more useful than detectors of already-observed failure?

## Cheap first run

No runnable probe yet; reuse agentic DFS traces as data.

## Metrics

- future outcome AUC
- quality after steering
- false early-exit rate

## Stop condition

If future probes are not better than current-state detectors or trace length, demote.
