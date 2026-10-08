# P0002 D004 source-compression audit — rev0028

## What was riskiest

P0002-D003 did not fail because it lacked receipts. It failed because its receipts had begun to dictate the poem's surface. The validator required too many literal source strings, rewarding a reliable but table-forward poem.

## Cold review result

`P0002-D003` is cold-reviewed `revise_not_promote`. It improved on D002 by adding the tide staff / pier / inspection-office object, but it still read too much like a NOAA fact card with lyric bridges.

## Substantive change

`P0002-D004` is the current head. It keeps station `8518750`, the tide gage/staff, Marine Inspection Office, MLLW, selected extrema, NAVD88/STND, and the relative sea-level trend on the surface. The rest of the datum stack stays in `source_material_packet_004.json` as packet-context facts.

## Refactor

`tools/check_external_material_pressure.py` and `tools/check_source_snapshots.py` now support `source_to_surface_policy.mode = anchor_context_compression`. The poem may use fewer surface anchors, but every current packet fact still needs a source receipt and snapshot.

## Non-claims

No poem is admitted. D004 is same-turn unjudged. No current/live NOAA water-level value is claimed; the local latest-data attempt failed at DNS resolution.
