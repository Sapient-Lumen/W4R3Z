# Surface contracts and metadata drift audit

Status: canonical metadata-control surface.  
Revision introduced: rev0228; rev0230 overlay: primary/mentioned tag separation.  
Owner: archive maintainer.  
Related artifacts: `CUBE_SURFACE_CONTRACTS.json`, `SURFACES.json`, `tools/gen_surface_map.py`, `tools/check_surfaces.py`, `tools/check_surface_contracts.py`, `tools/check_surface_priority_curation.py`, `CUBE_SCHEMA_REGISTRY.json`, `CUBE_TOOLCHAIN_REGISTRY.json`.  
Live boundary: this surface does not close `FT-0181`, does not upgrade examples into real pilot evidence, and does not prove learning, safety, access, workload, or compliance claims.

## Why this exists

The cube now has strong registries for tools, schemas, branch families, and release controls.  The next drift risk is subtler: canonical Markdown surfaces are classified into `SURFACES.json` by a rule-assisted generator.  That generator is useful for full-corpus coverage, but it can overreact to incidental words in a surface.  A metadata/refactor page that mentions exams, services, evidence, or imports may inherit tags that describe nearby prose rather than the surface's primary purpose.

rev0228 therefore adds a surface-contract registry.  A contract says: for this canonical surface, these metadata fields are expected and these tags are forbidden.  The contract does not replace `SURFACES.json`; it constrains the most important rows so generated metadata remains useful as navigation infrastructure instead of becoming another loose index.

## What the contract checks

Each contract row binds one Markdown path to:

- expected `type`, `lifecycle`, `owner`, `authority`, and `portability`;
- required evidence-level markers;
- required tags;
- forbidden tags, especially accidental `hot-exam` or `branch-archive` tags on meta/re-entry surfaces;
- required classification quality, usually `human-curated` for canonical re-entry, registry, audit, and control surfaces;
- a closure boundary that says the contract does not close `FT-0181`.

The contract deliberately covers a curated set of canonical surfaces rather than every Markdown file.  Rule-assisted rows are still useful for retrieval.  Decision-grade rows must be contract-backed when they are part of the re-entry path, metadata plane, registry plane, control plane, or real-import readiness plane.

## Refactor made in rev0228

The previous `tools/check_surface_priority_curation.py` carried its own long priority list.  That duplicated curation logic already present in `tools/gen_surface_map.py` and could drift away from future metadata expectations.  rev0228 refactors the priority check so it reads `CUBE_SURFACE_CONTRACTS.json` instead.

The new flow is:

1. `tools/gen_surface_map.py` regenerates `SURFACES.json` for all Markdown files.
2. `tools/check_surfaces.py` proves full Markdown coverage and valid reference fields.
3. `tools/check_surface_contracts.py` proves contract-backed canonical rows carry the expected metadata.
4. `tools/check_surface_priority_curation.py` proves the same contract-backed priority rows are still human-curated and non-empty.


## Rev0230 tag hygiene overlay

Rev0230 keeps `tags` as a backward-compatible union but adds `primary_tags` and `mentioned_tags` to every `SURFACES.json` row. `primary_tags` answer what the surface is. `mentioned_tags` answer what terms appear in it and may help retrieval. Contract checks still read `tags` so older release controls remain stable, while `tools/check_surfaces.py` now proves the new fields are present, list-shaped, subsetted to `tags`, and disjoint from each other.

This is not a new evidence gate. It corrects a retrieval risk found in the rev0230 audit: meta, audit, service, real-import, and branch surfaces can mention the same vocabulary without sharing the same identity.

## Drift classes

| Code | Drift | Required response |
|---|---|---|
| `SCD0` | no drift | accept generated row |
| `SCD1` | harmless retrieval tag | leave rule-assisted row alone |
| `SCD2` | canonical surface inherits irrelevant tag | add or update contract; adjust generator if repeatable |
| `SCD3` | canonical lifecycle/owner/authority drift | fail lint until generator or contract is corrected |
| `SCD4` | branch archive enters first-read path | fail lint; route through branch-family index |
| `SCD5` | metadata implies evidence completion or real import closure | fail lint; restore `FT-0181` boundary |

## No-new-control boundary

This is a refactor control, not a new real-import control.  It is justified because it removes duplicate hardcoded metadata logic and prevents canonical rows from inheriting misleading labels.  It does not reopen the control-saturation posture: new metadata contracts should be added only when a surface is canonical enough that incorrect metadata would mislead a future maintainer, reviewer, or implementer.
