# CELL-037 — Finite-State CoT Extraction Battery

Priority: **P1**  
Status: `candidate`  
Idea: `IDEA-0037`  
Sources: SRC-0083

## Question

Does explicit scratchpad create more linearly separable finite-state variables than compressed latent loops?

## Cheap first run

DFA tasks with hidden-state clustering; compare no-CoT, explicit CoT, compressed loop, and scratchpad variants.

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
- state_cluster_purity
- DFA_equivalence

## Stop condition

If clusters are not recoverable on simple automata, change logging/instrumentation.
