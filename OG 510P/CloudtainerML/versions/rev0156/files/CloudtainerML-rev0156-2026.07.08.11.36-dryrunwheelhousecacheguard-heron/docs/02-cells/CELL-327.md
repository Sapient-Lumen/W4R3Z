# CELL-327 — Routing Signature Telemetry Guard

Priority: **P1**  
Status: `scouted`  
Idea: `IDEA-0325`  
Sources: SRC-0345

This is a telemetry/refactor candidate: route signatures may expose task-conditioned routing structure before downstream score moves. Keep only if it adds information beyond load balance and accuracy.

## Cheap first run

Add route-signature clustering fields to one existing MoE/router probe.

## Metrics

- `within_task_similarity`
- `across_task_similarity`
- `load_balance_residual`
- `signature_entropy`

## Stop condition

Drop if signatures duplicate downstream accuracy or load-balance metrics.
