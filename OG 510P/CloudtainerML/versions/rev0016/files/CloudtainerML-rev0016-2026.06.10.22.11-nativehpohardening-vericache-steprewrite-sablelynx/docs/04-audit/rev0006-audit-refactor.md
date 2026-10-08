# Rev0006 audit/refactor note

Refactor goal: make probe outputs discoverable before forcing a single metric schema.

## Added tools

- `tools/probe_dashboard.py`: shallow inventory dashboard over probe JSON files.
- `tools/probe_suite_dashboard.py`: cross-probe highlight extractor with schema-warning metadata.
- `tools/cube_audit.py`: ledger consistency, source/id references, and retired-lane byte scan.

## Known schema debt

Probe outputs are heterogeneous. The next schema target is:

```json
{"probe":"...","config":{},"summary":{"row_count":0},"rows":[],"primary_metric":{"name":"...","direction":"lower|higher"}}
```

This revision deliberately records heterogeneity rather than pretending probes are already comparable.
