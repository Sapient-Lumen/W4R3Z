# Rematch worlds should jump to the nearest surviving support boundary when strengthening exact uncertainty floors

## Claim
When a fixed **live** dwell region must support a stronger current exact uncertainty floor, the first useful repair target is not an arbitrary interior dwell. It is the **nearest surviving support boundary** after the floor prune.

## Why this matters
The archive already records two facts:
- stronger exact floors from live regions always require **leftward** dwell jumps, and
- floor pruning leaves only a few surviving support components.

Putting those together yields a tighter retuning rule:
- from the relaxed suffix `[19,32]`, requests in `(0.870482, 0.980481]` should jump straight to dwell `18`, the right boundary of the next stronger continuous band,
- from either `[19,32]` or `[8,18]`, requests in `(0.980481, 0.999822]` should jump straight to dwell `2`, the singleton precision support,
- so the full current stronger-floor repair target set compresses to just `{18, 2}`.

That matters because it replaces a search over the current `26` live support points with a search over **two exact landing points** whenever the only problem is that the requested floor got stricter.

## Implementor rule
- If the failed request starts in `[19,32]` and only needs the next stronger non-precision floor, jump to dwell `18` first.
- Do not sweep neutral-band interior dwells `8–17` as first repairs; they are dominated by boundary target `18` on left-shift distance.
- If the failed request needs a floor above `0.980481`, jump straight to dwell `2`.
- Once the deployment already sits at the relevant boundary target, stop local dwell search and re-evaluate the menu or frontier instead.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_upgrade_boundary_targets_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_upgrade_boundary_targets_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_floor_upgrade_boundary_targets.py`
