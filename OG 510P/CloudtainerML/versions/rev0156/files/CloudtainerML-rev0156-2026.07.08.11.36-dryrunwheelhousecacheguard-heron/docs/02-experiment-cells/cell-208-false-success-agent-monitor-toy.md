# CELL-208 — False Success Agent Monitor Toy

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0208`  
Sources: SRC-0237

## Cheap first run

Generate symbolic agent traces with confident closing claims and environment truth; compare lightweight detectors with judge-like proxies.

## Metrics

- AUROC proxy
- false success recall
- false positive rate
- latency proxy

## Required baselines

- surface judge
- TF-IDF-ish detector
- state verifier
- oracle

## Stop condition

If state labels make it trivial, add partial observability and delayed environment checks.
