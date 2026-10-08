# CELL-267 — Learnable Rank Allocation Toy

Priority: **P1**  
Status: `future-trained-tiny`  
Sources: SRC-0286, SRC-0292

## Question

Can learnable rank/threshold allocation beat HPO rank grids under equal parameter or cache budgets?

## Cheap first run

Train or optimize soft rank gates over synthetic layer/component sensitivity curves.

## Metrics

- `score`
- `rank_budget`
- `heldout_loss`
- `rank_entropy`

## Required baselines

- `uniform_rank`
- `local_hpo_rank`
- `oracle_rank`

## Stop condition

Promote if learned ranks beat local HPO under equal budget.
