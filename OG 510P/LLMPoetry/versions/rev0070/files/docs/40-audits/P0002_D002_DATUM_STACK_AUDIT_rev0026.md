# P0002 D002 datum-stack audit — rev0026

Current head: **P0002-D002** (`poems/P0002/draft_002.md`).

## Risk addressed

The riskiest unfinished work after rev0025 was not another registry layer. It was a later-turn cold review of `P0002-D001`, followed by an actual rewrite if the review found that the NOAA material was still decorative.

## Finding

`P0002-D001` escaped P0001's house diction but mostly behaved like a fact card. It carried source facts honestly, yet did not make the competing reference frames do enough work.

## Change

`P0002-D002` keeps literal NOAA strings but stacks them as a conflict: MHHW/MHW/MSL/MLW/MLLW/NAVD88/STND, observed extrema, astronomical extrema, and relative trend. The new pressure question is: `against which zero?`

## Refactor

`tools/check_external_material_pressure.py` now separates historical packet indexing from current-head packet validation. This prevents an old packet from failing merely because a new draft is current, while still requiring the current head to have a packet from the current revision.

## Limits

No poem is admitted. `P0002-D002` is same-turn-unjudged. The trend value is source pressure, not a prophecy, and no live/current water-level reading is claimed.
