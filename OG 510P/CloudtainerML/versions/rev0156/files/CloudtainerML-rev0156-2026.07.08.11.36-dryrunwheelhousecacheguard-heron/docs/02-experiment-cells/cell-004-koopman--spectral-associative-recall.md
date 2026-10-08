# CELL-004 — Koopman / Spectral Associative Recall
Priority: `P0`  
Status: `candidate`
## Question
Can constant-memory spectral sufficient statistics preserve content-addressed key-value recall where additive recurrence fails?
## Sources
- `SRC-0005` Echo: KV-Cache-Free Associative Recall with Spectral Koopman Operators — https://arxiv.org/abs/2605.06997

## Cheap first run
Implement small SKA-like memory using kernel/ridge spectral summaries; compare with attention oracle, additive linear attention, delta-rule memory, and fixed hidden state.

## Baselines
- simplest heuristic / random baseline
- matched-memory attention or recurrence baseline
- oracle/full-information baseline where applicable

## Metrics
- exact accuracy or loss
- memory bytes / state size
- runtime
- extrapolation length
- failure-mode taxonomy
- seed variance

## Falsifier / demotion rule
If spectral memory only wins when rank is effectively full cache, mark as too expensive.
