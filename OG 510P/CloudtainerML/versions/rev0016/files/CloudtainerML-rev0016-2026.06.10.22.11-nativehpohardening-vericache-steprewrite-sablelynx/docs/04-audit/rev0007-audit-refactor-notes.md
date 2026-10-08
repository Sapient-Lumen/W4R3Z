# Rev0007 audit/refactor notes

- Added revision-aware output goals for dashboard and audit scripts.
- Promoted `tools/probe_suite_dashboard.py` as the main probe overview; shallow `tools/probe_dashboard.py` remains as a discoverability view.
- Added three probes with consistent `probe`, `purpose`, `config`, `summary`, `csv`, and truncated `rows` fields.
- Regenerated registries and experiment-cell CSVs.
- Remaining refactor debt: every probe should expose a declared `primary_metric` block so dashboards stop guessing the highlight.
