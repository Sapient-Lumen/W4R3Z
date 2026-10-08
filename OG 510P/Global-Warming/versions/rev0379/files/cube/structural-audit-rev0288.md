# Structural audit — rev0288

Created: 2026-05-26T03:15:00-04:00

## Summary

Rev0288 is a local-assurance and data-quality refactor. It repairs primary-key defects, normalizes raw dimension/tag edges, completes missing service-floor control-plane templates, and adds a jurisdiction-scoped synthetic local overlay for testing maturity-cap execution.

## Key repairs

- Repaired duplicate `A_ngo` primary key in `cube/actor.csv`; preserved `ngo` as an alias in `cube/actor-alias.csv`.
- Repaired duplicate tag IDs for `actor_tags_ngo`, `equity_lenses_indigenous_communities`, and `domain_tags_cdbg_dr`; preserved raw values in `cube/tag-alias.csv`.
- Added `cube/file-tag-edge-normalized.csv`: 6,575 raw tag edges now resolve to canonical tag IDs.
- Added missing claim/control/evidence/challenge/access/audit/contracting/workforce/materiality/control-test rows for four synthetic service floors.

## Local assurance overlay

The synthetic pilot jurisdiction `J_PILOT_FIXTURE_001` exercises local overlay records for 12 service floors. These rows are marked `synthetic_not_real_world_evidence` and are scored only in local/jurisdiction-scoped tables.

## Validation counts

- Numbered markdown files: 429
- Index rows: 429
- Schema fields: 120
- Sources: 770
- Service floors: 418
- High-stakes service floors: 393
- Claims: 418
- Controls: 2,801
- Global gate evaluations: 5,434
- Local gate evaluations: 5,434
- Data-quality rules: 10
- Referential-integrity checks: 42
- SQLite imports/views: 138

## Validation status

14 / 14 rev0288 validation rules passed.

## Data-quality status

10 / 10 data-quality rules passed.

## Caveat

The local overlay is deliberately synthetic. It demonstrates the shape of local implementation evidence and maturity-cap execution, but it does not assert that any real jurisdiction has implemented those controls.
