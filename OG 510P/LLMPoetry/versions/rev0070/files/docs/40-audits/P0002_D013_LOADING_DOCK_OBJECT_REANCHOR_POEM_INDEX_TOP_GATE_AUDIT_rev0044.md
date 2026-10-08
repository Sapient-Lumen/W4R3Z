# P0002-D013 loading-dock object reanchor / poem-index top gate audit — rev0044

Current head: `P0002-D013` (`The Disk in the Loading Dock`).

## Substantive finding

`P0002-D012` was cold-reviewed as `revise_not_promote`. It repaired D011's generic-harbor drift by adding Broadway / State Street / Coast Guard route specificity, but it still risked reading like directions plus abstract lyric closure.

`P0002-D013` shifts the pressure to a smaller NOAA benchmark object: a tidal station disk set in a concrete loading dock near a blue brick guard house, while retaining the Station Datum / first tide staff pressure and the no-live-value runtime gap.

## Audit finding

`registries/poem_index.json` had a split-surface drift class: the P0002 row could be current while top-level `current_head` and `current_revision` still pointed backward. `tools/check_release_surfaces.py` now checks those top-level fields directly.

## Boundaries

D013 is same-turn unjudged, not admitted, not evidence-ready, not an anthology candidate, not a reader response, and not a live NOAA water-level value claim. P0002-D010 candidate handoff remains preserved separately.
