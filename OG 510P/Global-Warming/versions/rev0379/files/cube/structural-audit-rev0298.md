# Structural audit — rev0298

Revision rev0298 continues the nuclear-positive policy orientation but moves the proof burden into human capital and institutional competence.

## Refactor target

Rev0297 made nuclear geopolitical resilience explicit. The next weakest plane was people and institutions: workforce planning, craft labor, operator licensing, simulator/requalification capacity, regulator staffing and independence, safety/quality culture, human performance, knowledge retention, emergency planning roles, host-community training benefit and personnel/security-safe publication controls.

## What changed

- Added canon files `474`–`478`.
- Added sources `S864`–`S875`.
- Added 30 nuclear human-capital service floors.
- Added nuclear assurance gates `NG_119`–`NG_136`.
- Rebuilt nuclear gate evaluations, gap backlog, traceability matrix and maturity caps.
- Added worker/regulator/operator/quality-culture normalized tables.
- Refactored route/source/tag edge tables and regenerated the current SQLite mirror.

## Audit findings

The cube now treats nuclear as favored only when the human system can build, license, inspect, operate, maintain, learn from and govern it. The revision intentionally caps maturity at `R2_documented_template_only` until local/project evidence supplies workforce capacity, licensed-operator pipeline, regulator-capacity, quality-culture and knowledge-retention proof.

## Counts

```json
{
  "numbered_markdown_files": 479,
  "index_rows": 479,
  "source_rows": 875,
  "service_floor_rows": 648,
  "nuclear_service_floor_rows": 229,
  "nuclear_assurance_gate_rows": 136,
  "nuclear_gate_evaluation_rows": 31144,
  "nuclear_human_capital_gap_rows": 4122,
  "cube_csv_resources": 277,
  "sqlite_imported_tables": 277,
  "route_edges": 5635,
  "validation_rules_passed": 22,
  "validation_rules_total": 22
}
```

## Caveat

The rev0298 human-capital rows are control-plane templates. They do not certify actual availability of licensed operators, inspectors, craft labor, health physics staff, training seats, regulator capacity, safety culture or knowledge-retention performance for any real project.
