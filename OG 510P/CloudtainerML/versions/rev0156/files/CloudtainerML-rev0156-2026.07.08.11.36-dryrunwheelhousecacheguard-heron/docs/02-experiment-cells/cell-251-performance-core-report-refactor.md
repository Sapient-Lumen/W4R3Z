# CELL-251 — Performance Core Report Refactor

Priority: **P0**  
Status: **audit-refactor**

## Cheap first run

tools/performance_core_report.py writes REV0022_PERFORMANCE_CORE_REPORT.json/md under artifacts/dashboard.

## Metrics

- p0_cells
- sidewing_p0_fraction
- current_native_smoke_outputs
- performance probe coverage

## Required baselines

- charter_focus_audit
- p0_integrity_report
- native_probe_index

## Stop condition

If side-wing-ish P0 fraction grows, reset docs before adding more security/trust probes.
