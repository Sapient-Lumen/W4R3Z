# CELL-059 — Probe Dashboard Refactor

Priority: P1

Status: active-refactor

Source IDs: SRC-0109, SRC-0110

## Cheap first run

Read all probe smoke CSVs and JSONs; emit a dashboard MD/HTML/CSV/JSON.

## Baselines

- manual per-probe notes
- raw CSV inspection

## Metrics

- probe count
- rows
- metric coverage
- categorical hint coverage

## Stop condition

If dashboard cannot summarize heterogeneous probes usefully, turn it into an index only.
