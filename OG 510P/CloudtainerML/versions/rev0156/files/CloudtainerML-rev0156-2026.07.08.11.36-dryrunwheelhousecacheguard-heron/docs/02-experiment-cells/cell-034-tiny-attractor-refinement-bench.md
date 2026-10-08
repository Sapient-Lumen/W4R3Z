# CELL-034 — Tiny Attractor Refinement Bench

Priority: **P1**  
Status: `candidate`  
Idea: `IDEA-0034`  
Sources: SRC-0080, SRC-0023

## Question

Can fixed-point refinement solve tiny maze/constraint tasks with fewer parameters than equivalent feed-forward depth?

## Cheap first run

Fixed-point/refinement MLP on maze-lite and pointer chase; compare loops, convergence threshold, and equivalent depth.

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
- iterations_to_converge
- cycle_rate

## Stop condition

If convergence dominates wall-clock without accuracy gain, postpone.
