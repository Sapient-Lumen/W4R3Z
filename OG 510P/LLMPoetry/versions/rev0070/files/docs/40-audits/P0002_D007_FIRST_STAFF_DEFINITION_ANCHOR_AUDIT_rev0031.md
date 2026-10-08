# P0002-D007 first-staff definition-anchor audit — rev0031

Current head: **P0002-D007 — Zero of the First Staff**  
Created: `2026-06-15T17:42:00-04:00`  
Prior head reviewed: `P0002-D006` → `revise_not_promote`.

## Risk addressed

D006 was the strongest P0002 compression so far, but the witness/oath frame was too ready-made and the MLLW/NAVD88 numbers still operated as a concept demonstration. D007 tests a smaller, riskier source pressure: NOAA's Station Datum definition, especially the zero of the first tide staff installed.

## Substantive change

D007 removes the numeric hinge from the poem body. The body carries `Station Datum`, `first tide staff`, and `Its zero remains`, but no source-table numbers and no NOAA mention. Station identity, datum values, API mechanics, and failed live-pull details remain in packet/snapshot/receipt surfaces.

## Refactor

`tools/check_external_material_pressure.py` now supports `definition_anchor_policy`. The new guard requires source-definition body anchors, blocks the prior witness/oath and numeric contrast phrases, and checks the source snapshot for the definition anchor. This is a regression guard, not a quality claim.

## Non-claim

No poem is admitted. No evidence candidate is created. No live/current NOAA water-level value is claimed.
