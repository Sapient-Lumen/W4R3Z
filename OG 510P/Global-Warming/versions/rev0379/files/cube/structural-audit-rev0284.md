# Structural audit — rev0284

Created: 2026-05-25T18:35:00-04:00

## Scope

This audit reviewed the rev0283 cube after adding rev0284 assurance and accountability material. It focused on schema/index drift, route resolution, source resolution, CSV parseability, source-use reconciliation, and the growing width of `cube/index.csv`.

## Findings

- `cube/index.csv` has grown to 429 rows and 120 columns. The wide table remains useful for scanning, but it is now too wide to be the only durable representation.
- The rev0284 refactor therefore keeps the wide index and adds normalized `file-core`, `tag-edge`, `route-edge`, `source-edge`, and `field-coverage` tables.
- Registered source IDs currently used in numbered files: 770.
- Registered source IDs with no numbered-file use after rebuild: 0.
- Unresolved source citations after rebuild: 0.
- Unresolved numeric route targets after rebuild: 0.

## New normalized artifacts

- `cube/file-core.csv` — one row per numbered file.
- `cube/tag-edge-table.csv` — many-to-many tag relationships.
- `cube/route-edge-table.csv` — numeric file-to-file routes with resolved/unresolved status.
- `cube/source-edge-table.csv` — file-to-source citation/provenance edges.
- `cube/field-coverage-dashboard.csv` — column coverage and sparsity class for every index field.

## Refactor recommendation

Future revisions should add a new wide-index column only when a query or validation rule requires it. Otherwise, prefer normalized edge tables or specialized registers. The archive should treat the wide index as a compatibility view, not the only cube.

## Rev0284 assurance recommendation

High-stakes service floors should be maturity-capped unless they have source provenance, internal-control posture, corrective-action closure, independent challenge/redress, civil-rights and language-access gates, workforce competency/succession evidence, and a scoped resilience assurance case.
