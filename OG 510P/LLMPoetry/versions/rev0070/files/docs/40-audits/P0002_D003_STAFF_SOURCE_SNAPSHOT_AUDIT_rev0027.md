# P0002-D003 Staff/Source Snapshot Audit — rev0027

## What changed

`P0002-D002` was cold-reviewed `revise_not_promote`, then superseded by `P0002-D003` / **“Staff Behind the Inspection Office.”** The revision does not promote a poem. It moves the test from a datum-stack poem toward a physical measuring scene: station `8518750`, The Battery, NY; a tide gage and staff; a pier behind the Inspection Office; datum values; observed/predicted extrema; relative sea-level trend; and the failed local attempt to capture a live reading.

## Risk addressed

D002’s core weakness was that it still behaved like a verified table with lyric explanation. D003 answers that by forcing a place-object into the draft: the staff/gage is a fixed local ruler for a moving body. The current risk is now more useful: whether that physical source pressure creates reading pressure, or merely creates a better source card.

## Audit/refactor

New validator: `tools/check_source_snapshots.py`

New schema: `schemas/source_snapshot.schema.json`

New registry: `registries/source_snapshot_registry.json`

The validator checks that current-head source snapshots are present, registered, hash-matched, source-bound, non-claim-limited, connected to current packet facts, and mirrored by source receipts. `tools/check_external_material_pressure.py` now also verifies source-snapshot IDs for the current packet facts.

## Current validation

- External-material pressure: `True` / 271 checks
- Source snapshots: `True` / 168 checks
- D003 metrics: 284 words; 40 nonblank non-heading lines; banlist hits: []

## Limits

- `P0002-D003` is same-turn unjudged and not admitted.
- The source snapshots are lightweight excerpts/runtime receipts, not WACZ captures.
- The local CO-OPS `date=latest` attempt failed at DNS resolution, so no current/live reading is claimed.
- This audit does not claim poem quality.

## Recommended next move

Cold-review D003. The precise question is whether the tide-staff and Inspection Office location convert the NOAA facts into a poem under disclosure, or whether D003 is only a better documented fact-card.
