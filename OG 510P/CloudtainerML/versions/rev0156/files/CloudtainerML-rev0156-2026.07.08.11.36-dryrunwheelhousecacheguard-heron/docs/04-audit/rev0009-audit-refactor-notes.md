# Rev0009 audit/refactor notes

## Added refactor tools

- `tools/cache_probe_report.py` groups existing probe outputs by family and extracts compact winners/primary-metric readiness.
- `tools/surprise_audit.py` writes `SURPRISE-LEDGER.md/json` and audit copies.

## Structure changes

- Added `SURPRISE-LEDGER.md` and `SURPRISE-LEDGER.json` as root porch files.
- Added three runnable probes under `experiments/`.
- Updated the baby datacube axes with `mechanism_role` so compression mechanisms are not conflated.
- Added rev0009 research notes and cell notes.

## Known cleanup queue

- Older probes still need uniform `summary.primary_metric` patches.
- Some dashboards summarize heterogeneous metrics; keep them as navigation/report surfaces, not leaderboards.
- The next refactor should add per-family graph specs.
