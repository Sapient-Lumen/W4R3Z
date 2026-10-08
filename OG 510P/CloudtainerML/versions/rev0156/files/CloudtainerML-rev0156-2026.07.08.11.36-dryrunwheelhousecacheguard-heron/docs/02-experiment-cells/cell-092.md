# CELL-092 — IntentKV Cross-Turn Pruning Probe

Priority: **P0**  
Status: **runnable**  
Idea: `IDEA-0092`  
Sources: SRC-0154

## Cheap first run

Run intent-aware retention over synthetic multi-turn agent sessions.

## Baselines

- full cache
- recency
- current query
- session QueryMemory
- intentkv toy
- slotmap toy
- oracle critical

## Metrics

- critical_retention
- stale_retention
- intent_purity
- answer_error_proxy

## Stop condition

If QueryMemory loses to recency/current-query in buried-tool regimes, redesign memory update.
