# CELL-280 — FFN-Attention Redistribution Meter

Priority: **P0**  
Status: **candidate-with-runnable-probe**

## Why this cell exists
Runnable C++ probe at experiments/ffn_attention_redistribution/ffn_attention_redistribution.cpp; smoke output REV0026_FFN_ATTENTION_REDISTRIBUTION_SMOKE.json.

## Metrics
- score
- loss/error
- runtime/FLOPs proxy
- memory/bytes proxy
- failure-mode fields
- winner counts

## Stop condition
If attention_shift is uninformative or sparse variants never expose a compute/performance tradeoff, demote.

## Rev0026 focus
Performance-core / tiny architecture-surprise lane. Security/trust material is a bounded side wing, not the project center.
