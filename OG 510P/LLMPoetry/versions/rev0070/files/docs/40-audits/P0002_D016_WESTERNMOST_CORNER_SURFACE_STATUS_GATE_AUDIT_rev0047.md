# P0002-D016 westernmost-corner reanchor and SURFACE_STATUS gate audit — rev0047

## Substantive action

`P0002-D015` was cold-reviewed `revise_not_promote`. The review found that D015's above-ground pressure was real, but the draft turned it into thesis and aphorism too early. `P0002-D016` / **The Westernmost Corner** re-anchors in the NOAA benchmark sheet's dry location syntax: Coast Guard Building, southwest corner, blue brick guard house, westernmost corner, south corner, concrete, above ground.

## New risk

D016 may fail by becoming another set of directions, just at smaller scale. The validator guard therefore caps D012-style route/direction words while requiring corner-offset terms.

## Refactor/audit

The audit found a compact-surface fault in the source package: `SURFACE_STATUS.json` had a fresh `current_head` but stale D012-era `non_claim`, `previous_head`, `previous_head_review`, and `updated_at` values. `tools/check_surface_freshness.py` now blocks that class of drift by checking `SURFACE_STATUS.updated_at`, status, non-claim, next action, previous head, and previous-head review against `STATE.json`.

## Non-claim

This audit validates source pressure, drift repair, and no-live-value boundaries. It does not claim poem quality, admission, reader evidence, or a current NOAA water-level value.
