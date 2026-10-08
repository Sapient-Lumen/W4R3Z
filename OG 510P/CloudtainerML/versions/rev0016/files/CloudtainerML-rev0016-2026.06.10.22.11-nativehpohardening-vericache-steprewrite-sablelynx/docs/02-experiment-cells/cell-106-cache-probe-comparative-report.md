# CELL-106: Cache Probe Comparative Report

Priority: **P0**
Idea: `IDEA-0118`
Status: **candidate-with-runnable-refactor**

## Cheap first run

Runnable refactor exists in tools/cache_probe_report.py; writes REV0009_CACHE_PROBE_REPORT.* under artifacts/dashboard/.

## Required baselines

- existing probe_metric_index
- manual inspection

## Metrics

- schema_ready_count
- family coverage
- compact winners extracted

## Stop / demote condition

If the report duplicates metric_index without reducing comparison friction, merge/delete it.
