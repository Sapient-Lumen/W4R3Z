# P0002-D028 Lower-Than-Expected / Generic Reanchor Gate Audit — rev0059

## Scope

This revision cold-reviews `P0002-D027`, drafts `P0002-D028`, and refactors current-reanchor validation away from one-off per-draft policy blocks.

## Literary finding

D027 improved on D026 by escaping the clean horizontal/vertical paradox, but it remained an address lyric. The phrase `ready for a height / that had to arrive / from somewhere else` explained the relation instead of making the dry mark exert pressure.

D028 therefore shifts to NOAA's Station Datum clause: a fixed base elevation established lower than water is ever expected to reach. The north-curb/copper/sidewalk facts remain, but the visible poem tests the source-defined floor below expected water.

Current head: `P0002-D028`  
Draft: `poems/P0002/draft_028.md`  
Packet: `poems/P0002/material/source_material_packet_028.json`

D028 is same-turn unjudged and makes no quality claim.

## Audit/refactor

The validation risk was maintenance drift. Each recent draft had added a new bespoke `*_reanchor_policy` block to `tools/check_external_material_pressure.py`. That kept the source pressure check alive, but it also made every future poem movement require new validator code even when the validation shape was the same: prior cold review, required body anchors, forbidden regression phrases, numeric/body caps, and a rationale.

Rev0059 adds a generic optional `current_reanchor_policy.mode = generic_current_reanchor`. D028 uses that policy instead of adding a new one-off lower-expected checker block.

I also found a compact release-surface drift class: `registries/poem_index.json` could carry fresh top-level `current_head` / `current_revision` fields while top-level `current_draft` / `current_packet` fields lagged behind. `tools/check_release_surfaces.py` and `tools/check_surface_freshness.py` now block that class directly.

Changed validators:

- `tools/check_external_material_pressure.py`
- `tools/check_release_surfaces.py`
- `tools/check_surface_freshness.py`
- `schemas/external_material_packet.schema.json`

## Non-claim

This audit is traceability, drift control, and validator-maintenance reduction only. It is not admission, reader evidence, or poem quality evidence.
