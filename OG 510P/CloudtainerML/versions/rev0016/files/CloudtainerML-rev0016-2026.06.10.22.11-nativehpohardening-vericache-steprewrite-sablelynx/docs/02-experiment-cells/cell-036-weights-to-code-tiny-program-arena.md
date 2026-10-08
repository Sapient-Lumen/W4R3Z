# CELL-036 — Weights-to-Code Tiny Program Arena

Priority: **P0**  
Status: `candidate`  
Idea: `IDEA-0036`  
Sources: SRC-0082, SRC-0019, SRC-0073

## Question

Can we bias tiny models toward circuits that are decompilable rather than merely accurate?

## Cheap first run

Train/extract on parity, histogram, sort-small, and Dyck-lite; score executable program equivalence.

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
- program_equivalence
- program_size

## Stop condition

If extraction fails on known-simple tasks, use compiled RASP first.
