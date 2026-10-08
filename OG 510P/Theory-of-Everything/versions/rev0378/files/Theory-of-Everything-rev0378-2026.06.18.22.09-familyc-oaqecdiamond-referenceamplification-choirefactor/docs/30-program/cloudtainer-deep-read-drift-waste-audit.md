# Cloudtainer deep-read drift and waste audit

## Scope

This revision treats the extracted release tree as the working cloudtainer: a self-contained carrier with source ledgers, generated mirrors, release identity, lint, schema validation, and package smoke checks. The audit asked whether the datacube is still internally navigable, what is missing, what should change, and where work has gone wrong or become wasteful.

## Bottom line

The archive is healthier than a loose notes folder: `make lint` passed before this revision, registered JSON schemas validate, release packaging is deterministic, JSON source refs resolve to the bibliography, and the rev0344 equivalence/fifth-force/weak-field sources are correctly treated as denominator pressure rather than route support. The serious failure was semantic current-head drift: several human-facing surfaces named rev0343 or even rev0338 as current while the manifest and stable current-linked line named rev0344. The generated restart mirror also faithfully carried stale `context-pack.json` posture, proving that mirror parity can preserve bad source truth when source-currentness is not linted.

## What had gone wrong

- `README.md`, `ARCHIVE_INDEX.md`, `docs/00-meta/trajectory-map.md`, and `docs/40-model/current-head-control-router.md` had stale first update headings even though their first `Current linked revision` lines pointed at rev0344.
- `START_HERE.md` opened with `Current head: rev0343`, while its generated mirror inherited `rev0338 is the current linked revision` from `context-pack.json`.
- `SURFACE-STATUS.json` still described the followthrough state as `empty-after-lorentz-cpt-sme-denominator-audit`, a rev0342-era posture incompatible with the rev0344 package.
- Three ledgers carried `rev0343_equivalence_principle_source_role_note` keys for equivalence-principle content that belongs to the rev0344 source-role pass.

## Missing controls

1. A typed `source_role` enum is needed so `acquired_support`, `denominator_pressure`, `forecast_runway`, `operational_status`, and `metadata_wrapper` cannot be swapped by prose.
2. Fresh frontier-source receipts should record `checked_at`, `public_status`, `source_role`, and `no_promotion_disposition` for MICROSCOPE, ACES/PHARAO, atom-interferometer WEP, torsion-balance, and inverse-square/fifth-force records.
3. First-heading and current-posture currentness should be linted, not just the first stable `Current linked revision` line. This revision adds that lint.
4. JSON schemas remain too permissive in many ledgers. Revision-specific note fields can accumulate because many schemas allow additional properties.
5. Generated and manually curated navigation surfaces need a compression boundary: current-head surfaces should not replay old current-head claims as if they still had present authority.

## Waste and overgrowth

The archive has useful redundancy for safety, but some redundancy has turned into cost. Many route-support ledgers repeat the same small route row structure with long residual-cap prose. Per-revision JSON keys such as `rev0340_*`, `rev0342_*`, `rev0343_*`, and `rev0344_*` have become a second informal schema. Large generated artifacts such as the authority dependency graph are valuable for replay, but should be explicitly treated as generated/checksummed products so humans do not need to read them as primary narrative. The highest-leverage compression path is not deletion; it is moving repeated prose into typed events and generated summaries.

## Scientific/source-role readout

The external source posture remains conservative. MICROSCOPE, torsion-balance, atom-interferometer WEP, ACES/PHARAO, and short-range inverse-square/fifth-force records are excellent denominator pressure for weak-field, equivalence, redshift, and fifth-force claims. They do not identify a candidate-native route, do not provide acquired ToE support, and do not promote any route. Their proper use in this datacube is to raise the burden of recovery and to prevent weak or anomalous wording from sneaking into route state.

## Correction made in rev0345

rev0345 repairs the current-head/front-matter drift, adds currentness checks to lint, corrects stale equivalence-principle note keys, updates context and surface status, and opens `FOLLOWTHROUGH-QUEUE.json` with five active repair items. The queue is archive-control work: source-role typing, freshness receipts, schema hardening, navigation pruning, and compression.
