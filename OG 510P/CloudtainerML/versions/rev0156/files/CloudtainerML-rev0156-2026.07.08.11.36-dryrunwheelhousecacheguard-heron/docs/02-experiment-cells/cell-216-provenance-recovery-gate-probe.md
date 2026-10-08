# CELL-216 — Provenance Recovery Gate Probe

Priority: **P0**  
Status: **runnable**  
Idea: `IDEA-0215`  
Sources: SRC-0241

## Cheap first run

Run experiments/provenance_recovery_gate/provenance_recovery_probe.cpp.

## Metrics

- yield
- valid accept rate
- injection recall
- recovery rate
- quality
- utility

## Required baselines

- reward-only
- provenance-only
- dual gate
- adaptive recovery
- naive resample

## Stop condition

If recovery lowers valid accept rate or injection recall, mark as unsafe.
