# CELL-123 — SMT Transition Label Probe

Priority: **P0**  
Status: **active**  
Idea: `IDEA-0122`  
Sources: SRC-0187

## Cheap first run

Run smt_transition_probe.py on key/value streams.

## Metrics

- query accuracy
- state accuracy
- overwrite accuracy
- memory MSE

## Required baselines

- teacher oracle
- zero memory
- recency buffer
- noisy recurrent
- ridge supervised update

## Stop condition

If supervised update cannot beat recency after feature audit, demote.
