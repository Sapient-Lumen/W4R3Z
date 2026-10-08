# CELL-112: Distributed Active Memory Toy

Priority: **P1**
Idea: `IDEA-0111`
Status: **candidate**

## Cheap first run

Symbolic planner/memory split where planner sees gists and memory daemon consolidates facts.

## Required baselines

- central full history
- recency pruning
- gist-only
- distributed memory

## Metrics

- multi-hop answer accuracy
- tokens shown to planner
- missed detail rate

## Stop / demote condition

If gist split never beats central retention under equal budget, demote.
