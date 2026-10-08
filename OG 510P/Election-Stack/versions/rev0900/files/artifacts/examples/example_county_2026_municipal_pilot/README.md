# Example County 2026 Municipal pilot scenario

**Track:** A / synthetic pilot harness

This directory contains the smallest end-to-end synthetic scenario for the stack. It links existing Example County packets into one operator path so a reviewer can test the public-notice, witness, monitoring, result, incident, and verifier surfaces without browsing the full archive.

## Run

```bash
python3 scripts/check_pilot_readiness.py
python3 tools/example_county_pilot_smoke.py --json
```

## Non-claim

This is synthetic example data only. It is not live election evidence, does not prove any outcome, and does not replace canvass, audit, certification, recount, or court process.

## Files

- `scenario.json` — machine-readable phase map and packet pointers.
- `public-summary.md` — public-language summary that shows how to explain the packet without overstating it.
- `negative-control-report.json` — synthetic expected-failure verifier report for temporary tamper fixtures.
- `public-negative-control-summary.md` — public-safe explanation of expected-failure checks and non-claims.

- `release-maintainer-handoff.json` — generated release-maintenance summary for current synthetic outputs and source-review triage.
- `release-maintainer-handoff.md` — public-safe maintainer handoff summary.
- `source-review-triage.json` / `source-review-triage.csv` — generated source-review pressure summaries under `artifacts/reports/`.
