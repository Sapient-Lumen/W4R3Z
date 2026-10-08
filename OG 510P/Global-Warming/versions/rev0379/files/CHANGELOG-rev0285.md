# CHANGELOG — rev0285

Created: 2026-05-26T00:45:00-04:00

## Theme

Normalization completion, canonical IDs, source/route synchronization, and executable assurance-control-plane tables.

## Added cube artifacts

- `cube/file.csv`
- `cube/file-field-value.csv`
- `cube/tag.csv`
- `cube/file-tag-edge.csv`
- `cube/route-edge.csv`
- `cube/source.csv`
- `cube/file-source-edge.csv`
- `cube/service-floor.csv`
- `cube/service-floor-edge.csv`
- `cube/loadcase.csv`
- `cube/metric.csv`
- `cube/observation.csv`
- `cube/jurisdiction.csv`
- `cube/hazard.csv`
- `cube/actor.csv`
- `cube/owner-assignment.csv`
- `cube/claim.csv`
- `cube/evidence-role.csv`
- `cube/claim-challenge.csv`
- `cube/materiality-register.csv`
- `cube/evidence-item.csv`
- `cube/claim-evidence-edge.csv`
- `cube/control.csv`
- `cube/control-test.csv`
- `cube/corrective-action.csv`
- `cube/audit-redress.csv`
- `cube/access-test.csv`
- `cube/workforce-role.csv`
- `cube/contracting-process.csv`
- `cube/maturity-cap-rule.csv`
- `cube/publication-control.csv`
- `cube/cube-control-plane-register.csv`
- `cube/validation-report-rev0285.csv`
- `cube/validation-report-rev0285.json`
- `cube/structural-audit-rev0285.md`

## Changed

- Added negative-evidence challenge paths and failure-materiality triage so claims can be refuted, qualified, stale-dated, contested, and prioritized before maturity is granted.

- Updated `cube/schema.json` to `rev0285` and expanded `object_type` values to match observed archive metadata plus future control-plane object types.
- Regenerated `cube/index.csv`, `cube/file-core.csv`, `cube/tag-edge-table.csv`, `cube/route-edge-table.csv`, `cube/route-graph.csv`, `cube/source-edge-table.csv`, `cube/source-use-ledger.csv`, and `cube/field-coverage-dashboard.csv`.
- Rewrote numbered-file YAML front matter where needed so ids, routes, and source ids are canonical and synchronized.
- Replaced the minimal controlled-vocabulary stub with a taxonomy-style controlled vocabulary while retaining backward-compatible first columns.
- Added query-view rows for maturity caps, claims without evidence, controls without tests, access-test gaps, contracting delivery trace, and source synchronization.
- Added service-floor checklist rows for assured high-stakes floors, open-contracting delivery trace, and civil-rights access path tests.

## Validation target

- continuous numbered files `00`–`428`;
- canonical ids in markdown front matter, index rows, and edge tables;
- body citations, front matter source ids, index source ids, and source-edge rows agree exactly per file;
- route ids resolve exactly and use canonical format;
- object-type vocabulary covers observed values;
- all cube CSVs parse;
- control-plane tables exist and parse;
- high-stakes maturity-cap and publication-control rules exist;
- validation report written to `cube/validation-report-rev0285.csv` and `.json`.
