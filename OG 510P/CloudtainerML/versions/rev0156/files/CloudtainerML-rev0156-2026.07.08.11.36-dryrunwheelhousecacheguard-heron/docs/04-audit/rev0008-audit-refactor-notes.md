# rev0008 audit/refactor notes

## Refactor performed

- Added `tools/probe_metric_index.py` to complement the broad probe dashboard.
- New probes emit `summary.primary_metric` so the metric index can compare them with less heuristic guessing.
- Added five new runnable probes under separate experiment folders.
- Added cell notes for CELL-091 through CELL-105.
- Updated smoke validation to require rev0008 probes, metric index, and audit outputs.

## Current schema issue

Older probes are still heterogeneous. That is acceptable for scouting, but the cube now has a clear migration target:

```json
{
  "probe": "name",
  "config": {},
  "rows": [],
  "summary": {
    "row_count": 0,
    "primary_metric": {
      "name": "...",
      "direction": "higher_is_better"
    }
  }
}
```

## Next audit target

Patch the highest-priority old probes to include `summary.primary_metric`, not necessarily rewrite their row schema.
