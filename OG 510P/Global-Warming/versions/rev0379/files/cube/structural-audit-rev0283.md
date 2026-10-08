# Structural audit — rev0283

Created: 2026-05-25T16:50:00-04:00

## Purpose

This audit/refactor pass addresses the datacube's growing width. `cube/index.csv` remains the canonical row index, but rev0283 externalizes its schema, vocabularies, routes, source use, and validation rules so the archive can be tested rather than merely extended.

## Findings from rev0282 intake

- Numbered canon was mechanically clean from `00` to `412`.
- `cube/index.csv` had 413 rows and 104 columns; the width made the schema harder to inspect by eye.
- `cube/schema.json` matched the index header count, but its notes skipped the rev0281 household-function layer and its timestamp lagged later revisions.
- Route relationships were embedded in semicolon-separated cells only; there was no edge list for graph checks.
- Source use could be validated by script but not inspected as a first-class cube artifact.

## Refactor performed

- Added `cube/cube-data-dictionary.csv` with one row per schema field.
- Added `cube/controlled-vocabulary.csv` as a seed controlled vocabulary for enumerated fields and common tags.
- Added `cube/route-graph.csv` with 3470 directed route edges extracted from `routes_to`.
- Added `cube/source-use-ledger.csv` with 755 registered sources and use counts in numbered notes.
- Added `cube/validation-rules.json` to make future archive checks explicit.
- Added two substantive registers for rev0283: adaptive pathway/model governance and portfolio stress/professional duty.

## Rev0283 structural checks

- numbered files: 421
- max numbered file: 420
- missing numbered ids: []
- `cube/index.csv` rows: 421
- `cube/index.csv` columns: 112
- `cube/schema.json` fields: 112
- index/schema header match: True
- source register max id: S755
- source sequence gaps: []
- unresolved source ids in numbered notes: []
- unused registered source ids in numbered notes: []
- nonexistent numeric routes: []
- front-matter defects: []
- H1 defects: []
- citation-footer defects: []
- cube CSV parse errors: []

## Remaining refactor candidates

1. Split `cube/index.csv` into a narrow canonical index plus thematic extension tables once the schema stabilizes above 125 columns.
2. Add a `cube/field-ownership.csv` table naming who maintains each field family.
3. Add route-type semantics beyond the generic `routes_to` edge.
4. Add automated diff artifacts between revisions so additions and schema changes can be reviewed without opening the entire archive.
5. Add freshness scoring to `source-use-ledger.csv` by parsing source year and access status from `sources/register.md`.

## Result

Rev0283 keeps `cube/index.csv` as the canonical query table but makes the cube auditable through normalized companion artifacts.
