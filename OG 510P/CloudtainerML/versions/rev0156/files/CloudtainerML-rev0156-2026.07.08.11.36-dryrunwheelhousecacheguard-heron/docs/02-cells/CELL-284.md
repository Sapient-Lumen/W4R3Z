# CELL-284 — Critical Layer Isolation Phase Diagram

Priority: **P1**  
Status: **candidate-with-runnable-probe**

## Why this cell exists
Runnable C++ probe at experiments/critical_layer_isolation/critical_layer_isolation.cpp; smoke output REV0026_CRITICAL_LAYER_ISOLATION_SMOKE.json.

## Question
Linked idea: `IDEA-0283`.

## Sources
SRC-0305

## Metrics
- score
- loss/error
- runtime/FLOPs proxy
- memory/bytes proxy
- failure-mode fields
- winner counts

## Stop condition
If fixed layer-0 protection loses whenever the critical layer moves, make CLI a task-diagnostic rather than core compression principle.

## Rev0026 note
This cell keeps CloudtainerML centered on tiny-scale performance/surprise. Security/trust side-wing material is not driving this priority.
