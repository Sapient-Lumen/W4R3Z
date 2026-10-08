# CELL-035 — Feedback-Token Latent CoT Structured Bench

Priority: **P1**  
Status: `candidate`  
Idea: `IDEA-0035`  
Sources: SRC-0081

## Question

Do feedback tokens help toy tabular/time-series tasks by creating a reusable latent scratchpad?

## Cheap first run

Synthetic tabular hidden-factor task: append latent feedback tokens between passes and compare to deeper/looped baselines.

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
- OOD_split_accuracy

## Stop condition

If feedback tokens lose to matched-depth baseline, lower priority.
