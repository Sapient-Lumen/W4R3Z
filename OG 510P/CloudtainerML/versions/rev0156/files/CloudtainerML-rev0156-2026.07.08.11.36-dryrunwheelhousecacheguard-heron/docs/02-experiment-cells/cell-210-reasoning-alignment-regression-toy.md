# CELL-210 — Reasoning Alignment Regression Toy

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0210`  
Sources: SRC-0240, SRC-0127

## Cheap first run

Two-objective synthetic update: improve reasoning score while monitoring safety/privacy canary projections.

## Metrics

- reasoning score
- safety canary loss
- KL drift proxy
- privacy leakage proxy

## Required baselines

- base
- reasoning-only update
- constrained update
- oracle Pareto

## Stop condition

If toy is too hand-coded, wait for tiny trained transformer.
