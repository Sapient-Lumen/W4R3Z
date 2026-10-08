# CELL-076 — QK Restore Amnesia Probe

Priority: **P0**
Status: **candidate-with-runnable-probe**

## Cheap first run

Runnable scaffold exists in experiments/qk_restore_amnesia/qk_restore_probe.py; smoke output under artifacts/probe-results/REV0007_QK_RESTORE_AMNESIA_SMOKE.*.

## Sources

SRC-0131

## Baselines

- pre-SFT QK oracle
- post-local-biased QK
- QK restore
- Procrustes compromise
- local-only ablation

## Metrics

- target rank
- target attention mass
- local decoy mass
- output error
- long recall success

## Stop condition

If restored and post-local QK are indistinguishable, the toy fails to isolate routing amnesia.
