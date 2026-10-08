# CELL-283 — Sparse State Expansion Linear-Attention Probe

Priority: **P1**  
Status: **candidate-with-runnable-probe**

## Why this cell exists
Runnable C++ probe at experiments/sparse_state_expansion/sparse_state_expansion.cpp; smoke output REV0026_SPARSE_STATE_EXPANSION_SMOKE.json.

## Question
Linked idea: `IDEA-0282`.

## Sources
SRC-0304

## Metrics
- score
- loss/error
- runtime/FLOPs proxy
- memory/bytes proxy
- failure-mode fields
- winner counts

## Stop condition
If partitioned state has no advantage over single state at equal bytes, demote.

## Rev0026 note
This cell keeps CloudtainerML centered on tiny-scale performance/surprise. Security/trust side-wing material is not driving this priority.
