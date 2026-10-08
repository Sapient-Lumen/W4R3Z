# CELL-292 — Subquadratic Negative-Guard Battery

Priority: **P1**  
Status: **test-design**

## Why this cell exists
Add pairwise/multi-reference integration tasks to future subquadratic phase screens.

## Question
Linked idea: `IDEA-0291`.

## Sources
- `SRC-0312`
- `SRC-0314`

## Metrics
- single-needle accuracy
- multi-reference integration
- pairwise similarity
- cost

## Required baselines
- dense transformer-like oracle
- local/window baseline
- linear state baseline

## Stop condition
If all subquadratic tests remain single-needle, block promotion claims.

## Rev0027 note
Performance-first lane. Security/trust side-wing material is not driving this cell.
