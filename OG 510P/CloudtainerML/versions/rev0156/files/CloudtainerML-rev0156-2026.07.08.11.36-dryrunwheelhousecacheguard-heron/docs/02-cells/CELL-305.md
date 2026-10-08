# CELL-305 — Ranker-Once Contextualization Frontier

Priority: **P1**  
Status: `runnable-native`

## Why this exists
experiments/ranker_contextualization/ranker_contextualization_probe.cpp tests chunk ranker, dense context, local window, recurrent summary, neighbor expansion, and verification.

## Metrics
- recall
- exact_match
- cost_frac
- budget_over
- distractor_leak
- rank_miss
- regret
- score

## Required baselines
- dense_full_context
- local_window_only
- recurrent_summary
- ranker_topk
- oracle_split_ranker

## Stop condition
If ranker wins only by leaking oracle recall, keep as an evaluator not an architecture.
