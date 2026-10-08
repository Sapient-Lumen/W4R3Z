# Rematch worlds should search left, not right, when strengthening exact uncertainty floors from fixed dwell regions

## Claim
When target dwell is already inside a **live** exact uncertainty region and a stronger current exact preserved-gain floor becomes necessary, the repair direction is always **leftward in dwell**. No saved exact floor upgrade is reachable by increasing dwell.

## Why this matters
The archive already records three live exact dwell regions and their fixed-dwell floor ceilings:
- dwell `{2}` -> exact floor ceiling `0.999822`,
- dwell `[8,18]` -> exact floor ceiling `0.980481`,
- dwell `[19,32]` -> exact floor ceiling `0.870482`.

That ceiling structure implies a directional search rule:
- from the relaxed suffix `[19,32]`, any stronger floor above `0.870482` first appears only by jumping **left** into `[8,18]`, with the first stronger support reached at dwell `18`,
- from the neutral band `[8,18]`, any stronger floor above `0.980481` first appears only by collapsing **left** to the singleton dwell `2`,
- and from dwell `{2}`, there is no stronger saved exact floor left anywhere in the current menu.

So once a deployment is already in live support, searching rightward for a stronger exact floor is guaranteed waste.
Rightward dwell changes can change the mode, but they do not unlock a stronger current exact floor.

## Implementor rule
- When a fixed live dwell region must support a stronger exact floor, search left first.
- Treat `25→18` as the representative jump for strengthening the relaxed suffix into the neutral band.
- Treat `13→2` as the representative jump for strengthening the neutral band into the precision singleton.
- If the deployment already sits at dwell `2`, stop retuning for stronger current exact floors and switch to frontier extension work.
- Keep the dead regions (`<2`, `[3,7]`, `>32`) separate from this rule: they still need nearest-live-support repair first.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_upgrade_dwell_jump_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_floor_upgrade_dwell_jump_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_floor_upgrade_dwell_jump.py`
