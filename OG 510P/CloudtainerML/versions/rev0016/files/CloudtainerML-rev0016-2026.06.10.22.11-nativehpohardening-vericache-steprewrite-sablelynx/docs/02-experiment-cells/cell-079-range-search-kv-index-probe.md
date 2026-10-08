# CELL-079 — Range-Search KV Index Probe

Priority: **P1**
Status: **candidate**

## Cheap first run

Build simple cone/range/LSH indexes over synthetic keys and queries with thresholded relevance.

## Sources

SRC-0134

## Baselines

- dense attention
- topk
- LSH
- cone index
- oracle threshold

## Metrics

- false negative rate
- false positive rate
- output error
- index scan fraction

## Stop condition

If zero false negatives require dense scanning, record boundary and defer.
