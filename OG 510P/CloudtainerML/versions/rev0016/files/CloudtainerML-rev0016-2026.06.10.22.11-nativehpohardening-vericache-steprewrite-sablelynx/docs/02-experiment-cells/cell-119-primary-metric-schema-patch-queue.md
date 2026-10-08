# CELL-119: Primary Metric Schema Patch Queue

Priority: **P0**
Idea: `IDEA-0118`
Status: **active-refactor**

## Cheap first run

Use REV0009 cache report plus metric index to identify older probes missing primary_metric.

## Required baselines

- manual grep
- probe_metric_index only

## Metrics

- missing primary_metric count
- patched artifacts count

## Stop / demote condition

Stop once schema-ready count exceeds 90% or we split by family.
