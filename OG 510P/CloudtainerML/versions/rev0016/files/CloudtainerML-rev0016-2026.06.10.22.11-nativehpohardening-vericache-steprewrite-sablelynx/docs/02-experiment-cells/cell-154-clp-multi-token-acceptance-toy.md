# CELL-154 — CLP Multi-Token Acceptance Toy

Priority: **P1**  
Status: **candidate-with-runnable-probe**

## Question

Is the first predicted token special enough that acceleration should never let auxiliary heads compete with the backbone LM head?

## Cheap first run

Runnable Python smoke test emits REV0013_CLP_MULTITOKEN_ACCEPTANCE_SMOKE.json.

## Metrics

- speed-quality utility
- tokens per forward
- error rate
- repetition proxy

## Stop condition

If naive MTP-first dominates despite error penalties, the CLP design principle is less relevant at tiny scale.
