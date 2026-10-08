# CELL-219 — Recall-Preserving Rerank Cascade Toy

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0218`  
Sources: SRC-0245

## Cheap first run

Fix a top-k candidate set and compare rerank-only policies under anti-shortcut ablations.

## Metrics

- MRR proxy
- Hit@1
- Recall@10 fixed
- shortcut-collapse gap

## Required baselines

- raw dense
- protected top-10
- small reranker
- full-pool reranker oracle

## Stop condition

If candidate-specific text is not load-bearing, discard.
