# CELL-033 — Entmax Support-Recovery Probe

Priority: **P1**  
Status: `candidate`  
Idea: `IDEA-0033`  
Sources: SRC-0079, SRC-0018

## Question

Does exact-zero sparse attention make cache pruning a support-recovery problem with clearer success criteria?

## Cheap first run

Single-head attention probe with softmax, sparsemax, entmax-ish bisection, and page/top-k support pruning.

## Baselines

- random or identity baseline
- strong simple heuristic
- matched-budget architecture baseline

## Metrics

- accuracy/exact match
- loss/error
- memory bytes
- runtime
- failure mode count
- seed variance
- support_recall
- dropped_mass

## Stop condition

If support recovery does not correlate with output error, revise.


## Runnable rev0005 scaffold

- Script: `experiments/entmax_support_recovery/entmax_support_probe.py`
- Smoke output: `artifacts/probe-results/REV0005_ENTMAX_SUPPORT_SMOKE.json`
