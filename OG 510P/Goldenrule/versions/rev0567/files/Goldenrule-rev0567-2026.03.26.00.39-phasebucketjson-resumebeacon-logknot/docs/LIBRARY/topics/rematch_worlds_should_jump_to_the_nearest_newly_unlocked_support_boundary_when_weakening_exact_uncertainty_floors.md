# Rematch worlds should jump to the nearest newly unlocked support boundary when weakening exact uncertainty floors

## Claim
When a required exact uncertainty floor weakens, the first useful widening repair is not an arbitrary interior dwell. It is the **nearest newly unlocked support boundary**.

## Why this matters
The archive already knew how to react when a stronger floor prunes support: jump left to the nearest surviving boundary. The dual fact is now explicit too:
- from precision singleton `{2}`, weakening one staircase notch should jump first to dwell `8`, the left boundary of the newly recovered neutral band,
- from neutral band `[8,18]`, weakening one staircase notch should jump first to dwell `19`, the left boundary of the newly recovered relaxed suffix,
- so the full current one-notch weaker-floor widening target set compresses to just `{8, 19}`.

That matters because it replaces a search over `25` newly unlocked dwell points with a search over **two exact landing points** whenever the requirement got easier and the implementor wants to reclaim dwell freedom.

## Implementor rule
- If a precision-only requirement weakens into the near-optimal band, target dwell `8` first.
- Do not sweep neutral-band interior dwells `9–18` as first widening repairs; they are dominated on right-shift distance.
- If a near-optimal requirement weakens into the relaxed lane, target dwell `19` first.
- Do not sweep relaxed-suffix interior dwells `20–32` as first widening repairs; they are dominated on right-shift distance.
- If a precision-only deployment relaxes all the way to the lowest saved exact floor, widening still starts at dwell `8`; move on to dwell `19` only if the relaxed suffix itself is desired.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_relaxation_boundary_targets_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_relaxation_boundary_targets_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_floor_relaxation_boundary_targets.py`
