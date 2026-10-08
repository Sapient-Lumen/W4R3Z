# CELL-250 — Attention Dilution Eviction Probe

Priority: **P0**  
Status: **candidate-with-runnable-native-probe**

## Cheap first run

Runnable C++ probe exists at experiments/attention_dilution_eviction/attention_dilution_eviction.cpp; smoke output REV0022_ATTENTION_DILUTION_EVICTION_SMOKE.json.

## Metrics

- useful_recall
- distractor_rate
- output_quality
- cost_ratio
- score

## Required baselines

- full_cache
- recency_topk
- attention_topk
- geometric_proxy
- oracle_future_utility

## Stop condition

If full_cache dominates distraction-heavy equal-cost regimes, learned eviction should stay compression-oriented, not performance-oriented.
