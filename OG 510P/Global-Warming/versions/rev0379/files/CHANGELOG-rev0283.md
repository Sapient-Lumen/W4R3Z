# CHANGELOG — rev0283

Created: 2026-05-25T16:50:00-04:00

## Theme

Adaptive pathways, model governance, portfolio stress, enforceable resilience service levels, unsafe-asset exit, professional duty, and cube refactor.

## Added

- `413` — adaptive pathways with signposts and switching rules.
- `414` — climate-risk model governance, uncertainty, and assumption ledgers.
- `415` — real options, modularity, reversibility, and temporary-measure expiry.
- `416` — maladaptation and lock-in red-team gate.
- `417` — asset-portfolio stress testing and capital-plan crosswalk.
- `418` — resilience service levels in contracts, permits, grants, concessions, and handoffs.
- `419` — unsafe-asset decommissioning, retirement, repurpose, and service replacement.
- `420` — climate-informed professional duty and future-risk disclosure.

## Added cube artifacts

- `cube/adaptive-pathways-and-model-governance-register.csv`
- `cube/portfolio-stress-and-duty-register.csv`
- `cube/cube-data-dictionary.csv`
- `cube/controlled-vocabulary.csv`
- `cube/route-graph.csv`
- `cube/source-use-ledger.csv`
- `cube/validation-rules.json`
- `cube/structural-audit-rev0283.md`

## Updated

- Expanded `cube/schema.json` to 112 fields.
- Expanded `cube/index.csv` to 421 rows.
- Added adaptive-governance rows to interdependency, service-floor, scenario, and query-view cube files.
- Added rev0283 open questions `166`–`173`.
- Updated core thesis, ranked stack, minimum sufficient solution, mature front-door router, readiness scoring, query views, risk-reduction pipeline, and performance-monitoring packets.
- Added sources `S741`–`S755`.

## Refactor

- Created a field dictionary to externalize the 112-column schema.
- Created a controlled-vocabulary seed for enumerated fields and common tag values.
- Extracted numeric `routes_to` relationships into a route graph.
- Extracted source usage into a source-use ledger.
- Added explicit validation rules for future archive builds.

## Validation target

- continuous numbered files `00`–`420`;
- source register continuous through `S755`;
- no unresolved or unused source IDs;
- all numeric routes point to existing numbered files;
- all cube CSVs parse;
- `cube/index.csv` headers match `cube/schema.json` fields;
- ZIP integrity passes.
