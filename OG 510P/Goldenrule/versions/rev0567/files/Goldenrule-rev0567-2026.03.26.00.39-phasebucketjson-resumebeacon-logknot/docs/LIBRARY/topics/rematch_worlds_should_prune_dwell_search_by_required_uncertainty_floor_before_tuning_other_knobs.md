# Rematch worlds should prune dwell search by required uncertainty floor before tuning other knobs

## Claim
The current exact compact repeat-sidecar uncertainty menu is now structured enough that implementors should prune dwell search directly from the **required worst-case preserved-gain floor** before they spend time tuning caps, checkpoints, or tolerance.

The saved exact menu implies a three-cliff dwell-support ladder:
- for required floors in `[0, 0.870482]`, the live exact dwell support is `{2} ∪ [8, 32]`,
- for required floors in `(0.870482, 0.980481]`, the live exact dwell support shrinks to `{2} ∪ [8, 18]`,
- for required floors in `(0.980481, 0.999822]`, the live exact dwell support collapses to `{2}`,
- and above `0.999822` the current exact menu has no certified dwell support at all.

## Why this matters
The archive already knew that the exact uncertainty menu has three tiers and that dwell `3–7` is a dead zone.
But an inheritor often starts from a preserved-gain requirement, not from a tier label.

That makes the guarantee-conditioned dwell support more useful than the raw tier names:
- once the required floor rises above `0.870482`, the relaxed dwell suffix `19–32` is gone and should not be retuned,
- once the floor rises above `0.980481`, the continuous non-fragile band `8–18` disappears as well,
- and once the floor rises above `0.999822`, no current exact dwell remains.

So stronger guarantees are not merely more expensive in cap and checkpoints.
They also leave **less legal dwell space**.
That means future retuning work should start by shrinking the dwell search region from the floor requirement itself.

## Implementor rule
- If the floor requirement is at most `0.870482`, search only on `{2} ∪ [8, 32]`.
- If the floor requirement is above `0.870482` but at most `0.980481`, search only on `{2} ∪ [8, 18]`.
- If the floor requirement is above `0.980481` but at most `0.999822`, search only at dwell `2`.
- If the floor requirement exceeds `0.999822`, do not retune dwell inside the current exact menu; either weaken the requirement or generate new frontier evidence.
- Keep the internal exact gap `[3, 7]` in mind even when the floor is loose: the widest current exact menu is still not continuous from dwell `2` upward.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_conditioned_dwell_support_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_conditioned_dwell_support_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_floor_conditioned_dwell_support.py`
