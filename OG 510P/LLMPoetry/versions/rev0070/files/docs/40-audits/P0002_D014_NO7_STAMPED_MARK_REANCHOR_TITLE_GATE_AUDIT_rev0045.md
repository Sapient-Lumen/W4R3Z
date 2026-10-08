# P0002-D014 NO 7 1975 stamped-mark reanchor / title-gate audit — rev0045

## Decision

`P0002-D013` was cold-reviewed as `revise_not_promote`.

The strongest advance in D013 was the tidal-disk/loading-dock object. The failure was that the object was still asked to deliver a clean conceptual closing claim: water needed something it could be wrong against. That made the benchmark object feel explained rather than endured.

`P0002-D014` therefore moves to the smaller stamped mark on the published NOAA benchmark sheet: `NO 7 1975`. The poem body keeps the disk, concrete loading dock, blue brick guard house, Coast Guard wall, staff, first zero, and no-value/water hinge, while cutting the D013 route opening and conceptual final sentence.

## Current head

- Current head: `P0002-D014`
- Draft: `poems/P0002/draft_014.md`
- Packet: `poems/P0002/material/source_material_packet_014.json`
- Status: same-turn unjudged; not admitted; not evidence-ready; not anthology candidate; not reader response.

## Source pressure

D014 is bound to the NOAA published benchmark sheet for station `8518750`, including the primary benchmark stamping `NO 7 1975`, designation `851 8750 TIDAL 7`, monumentation as a Tidal Station disk, setting classification as Loading dock, and the disk location in a concrete loading dock near the Coast Guard Building and blue brick guard house. It also retains the Station Datum / first tide staff definition, old tide-staff measurement context, and the local no-live-value runtime gap.

## Validator/refactor change

`tools/check_external_material_pressure.py` now supports `stamped_mark_reanchor_policy.mode = benchmark_stamped_mark_reanchor`. The policy allows a tiny numeric exception only for the stamped object name `NO 7 1975`, blocks extra numeric-token drift, requires D013's cold review, requires D014 body strings, and forbids D013's conceptual closure.

## Audit fault corrected

The live drift fault found this turn was not in the poem body. It was in a compact operator surface: after D013 became current, `poems/P0002/INDEX.json` still carried the older D012 title `At the End of Broadway`. That title drift could mislead a future operator even when paths and current-head IDs were fresh.

`tools/check_release_surfaces.py` now extracts the current draft H1 and blocks mismatches against both `poems/P0002/INDEX.json` and the P0002 row in `registries/poem_index.json`.

## Non-claims

D014 is not promoted. No reader response is recorded. No live NOAA water-level value is claimed. The preserved D010 reader handoff remains separate from the current D014 head.
