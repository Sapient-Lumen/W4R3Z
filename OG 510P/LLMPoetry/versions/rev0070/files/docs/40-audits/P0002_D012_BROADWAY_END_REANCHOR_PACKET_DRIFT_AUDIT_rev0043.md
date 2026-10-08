# P0002-D012 Broadway-End Re-anchor / Packet Drift Audit — rev0043

Current head: `P0002-D012`  
Previous head: `P0002-D011`  
Timestamp: 2026-06-16T23:04:00-04:00

## Substantive finding

`P0002-D011` was cold-reviewed `revise_not_promote`. It made a real subtraction from D010, but it also drifted toward generic harbor realism. The strongest hinge stayed `No value came back. / Water did.`, but too much surrounding atmosphere could have belonged to any waterfront poem.

`P0002-D012` uses a more resistant source route: Broadway ends at The Battery, State Street turns toward the U.S. Coast Guard Inspection Office, and the tide gage/staff are on the pier behind the office. It remains same-turn unjudged, not a candidate, not admitted, not evidence-ready, not reader evidence, and not a live water-level claim.

## Refactor finding

Four drift classes were repaired:

1. `registries/poem_index.json` had allowed `source_material_packet` and `external_material_packet` to disagree. `tools/check_release_surfaces.py` now blocks stale `external_material_packet` values.
2. `REVISION_RECEIPT.json` had lagged behind packaged state. `tools/check_release_surfaces.py` now checks the receipt revision, artifact, and current head against `STATE.json`.
3. The D010 reader/candidate gates still assumed the preserved D010 handoff was the active current head. The gates now permit D010 reader surfaces to remain historical after D011/D012 while still blocking fabricated response evidence.
4. Several compact prose surfaces still described D011 as current after D012 had become current. `tools/check_release_surfaces.py` now blocks stale current-head prose in release/status summaries.

## Non-claim

This audit is not poem-quality evidence and not a reader response.
