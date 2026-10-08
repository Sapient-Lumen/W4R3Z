# CHANGELOG — rev0284

Created: 2026-05-25T18:35:00-04:00

## Theme

Assurance, accountability, civil-rights access, open contracting, workforce competency, resilience assurance cases, and cube normalization.

## Added

- `421` — cube normalization into core, tag, route, source, and field-coverage tables.
- `422` — service-floor claims as internal-control objects.
- `423` — corrective-action closure and continuous improvement.
- `424` — independent audit, redress, and public challenge.
- `425` — open contracting and contractor-performance transparency.
- `426` — civil-rights, language-access, and disability-access readiness gates.
- `427` — workforce competency, credentialing, and succession.
- `428` — resilience assurance cases for high-stakes service floors.

## Added cube artifacts

- `cube/file-core.csv`
- `cube/tag-edge-table.csv`
- `cube/route-edge-table.csv`
- `cube/source-edge-table.csv`
- `cube/field-coverage-dashboard.csv`
- `cube/cube-refactor-and-assurance-register.csv`
- `cube/structural-audit-rev0284.md`

## Updated

- Expanded `cube/schema.json` to 120 fields.
- Expanded `cube/index.csv` to 429 rows.
- Regenerated route and source-use ledgers from current content.
- Added rev0284 open questions `174`–`181`.
- Updated core thesis, ranked stack, minimum sufficient solution, mature front-door router, readiness scoring, query views, and public-ledger packets.
- Added sources `S756`–`S770`.

## Refactor

- Kept `cube/index.csv` as a backward-compatible wide table.
- Added normalized core, tag, route, and source edge tables.
- Added a field-coverage dashboard to expose sparse and specialized schema fields.
- Updated validation rules to check normalized table generation and source-use reconciliation.

## Validation target

- continuous numbered files `00`–`428`;
- source register through `S770`;
- no unresolved or unused source IDs;
- all numeric routes point to existing numbered files;
- all cube CSVs parse;
- `cube/index.csv` headers match `cube/schema.json` fields;
- normalized cube tables parse and cover all indexed files;
- ZIP integrity passes.
