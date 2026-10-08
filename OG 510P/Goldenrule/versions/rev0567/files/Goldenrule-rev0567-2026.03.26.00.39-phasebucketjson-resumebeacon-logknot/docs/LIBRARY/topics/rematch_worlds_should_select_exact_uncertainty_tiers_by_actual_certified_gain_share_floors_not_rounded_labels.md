# Rematch worlds should select exact uncertainty tiers by actual certified gain-share floors, not rounded labels

## Claim
The compact repeat-sidecar uncertainty tiers should be selected by their **actual certified worst-case gain-share floors** — `0.870482`, `0.980481`, and `0.999822` — not by the rounded public labels `0.85`, `0.95`, and `0.99`.

## Why this matters
The archive already names the current exact uncertainty-safe lanes as `0.85`, `0.95`, and `0.99` tiers.
Those names are useful shorthand, but they look tighter than they really are.

The exact certification data show that the current lanes actually clear those labels by nontrivial margins:
- the relaxed lane clears `0.85` up to `0.870482`,
- the near-optimal lane clears `0.95` up to `0.980481`,
- the near-exact precision lane clears `0.99` up to `0.999822`.

That means future sessions can overpay if they escalate directly from “needs more than `0.95`” to the `0.99` lane.
For any required worst-case floor in `(0.870482, 0.980481]`, the exact `0.95` lane is still the cheapest certifiable choice.

So the archive now carries an explicit threshold selector rather than forcing inheritors to infer that hidden headroom from separate reports.

## Implementor rule
- Treat `0.85`, `0.95`, and `0.99` as conservative tier names, not as tight exact floors.
- Compare requested worst-case preservation floors against the actual certified breakpoints `0.870482`, `0.980481`, and `0.999822`.
- Use the exact `0.85` lane only when the requested floor is at most `0.870482` and its lower cap / wider tolerance is desirable.
- Use the exact `0.95` lane for any requested floor above `0.870482` and up to `0.980481`.
- Reserve the exact `0.99` lane for requested floors above `0.980481`.
- Treat requirements above `0.999822` as outside the current exact certified menu.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_guarantee_threshold_selector_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_guarantee_threshold_selector_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_guarantee_threshold_selector.py`
