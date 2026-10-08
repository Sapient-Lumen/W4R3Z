# CELL-313 — Gated Bidirectional Linear Attention Frontier

Priority: **P1**  
Status: `coded-native-frontier`

## Why it exists

Are local mixing, key gating/forgetting, and output gating enough to make bidirectional linear attention competitive on long-history retrieval toys?

## Cheap first run

Run REV0030_GATED_BIDIRECTIONAL_LINEAR_SMOKE.json; ask if local+gate+norm beats plain linear attention under equal budget.

## Metrics

- `score`
- `quality`
- `cost_frac`
- `forget_error`
- `local_miss`
- `latency_proxy`
- `regret`

## Required baselines

- `bidirectional_self_attention`
- `plain_linear_attention`
- `linear_plus_local_conv`
- `linear_key_gate`
- `gbla_style_all`
- `hybrid_sa_gbla_1to2`

## Stop condition

Promote only if a less symbolic matrix/retrieval probe reproduces the qualitative winner.
