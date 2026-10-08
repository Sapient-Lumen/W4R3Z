# meta-0456 — Food/nutrition continuity and source-crosscheck guard note

This maintenance note records the rev0755 change set.

## What changed

- Added notes 944 and 945 for SNAP, WIC, child nutrition, Summer EBT, D-SNAP, EBT theft/security, retailer access, disaster replacement, and food-security outcome continuity.
- Added `metadata/food_nutrition_tests.json`, `schema/food_nutrition_tests.schema.json`, and generated `FOOD_NUTRITION_TESTS.*` through the common matrix builder.
- Added food/nutrition source keys, source-health rows, claims, a case-packet entry, and a repaired gap-ledger entry for the food/nutrition assistance continuity domain.
- Refactored `tools/lint_archive.py` so current-revision note metadata source keys and source-catalog source groups must match exactly.

## Governing rule

**No food security by benefit row.**

## Audit note

The guard is intentionally narrow. It does not demand a historical source-catalog rewrite. It catches the forward failure mode created by rapid substantive packets: a current note could previously carry one set of source keys in metadata and a different set in the source catalog while still passing basic existence checks.
