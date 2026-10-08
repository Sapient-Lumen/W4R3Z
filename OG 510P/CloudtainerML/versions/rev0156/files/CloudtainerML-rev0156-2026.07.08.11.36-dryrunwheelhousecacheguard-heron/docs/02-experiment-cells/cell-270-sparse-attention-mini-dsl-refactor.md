# CELL-270 — Sparse Attention Mini-DSL Refactor

Priority: **P1**  
Status: `audit-design`  
Sources: SRC-0284

## Question

Can CloudtainerML represent sparse attention policies in a common page/block DSL so probes become comparable?

## Cheap first run

Draft page/block sparse-support schema and map existing sparse probes into it.

## Metrics

- `mapped_probe_count`
- `missing_fields`
- `overhead_fields_present`

## Required baselines

- `existing_probe_outputs`
- `manual notes`

## Stop condition

Keep if it reduces comparison friction without hiding probe-specific failure modes.
