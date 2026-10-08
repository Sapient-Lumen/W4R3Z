# CELL-081 — Evolving Memory Query Stream Probe

Priority: **P2**
Status: **candidate**

## Cheap first run

Tiny stream where evicted local-window tokens update fixed memory query slots.

## Sources

SRC-0135

## Baselines

- sliding window
- EMA summary
- outer-product memory
- memory query slots

## Metrics

- recall
- drift
- slot utilization
- write entropy

## Stop condition

If learned slots match EMA only, keep as visualization.
