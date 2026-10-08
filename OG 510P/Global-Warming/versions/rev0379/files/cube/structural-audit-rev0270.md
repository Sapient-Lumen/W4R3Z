# Structural audit — rev0270

## Scope

This audit covers the archive after adding rev0270 files `308`–`315` and the new cube artifacts.

## Counts

- Top-level numbered Markdown files: 316
- Numbered range: `00`–`315`
- Missing numbered IDs: none
- Cube index rows: 316
- Registered source IDs: 563 (`S1`–`S563`)
- Markdown-used source IDs: 561
- Unresolved source IDs: none
- Unused registered source IDs: [336, 516]
- Nonexistent numeric `routes_to` targets in cube index: none
- Numbered files without canonical citation footer: 0

## Repairs made in rev0270

1. Fixed the rev0269 cube-index route typo in row `306`: `383` now routes to `283`.
2. Expanded the cube schema with explicit dependency-graph fields.
3. Added `cube/interdependency-matrix.csv` so service floors can be read as a dependency graph, not only as prose notes.
4. Added `cube/service-floor-checklist.csv` so readiness can be checked across repeated service-continuity packets.
5. Added eight new canon files only where the gap introduced a new dimension, proof lens, or service floor rather than another instance of an existing pattern.

## Remaining watch items

- `S336` and `S516` remain registered but unused by numbered files; they were inherited from prior revisions and should either be routed to relevant notes or deprecated in a later source-register cleanup.
- Most legacy files still lack per-file YAML front matter. rev0269 and rev0270 provide an external cube index first; full front-matter backfill remains a future mechanical pass.
- The archive now has enough service-continuity files that future additions should generally be admitted through `302` and indexed through the dependency fields rather than added as free-standing prose.

---
Citations point to `sources/register.md`.
