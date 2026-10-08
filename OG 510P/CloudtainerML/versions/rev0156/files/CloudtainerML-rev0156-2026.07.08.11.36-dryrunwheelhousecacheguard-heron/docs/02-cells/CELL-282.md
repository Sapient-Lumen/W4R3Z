# CELL-282 — Sgatlin Tiny Linear Experts

Priority: **P0**  
Status: **candidate-with-runnable-probe**

## Why this cell exists
Runnable C++ probe at experiments/sgatlin_tiny_linear_experts/sgatlin_tiny_linear_experts.cpp; smoke output REV0026_SGATLIN_TINY_LINEAR_EXPERTS_SMOKE.json.

## Question
Linked idea: `IDEA-0281`.

## Sources
SRC-0303, SRC-0301

## Metrics
- score
- loss/error
- runtime/FLOPs proxy
- memory/bytes proxy
- failure-mode fields
- winner counts

## Stop condition
If tiny linear experts only win by undercharging routing overhead or fail rare-feature regimes without repair, keep as conditional.

## Rev0026 note
This cell keeps CloudtainerML centered on tiny-scale performance/surprise. Security/trust side-wing material is not driving this priority.
