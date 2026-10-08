# CELL-227 — Active Graph Reconstruction Probe

Priority: **P1**  
Status: **candidate**  
Idea: `IDEA-0226`  
Sources: SRC-0253

## Cheap first run

Create cue-tag-content graph tasks where evidence is only recoverable after following intermediate tags; compare static retrieval vs bounded active reconstruction.

## Metrics

- evidence_recall
- expansion_cost
- wrong_branch_rate
- answer_utility

## Required baselines

- static_topk
- rerank_topk
- bounded_graph_walk
- active_reconstruct
- oracle_walk

## Stop condition

If active walks need oracle edges, keep graph memory below execution-state tree memory.
