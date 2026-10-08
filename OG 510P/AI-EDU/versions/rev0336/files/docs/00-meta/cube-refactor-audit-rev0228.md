# Cube refactor audit rev0228

Audit target: surface metadata contracts and priority-curation drift.  
Status: maintenance audit.  
Live boundary: this audit does not close `FT-0181`, does not upgrade examples into real pilot evidence, and does not prove service effectiveness.

## Finding

The rev0227 cube was lint-clean, but the metadata plane still had a duplication and drift problem.  `SURFACES.json` was comprehensive, and the toolchain/schema registries were checkable, but priority surface curation still lived in a hardcoded Python list.  Meanwhile, newer meta surfaces could inherit generated tags from incidental prose rather than from their primary role.

The most visible symptom was not a broken link or invalid JSON.  It was classification ambiguity: a registry or audit surface may mention exams, services, evidence, and imports while actually functioning as metadata infrastructure.  If those incidental terms become the row's practical identity, later search and handoff work can over-weight the wrong part of the cube.

## Refactor performed

rev0228 adds `CUBE_SURFACE_CONTRACTS.json` and makes it the contract-backed source for canonical surface metadata expectations.  The pass also:

- adds `schemas/surface-contracts.schema.json`;
- adds `tools/check_surface_contracts.py`;
- refactors `tools/check_surface_priority_curation.py` so it reads the contract registry instead of maintaining a second hardcoded priority list;
- updates `tools/gen_surface_map.py` so meta/registry/refactor surfaces do not accidentally carry `hot-exam` tags merely because their prose names the live gate;
- registers the new root-control JSON in `CUBE_SCHEMA_REGISTRY.json`;
- registers the new validator in `CUBE_TOOLCHAIN_REGISTRY.json`;
- updates the surface-map overview and re-entry navigation so future maintainers know where metadata contracts live.

## What did not change

The branch-history files were not moved.  The real-import gate was not closed.  No example service record was promoted into real evidence.  The release-candidate posture remains ready-but-not-closed.

## Residual risk

The surface contracts cover canonical rows, not every Markdown file.  That is intentional.  Full-corpus metadata is still rule-assisted, and branch-history retrieval remains a separate layer under `BRANCH_FAMILY_INDEX.json`.  A future refactor may add more contracts if a newly canonical surface becomes part of the first-read, registry, release, or real-import path.

## Result

The metadata plane is now less dependent on word-frequency inference and less duplicated across tools.  `SURFACES.json` remains the comprehensive map; `CUBE_SURFACE_CONTRACTS.json` now marks the rows whose meaning must not drift silently.
