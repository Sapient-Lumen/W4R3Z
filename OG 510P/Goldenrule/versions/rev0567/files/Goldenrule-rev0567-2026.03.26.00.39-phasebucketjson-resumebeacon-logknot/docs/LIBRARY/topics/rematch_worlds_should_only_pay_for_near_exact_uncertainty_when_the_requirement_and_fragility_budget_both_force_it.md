# Rematch worlds should only pay for near-exact uncertainty when the requirement and fragility budget both force it

## Claim
The current exact `0.99` compact repeat-sidecar uncertainty tier should be treated as a **precision escalation gate**, not as a generic stronger default.
Future inheritors should only pay for it when the deployment both:
- requires a worst-case preserved-gain floor **above `0.980481`**, and
- can accept the current near-exact tier’s **single-point zero-slack fragility**.

## Why this matters
The archive already contains the pieces of this conclusion, but they were spread across several cards:
- the exact `0.95` lane is certified up to **`0.980481`**,
- the exact `0.99` lane requires **hard cap `11`**,
- before master-calendar amortization it needs **`14` checkpoints**,
- and its dwell tolerance collapses to a single point with **zero minimum slack** and **band width `1`**.

That means the upgrade to near-exact precision should not be triggered just because the deployment *can* afford it.
It should be triggered only when the deployment actually needs a certified floor above `0.980481` **and** is willing to run a single-point precision mode.

This is useful because many future handoffs will start from “we want stronger protection” and then over-escalate.
The archive can now say something sharper:
- if the requirement is at or below `0.980481`, stay on the exact `0.95` lane,
- if the requirement is above `0.980481` but any positive slack is mandatory, there is **no current exact non-fragile near-exact option**,
- and if the master calendar has already been pre-registered, the only blocker that disappears is checkpoint budget — the floor, cap, and fragility gates remain.

So this card turns the near-exact tier from a temptation into an exact gate.

## Implementor rule
- Escalate from exact `0.95` to exact `0.99` only when the required worst-case floor exceeds `0.980481`.
- Treat exact `0.99` as a single-point precision mode: hard cap `11`, minimum slack `0`, band width `1`.
- Before the master calendar is pre-registered, also require checkpoint budget `14`.
- After master-calendar amortization, drop only that checkpoint blocker; do **not** drop the floor, cap, or fragility gates.
- If the required floor exceeds `0.980481` but any positive slack or any band width above `1` is required, record that the current exact menu has no surviving exact tier rather than pretending `0.99` is still feasible.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_precision_escalation_gate_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_precision_escalation_gate_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_precision_escalation_gate.py`
