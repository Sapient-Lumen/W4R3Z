# CELL-138 — Entropy-guided adaptive inference probe

Priority: **P0**  
Status: **candidate-with-runnable-probe**

## Cheap first run

Runnable scaffold exists in experiments/entropy_guided_budget/entropy_head_probe.py; smoke output in artifacts/probe-results/.

## Metrics

- primary utility
- accuracy/error
- compute fraction
- failure regime count
- seed variance

## Stop condition

If entropy_plus_decode wins only because it is an oracle proxy, split the probe into prefill-only and generated-token-only budgets.
