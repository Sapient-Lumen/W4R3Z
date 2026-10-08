# CELL-351 — Hard Gate Compilation Report

Priority: **P0**  
Status: audit-refactor-added

## Question

Do sparse/gate/bridge/routing probes explicitly distinguish soft training, hard deployment, exactness, and selected-edge cost?

## Cheap first run

Run tools/hard_gate_compilation_report.py on current revision artifacts. Verify sparse/gate/bridge/routing outputs include hard deployment, exactness, and selected-edge cost fields.

## Metrics

- `artifact_count`
- `compile_ready_count`
- `fully_ready_count`
- `ready_score`

## Stop condition

Promotion candidates involving sparse gates must be compile-ready or explicitly marked symbolic only.
