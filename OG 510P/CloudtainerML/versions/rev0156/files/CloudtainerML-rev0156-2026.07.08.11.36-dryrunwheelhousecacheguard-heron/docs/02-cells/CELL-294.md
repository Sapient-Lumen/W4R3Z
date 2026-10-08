# CELL-294 — Oscillator Attention Proxy Scout

Priority: **P2**  
Status: **future-candidate**

## Why this cell exists
Future C++ simulation of fixed-query oscillator attention versus cosine/softmax proxies under iteration budgets.

## Question
Linked idea: `IDEA-0292`.

## Sources
- `SRC-0313`

## Metrics
- attention error
- iteration cost
- entropy regime
- score

## Required baselines
- softmax
- cosine normalization
- linear attention

## Stop condition
Do not promote unless it exposes a software-useful phase, not only a hardware-substrate story.

## Rev0027 note
Performance-first lane. Security/trust side-wing material is not driving this cell.
