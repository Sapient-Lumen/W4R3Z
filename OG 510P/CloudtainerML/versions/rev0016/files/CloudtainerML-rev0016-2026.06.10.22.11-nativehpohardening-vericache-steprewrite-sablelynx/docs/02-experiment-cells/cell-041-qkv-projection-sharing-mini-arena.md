# CELL-041 — QKV Projection Sharing Mini-Arena

Priority: P0  
Status: candidate-with-runnable-probe

## Cheap first run

Runnable scaffold exists in experiments/qkv_projection_sharing/qkv_projection_probe.py; smoke output under artifacts/probe-results/.

## Metrics

accuracy/exact match, loss/error, memory bytes, runtime, failure mode count, seed variance

## Stop condition

If all projection variants are indistinguishable after stronger direction-sensitive tasks, demote.
