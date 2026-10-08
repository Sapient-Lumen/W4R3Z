# Surface map overview

`SURFACES.json` is the archive's machine-readable map. It does not make every document equally canonical. It lets a maintainer ask which surfaces govern a situation, which axes are already covered, and where the archive is repeating itself.

## Current overlay

Rev0332 keeps the surface map comprehensive while making the current hot path more provenance-safe. The teacher/tutor micro-pilot packet generates `DISCOVERY-FIRST-CONTACT.md`, `COACH-PROMPT.md`, `RUN-CHECKLIST.md`, `MEASURE-CARD.md`, and `CYCLE-RUN-SHEET.md`; readiness now checks those run-defining files against generation-time hashes and the owner-plan prompt hash, while the result path still masks exact small-cell counts/rates before any local receipt travels. The map indexes every Markdown surface, while `reentry-navigation-map.md` gives humans a short route through the active canon, `BRANCH_FAMILY_INDEX.json` keeps branch-history tails bounded, and the registry/refactor surfaces explain how validators, schemas, and contract-backed metadata stay aligned.

The map supports these overlays:

- `EV0-EV7` evidence grade and claim strength;
- claim-family separation;
- `AA0-AA6` action-authority ceilings;
- `SEC0-SECX` workflow security posture;
- `PH0-PH6` profile-hardening grammar;
- `MC0-MC5` micro-change classes;
- `TC0-TC5` transition-cost payer posture;
- construct, cognitive-effort, disclosure, and proof mapping;
- service-record import, source-status, custody, and public-redaction paths;
- release candidate, audit, assurance, coverage, refresh, quorum, invariant, dependency, delta, recovery, saturation, maintenance, and claim-language controls;
- compact open-question anchors with archived detail;
- branch-history family lookup through `BRANCH_FAMILY_INDEX.json`;
- lint/toolchain coverage through `CUBE_TOOLCHAIN_REGISTRY.json`;
- JSON/schema coverage through `CUBE_SCHEMA_REGISTRY.json`;
- surface metadata contracts through `CUBE_SURFACE_CONTRACTS.json`;
- `primary_tags` / `mentioned_tags` separation so retrieval can distinguish surface identity from incidental mentions.

## How to use the map

| Question | Look at |
|---|---|
| Are we about to create another branch where an existing compression rule would work? | `BRANCH_FAMILY_INDEX.json`, `lifecycle`, `function`, `risk_family`, `portability` |
| Which documents govern AI services that can take action? | `authority`, `function`, `owner` |
| Which documents touch proof of learning or official records? | `stakes`, `proof_state`, `owner` |
| Which documents touch memory, personalization, or records? | `memory_state`, `risk_family` |
| Which documents are local-only rather than portable? | `portability`, `sector`, `lifecycle` |
| Which live followthrough items still pressure a surface? | `followthrough` |
| Which open questions are concentrated in one branch family? | `open_questions`, `primary_tags`, `mentioned_tags`, `tags` |
| Which high-load rows are ready for decision-grade retrieval? | `classification_quality`, `CUBE_SURFACE_CONTRACTS.json`, `tools/check_surface_contracts.py`, and `tools/check_surface_priority_curation.py` |
| Which tools are validators, generators, or utilities? | `CUBE_TOOLCHAIN_REGISTRY.json`, `tools/check_toolchain_registry.py` |
| Which schema governs a JSON fixture or root control? | `CUBE_SCHEMA_REGISTRY.json`, `tools/check_schema_registry.py` |
| Which canonical metadata fields must not drift? | `CUBE_SURFACE_CONTRACTS.json`, `tools/check_surface_contracts.py` |

## Branch-history treatment

The archive keeps the historical treatment of `first-*`, `portable-*`, and `late-relapse-*` governance surfaces. They remain in place for compatibility, but the surface map now tags them as `branch-archive` and gives them `branch_archive` lifecycle. Use the branch-family index before adding another sibling.

## Backfill quality labels

| Value | Meaning |
|---|---|
| `human-curated` | deliberately classified in this revision or maintained as a priority row |
| `rule-assisted` | generated from path and title heuristics, then linted for required fields |
| `needs-review` | included to prevent invisibility, but should be revisited before using for decisions |

Many older hot-exam continuation documents remain branch surfaces with rule-assisted metadata. That is acceptable for retrieval, but not enough for new decision-grade reuse.

## Lint contract

`tools/check_surfaces.py` verifies that every canonical Markdown file appears exactly once, required fields are present, primary and mentioned tags are well-formed, and followthrough/open-question references resolve.

`tools/check_surface_priority_curation.py` adds a stronger promise for high-load rows. `tools/check_reentry_navigation.py` keeps re-entry documents from re-growing duplicate local link lists.

The validator layer includes `tools/check_branch_family_index.py`, which verifies that branch-history files are covered exactly once by the family index. `tools/check_toolchain_registry.py`, which verifies lint-order coverage, generated-artifact coverage, and utility-tool coverage. `tools/check_schema_registry.py`, which verifies schema coverage, example coverage, root structured-control coverage, validator wiring, and doc-surface coverage. Registered instances validate against their declared schemas.

`tools/check_surface_contracts.py`, which verifies contract-backed surface metadata and refactors `tools/check_surface_priority_curation.py` to read those contracts instead of a second hardcoded priority list. The re-entry checker keeps `context-pack.json` compact and prevents root startup surfaces from re-growing duplicate link lists. The current owner rail remains router-first, and the current pedagogy rail uses the generated run sheet, micro-pilot next-action router, owner-review stop recorder, and suppressed local result receipt recorder before governance-tail retrieval.

This is not a guarantee that every classification is final. It is a brake on the most important rows becoming invisible, duplicated, or purely heuristic.

## Maintenance rule

When adding a document, do one of three things:

1. add it to `SURFACES.json` directly;
2. regenerate the surface map and then hand-tune or contract-curate the row;
3. keep it outside canonical Markdown by placing it in a temporary workspace that is not packaged.

When adding a branch-history document, also regenerate and check `BRANCH_FAMILY_INDEX.json`. When adding or removing a Python tool, update and check `CUBE_TOOLCHAIN_REGISTRY.json`. When adding schemas, JSON examples, or root structured controls, update and check `CUBE_SCHEMA_REGISTRY.json`. Hidden branch surfaces, hidden validators, and hidden JSON fixtures are how the archive becomes ungovernable.
