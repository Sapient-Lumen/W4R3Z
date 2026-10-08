# P0002-D005 zero-choice / surface-burden audit — rev0029

## Finding

P0002-D004 was stronger than earlier P0002 drafts, but still too explanatory. The new risk was not missing source accountability; it was surface burden. A source-bound poem can fail by making the reader carry the source table instead of a poetic pressure.

## Substantive change

D005 keeps the staff and Marine Inspection Office, but its central engine is the reference-frame conflict: NOAA station-home material gives `8.99 above MHHW`, while the datum page gives `14.04 above MLLW`. The water is not the difference; the chosen zero is.

## Refactor

`tools/check_external_material_pressure.py` now supports `surface_burden_policy.mode = poem_body_source_burden_cap`. The checker extracts the `## Poem` body separately from `## Disclosure`, caps numeric tokens and digit-bearing lines in the poem body, blocks NOAA/source-table prose from the body, and still requires all packet facts to carry receipts/snapshots.

## Non-claim

This audit verifies source traceability and surface-burden discipline only. It does not promote D005 and does not claim poem quality.
