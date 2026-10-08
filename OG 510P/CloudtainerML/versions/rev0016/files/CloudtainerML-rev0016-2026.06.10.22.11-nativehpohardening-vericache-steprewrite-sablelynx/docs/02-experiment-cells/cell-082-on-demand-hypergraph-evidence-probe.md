# CELL-082 — On-Demand Hypergraph Evidence Probe

Priority: **P2**
Status: **candidate**

## Cheap first run

Generate hierarchical documents with multi-hop cross-section answers and experience replay.

## Sources

SRC-0136

## Baselines

- flat topk
- tree traversal
- hypergraph working memory
- oracle path

## Metrics

- F1/exact
- nodes visited
- hyperedge usefulness
- cost

## Stop condition

If hypergraph adds no value over flat topk in controlled cross-evidence tasks, defer.
