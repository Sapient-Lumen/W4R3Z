# CELL-308 — Copying Challenge Guard for Bounded Memory

Priority: **P1**  
Status: `future-candidate`

## Why this exists
Add exact copy and needle tasks to ranker, linear-attention, SSM-ish, and spectral operator probes.

## Metrics
- exact_copy_rate
- needle_exact_match
- cost_frac
- distractor_error

## Required baselines
- full_attention
- local_window
- recurrent_summary
- ranker_topk

## Stop condition
If a method cannot pass exact copying under tiny synthetic tests, block trained escalation.
