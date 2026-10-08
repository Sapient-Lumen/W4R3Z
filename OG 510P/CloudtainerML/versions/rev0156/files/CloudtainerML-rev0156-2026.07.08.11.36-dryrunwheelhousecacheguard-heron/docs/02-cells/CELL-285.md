# CELL-285 — Routing-Consistent MoE Quantization Toy

Priority: **P1**  
Status: **candidate**

## Why this cell exists
No code yet; future native toy should separate expert-selection consistency from value reconstruction under quantized routers and experts.

## Question
Linked idea: `IDEA-0284`.

## Sources
SRC-0306, SRC-0302

## Metrics
- score
- loss/error
- runtime/FLOPs proxy
- memory/bytes proxy
- failure-mode fields
- winner counts

## Stop condition
If routing consistency does not predict rare-domain failure, demote.

## Rev0026 note
This cell keeps CloudtainerML centered on tiny-scale performance/surprise. Security/trust side-wing material is not driving this priority.
