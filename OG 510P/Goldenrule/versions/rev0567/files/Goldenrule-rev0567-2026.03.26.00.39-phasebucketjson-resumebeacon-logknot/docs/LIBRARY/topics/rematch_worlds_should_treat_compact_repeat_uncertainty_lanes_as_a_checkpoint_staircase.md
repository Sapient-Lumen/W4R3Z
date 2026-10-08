# Rematch worlds should treat compact repeat uncertainty lanes as a checkpoint staircase

## Claim
The archive should remember the current repeat-uncertainty operating modes as a **checkpoint staircase**, not only as a rewrite-cap staircase.

## Why this matters
The archive already knows the exact hard-cap ladder: near-exact `0.99` behavior needs cap `11`, near-optimal `0.95` behavior needs cap `5`, and relaxed `0.85` behavior needs cap `3`.

What was missing is the maintenance picture. On the saved frontier, the corresponding finite checkpoint unions are:
- `14` checkpoints for the near-exact dwell-`2` lane,
- `8` checkpoints for the checkpoint-neutral near-optimal dwell-`13` lane,
- and `5` checkpoints for the relaxed dwell-`25` lane.

That means the guarantee ladder is also a maintenance ladder.

The shape is useful:
- moving from `0.95` to `0.85` removes the late-tail checkpoint pair `230/239` and the mid-band checkpoints `24/63`, while introducing only one relaxed-tier marker `56`,
- while moving from `0.95` up to `0.99` adds a cluster of earlier micro-checkpoints `9, 15, 31, 38, 54` plus a unique tail checkpoint `255`.

## Implementor rule
- When maintenance scheduling is tight, compare checkpoint-union size together with hard-cap size.
- Treat the `0.95` tier as the current balanced default because it keeps the union at `8` while preserving near-optimal value.
- Escalate to the `0.99` tier only when near-exact preservation is truly worth a larger checkpoint calendar.
- Relax to the `0.85` tier only when the weaker guarantee is explicitly acceptable and the smaller five-point maintenance surface matters.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_checkpoint_staircase_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_checkpoint_staircase_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_checkpoint_staircase.py`
