# P0002 external material pressure audit — rev0025

## Purpose

Rev0025 chooses the riskiest unfinished thread from rev0024: stop adding P0001 receipt layers and create a materially resistant `P0002` fork.

## Substantive change

`P0002-D001` now exists as `poems/P0002/draft_001.md`. Its source packet is `poems/P0002/material/source_material_packet_001.json`.

The draft is bound to NOAA CO-OPS station/datum material for station `8518750`, The Battery, NY. The required visible pressure is narrow: station ID/name, MLLW reference frame, accepted date, feet, epoch `1983–2001`, datum `MLLW`, extrema values/dates, mean range, and a compressed MLLW definition.

## Refactor/audit change

`tools/check_surface_freshness.py` was refactored so the current head is read from `SURFACE_STATUS.json`/`proof_status.json` instead of hard-coded as `P0001-D010`. This corrects a future-drift risk: after P0002 starts, the old freshness checker could have made the archive look current while still centering P0001.

New validator: `tools/check_external_material_pressure.py`.

New schema: `schemas/external_material_packet.schema.json`.

New make target: `make external-material`.

## What is still not done

P0002-D001 is not cold-reviewed in this turn. It is not promoted, not evidence-ready, and not a live-data poem. The next turn should ask whether the NOAA facts create reading pressure or whether this is only a clean fact-card poem.

## Non-claim

This audit verifies forward motion, source traceability, and validator coverage. It is not a literary-quality review.
