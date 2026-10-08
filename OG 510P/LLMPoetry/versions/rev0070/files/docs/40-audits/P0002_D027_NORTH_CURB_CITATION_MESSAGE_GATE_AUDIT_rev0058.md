# P0002-D027 North-Curb Reanchor / Citation Message Gate Audit — rev0058

## Scope

This revision cold-reviews `P0002-D026`, drafts `P0002-D027`, and tightens release citation-message checking.

## Literary finding

D026 found a genuinely strange benchmark detail: a horizontal line on a vertical copper bolt. But it explained that strangeness too cleanly. D027 therefore moves one ring outward to the dry address pressure on the NOAA sheet: north of the north curb of Bridge Street and above the sidewalk, while the staff and water are elsewhere.

## New draft

Current head: `P0002-D027`  
Draft: `poems/P0002/draft_027.md`  
Packet: `poems/P0002/material/source_material_packet_027.json`

D027 is same-turn unjudged and makes no quality claim.

## Audit/refactor

The concrete drift fault found in the incoming cube was `CITATION.cff`. It had the correct title/version surface for rev0057 but its `message` field still said: `Cite this datacube revision as rev0056; current head P0002-D025.`

That is a release-facing lie in miniature. A future citation export could point to the wrong revision/head even while `make validate` passed. Rev0058 fixes the data and strengthens `tools/check_release_surfaces.py` so `CITATION.cff` message text must explicitly name the current revision and current head and must not contain stale `current head P0002-D###` claims.

Changed validators:

- `tools/check_release_surfaces.py`
- `tools/check_external_material_pressure.py`
- `schemas/external_material_packet.schema.json`

## Non-claim

This audit is traceability and drift control only. It is not admission, reader evidence, or poem quality evidence.
