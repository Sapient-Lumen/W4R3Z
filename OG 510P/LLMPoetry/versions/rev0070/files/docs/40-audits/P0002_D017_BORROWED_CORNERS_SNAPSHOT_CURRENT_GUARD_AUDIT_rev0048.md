# P0002-D017 borrowed-corner reanchor + source-snapshot current-support audit — rev0048

## What was risky

`P0002-D016` improved on D015 by using the NOAA benchmark sheet's dry corner-offset language, but the poem body still behaved like instructions: `To find`, `Start with`, `Take`, and a conclusion that announced `found by corners, / not by tide`.

The substantive risk was another draft that only paraphrased the benchmark sheet more gracefully. The audit risk was a separate currentness problem: source-snapshot records could mark older snapshots as `supports_current_head` without a gate requiring that the true set match the current packet's facts exactly.

## What changed

`P0002-D016` was cold-reviewed `revise_not_promote`.

`P0002-D017` — **Borrowed Corners** — was created as the new current head. It cuts D016's instruction frame and tests the smaller pressure that the benchmark disk has no location of its own; it borrows corners, walls, and dry objects before it can say anything for water.

New validator support:

- `tools/check_external_material_pressure.py` now supports `borrowed_corner_reanchor_policy.mode = benchmark_borrowed_corner_reanchor`.
- `tools/check_source_snapshots.py` now checks `source_snapshot_current_support_exact_current_facts`, requiring the set of snapshots marked `supports_current_head` to equal the set used by the current packet facts.
- `schemas/external_material_packet.schema.json` now declares `borrowed_corner_reanchor_policy`.

## Non-claim

This audit validates trace, source pressure, no-live-value boundary, and current-support drift guards. It is not poem-quality evidence, not admission, not a reader response, and not a live NOAA water-level claim.
