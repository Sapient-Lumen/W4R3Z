# CELL-039 — Native Ternary Circuit Survival Probe

Priority: **P2**  
Status: `candidate`  
Idea: `IDEA-0039`  
Sources: SRC-0086

## Question

Which tiny transformer circuits survive native {-1,0,1} weight constraints?

## Cheap first run

Replace Linear layers with ternary straight-through BitLinear in tiny algorithmic models.

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
- circuit_extractability
- ternary_sparsity

## Stop condition

If only slower/worse with no insight, demote.
