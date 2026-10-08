# meta-0455 — Water/sanitation continuity and claim/case guard note

This maintenance note records the rev0754 change set.

## What changed

- Added notes 942 and 943 for drinking-water, wastewater, lead, PFAS, boil/do-not-drink/do-not-use advisories, AWIA resilience planning, cyber/OT risk, affordability, emergency water, and sanitation continuity.
- Added `metadata/water_sanitation_tests.json`, `schema/water_sanitation_tests.schema.json`, and generated `WATER_SANITATION_TESTS.*` through the common matrix builder.
- Added water/sanitation source keys, source-health rows, claims, a case-packet entry, and a repaired gap-ledger entry for the water/sanitation continuity domain.
- Refactored `tools/lint_archive.py` so current-revision policy dockets must have a claim-ledger entry and current-revision applied case packets must have both a claim-ledger entry and a case-packet matrix entry.

## Governing rule

**No safe water by compliance row.**

## Audit note

The guard is intentionally small. It does not backfill old notes or add a new registry layer. It catches a concrete future failure mode: a new substantive packet could previously pass with note metadata and sources while failing to enter the claim ledger or applied-case matrix.

