# CELL-271 — Expert-Choice Sparse Attention Routing Probe

Priority: **P1**  
Status: `future-probe`  
Sources: SRC-0293

## Question

Does expert-choice token selection produce more useful head specialization than token-choice top-k under equal compute?

## Cheap first run

Compare expert-choice and token-choice support selection with head budgets and candidate recall.

## Metrics

- `support_recall`
- `head_specialization`
- `load_balance`
- `score`

## Required baselines

- `token_topk`
- `expert_choice`
- `oracle_support`

## Stop condition

Promote if expert-choice improves support recall, not only utilization.
