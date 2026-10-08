# Structural audit rev0305

Revision rev0305 extends the nuclear-positive datacube with emergency-preparedness maturity caps.

## Counts

- Numbered markdown files: 514
- Index rows: 514
- Registered sources: 966
- Service floors: 856
- Nuclear service floors: 437
- Nuclear assurance gates: 262
- Nuclear gate evaluations: 114494
- Emergency-preparedness gap rows: 7866
- Cube CSV resources: 391
- SQLite rev0305 query-surface tables: 20
- SQLite import failures: 0
- SQLite view failures: 0
- Validation: 26 / 26 passed

## Audit/refactor result

The pro-nuclear policy orientation now includes an emergency-preparedness burden of proof. Nuclear service floors are capped at documented-template maturity unless EPZ assumptions, alerting, evacuation/shelter, KI/medical countermeasure decisions, special-population access, food/water controls, exercises, mutual aid, after-action closure, reentry/recovery and public challenge evidence are localized and current.

## SQLite scope

The rev0305 SQLite mirror imports the current query surfaces and core lookup tables needed for rev0305 views, rather than every historical CSV artifact.

## Publication boundary

The package publishes gate status, evidence classes, scorecards and gap backlogs. It does not publish sensitive evacuation vulnerabilities, security details, personal registries, medical records, route timing, facility weaknesses, or tactical response details.
