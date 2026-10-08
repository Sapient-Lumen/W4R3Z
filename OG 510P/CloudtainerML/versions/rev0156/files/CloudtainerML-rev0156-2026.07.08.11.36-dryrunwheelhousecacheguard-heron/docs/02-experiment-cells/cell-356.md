# CELL-356 — Sparse Index Compiler Report

Priority: **P0**  
Status: audit-refactor-added

## Question

Do hard-gate, block-index, and temporal top-k probes all report exactness plus realized selector/block cost in one place?

## Cheap first run

Run tools/sparse_index_compiler_report.py and check readiness for bridge/gate compiler, block index, and GVR artifacts.

## Metrics

- `artifact_count`
- `fully_ready_count`
- `ready_score`
- `exact_ready`
- `cost_ready`
- `compile_ready`
- `block_index_ready`
- `temporal_topk_ready`

## Required baselines

- `hard_gate_compilation_report`
- `exactness_guard_report`
- `native_probe_audit`

## Stop condition

Sparse index mechanisms cannot be promoted unless exactness and selector/block-cost fields are present.
