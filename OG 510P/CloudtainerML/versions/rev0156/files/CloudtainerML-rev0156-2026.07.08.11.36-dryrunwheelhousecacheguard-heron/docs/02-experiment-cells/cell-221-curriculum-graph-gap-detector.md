# CELL-221 — Curriculum Graph Gap Detector

Priority: **P2**  
Status: **candidate**  
Idea: `IDEA-0220`  
Sources: SRC-0247

## Cheap first run

Simulate prerequisite DAG and question stream; infer root gaps.

## Metrics

- gap recall
- false topic alarm
- root-cause rank
- frequency baseline delta

## Required baselines

- raw frequency
- topic classifier only
- graph propagation
- oracle gap

## Stop condition

If graph propagation does not improve root cause, drop.
