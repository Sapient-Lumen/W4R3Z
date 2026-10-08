# P0002-D006 zero-witness / revision-delta audit — rev0030

Current head: **P0002-D006 — Zero Has a Witness**.

## What changed

`P0002-D005` was cold-reviewed `revise_not_promote`. Its problem was not missing source traceability; it was a literary failure: the poem still explained the datum problem before it enacted it.

`P0002-D006` keeps the physical pressure behind the Marine Inspection Office and reduces the source surface to a smaller witness/testimony conflict. The body no longer begins with station metadata, drops the trend line, drops the MHHW station-home contrast, and uses the same observed high under two NOAA datum frames: `14.04` under MLLW and `11.27` under NAVD88.

## Refactor

`tools/check_external_material_pressure.py` now recognizes `revision_delta_policy.mode = previous_head_surface_compression_delta`. This gate checks that the current poem body has fewer numeric source tokens than the previous head, remains under a current numeric cap, does not begin with forbidden station metadata, and excludes specific D005 fact-card phrases.

This does not prove poem quality. It only prevents the validator from rewarding a successor draft that preserves source coverage while reverting to fact rows.

## Limits

No poem is admitted. `P0002-D006` is same-turn unjudged. The local NOAA CO-OPS `date=latest` pull failed at DNS resolution, so no current/live water-level value is captured or inferred.
