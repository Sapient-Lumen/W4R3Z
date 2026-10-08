# CELL-042 — MomentKV Directional Gap Probe

Priority: P0  
Status: candidate-with-runnable-probe

## Cheap first run

Runnable scaffold exists in experiments/moment_directional_gap/moment_directional_probe.py; smoke output under artifacts/probe-results/.

## Metrics

accuracy/exact match, loss/error, memory bytes, runtime, failure mode count, seed variance

## Stop condition

If moment correction fails even on constructed directional-gap streams, demote.
