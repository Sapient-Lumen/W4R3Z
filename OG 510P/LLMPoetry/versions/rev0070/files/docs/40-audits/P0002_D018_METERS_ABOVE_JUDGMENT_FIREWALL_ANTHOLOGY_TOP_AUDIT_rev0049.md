# P0002-D018 meters-above / judgment-firewall / anthology-top audit — rev0049

Current head: `P0002-D018` — **In Meters Above**.

## Substantive move

`P0002-D017` was cold-reviewed `revise_not_promote`. D017 improved on D016 by cutting procedural directions, but it still explained its borrowed-corner conceit too neatly. D018 moves the pressure from horizontal location syntax to NOAA's benchmark elevation table: the same dry disk is listed in meters above two water datums.

New current draft: `poems/P0002/draft_018.md`.  
New packet: `poems/P0002/material/source_material_packet_018.json`.

## Refactor/audit

The live audit fault was larger than compact prose drift: `make judgment-firewall` existed but was not wired into the headline validation path, and it failed on several late P0002 cold-review JSONs whose temporal-firewall fields were incomplete. Rev0049 backfills those fields, wires the checker into `tools/llmpoetry_validate.py` and `tools/doctor.py`, and keeps the new D018 same-turn unjudged.

A second compact-surface fault was found in `STATE.json`: `anthology_top_5` preserved historical drafts but could label a non-current draft as `current`. Rev0049 adds `state_anthology_top_current_status_consistent` to `tools/check_surface_freshness.py` so preserved/candidate lists can no longer mislabel the current head.

## Non-claim

D018 is not admitted, not evidence-ready, not an anthology candidate, not a reader response, and not a live NOAA water-level claim.
