# Rematch worlds should treat exact 0.95 as the best current buffer against requirement creep

## Claim
Among the current exact compact repeat-sidecar uncertainty tiers, the exact `0.95` lane is the **best buffer against silent upward requirement creep**.

## Why this matters
The archive already records the exact certified floors behind the rounded tier names:
- relaxed `0.85` actually certifies to `0.870482`,
- near-optimal `0.95` actually certifies to `0.980481`,
- near-exact `0.99` actually certifies to `0.999822`.

That means each rounded label has a hidden amount of floor drift it can absorb before a stronger lane is truly forced.
The current exact buffers are:
- `0.85` lane -> `+0.020482`,
- `0.95` lane -> `+0.030481`,
- `0.99` lane -> `+0.009822`.

So the exact `0.95` lane is not only the strongest current non-fragile default.
It is also the tier that tolerates the **largest** amount of upward requirement drift above its rounded public label.

That makes it the best current hedge when requirement language is likely to creep upward a bit over time.
By contrast, the `0.99` lane has the smallest hidden buffer and sits only `0.000178` below the current saved exact frontier ceiling.

## Implementor rule
- Treat rounded tier labels as conservative contract names, not as tight escalation triggers.
- If a stakeholder is asking for “about `0.95`” and that requirement may drift upward modestly, stay in the exact `0.95` lane until the requested floor truly exceeds `0.980481`.
- Do not pre-pay the fragile `0.99` precision premium merely because the request rises slightly above `0.95`.
- Use the relaxed `0.85` lane when its lower cap and wider tolerance matter, not as the best hedge against future upward floor drift.
- Treat the exact `0.99` lane as the worst current hedge against continued upward creep because it is already close to frontier overflow.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_requirement_creep_buffer_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_requirement_creep_buffer_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_requirement_creep_buffer.py`
