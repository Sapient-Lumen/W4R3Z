# Rematch worlds should treat dwell 3 through 7 as an exact uncertainty gap, not a retuning target

## Claim
The current exact compact repeat-sidecar uncertainty menu has a real internal dwell-coverage gap at **dwell `3` through `7`**.
Future inheritors should treat that region as **outside the saved exact certified menu**, not as a routine retuning neighborhood.

## Why this matters
The archive now has strong exact cards for cap, checkpoints, tolerance, canonical anchors, and guarantee thresholds.
Those cards implicitly define the topology of the current certified dwell menu:
- exact `0.99` covers only dwell `2`,
- exact `0.95` covers dwell `8–18`,
- exact `0.85` covers dwell `19–32`.

That means the current exact menu covers dwell `2` and then resumes only at dwell `8`.
The values `3, 4, 5, 6, 7` are not covered by any saved exact uncertainty-safe lane.

This is useful because implementors often want to “try nearby small dwells” when a precision point looks brittle.
For the current exact menu, that instinct is wasted motion.
If a deployment cannot tolerate the isolated precision point at dwell `2`, the next live exact choice is not dwell `3` or `4` — it is the start of the exact `0.95` band at dwell `8`.

So the archive should remember this as a search-discipline rule, not as a hidden implication scattered across several reports.

## Implementor rule
- Treat dwell `2` as a special isolated precision point tied to the exact `0.99` lane.
- Treat dwell `3–7` as an exact-certification gap under the current saved frontier.
- When any positive slack or any band width above `1` is required, jump straight to the exact `0.95` band beginning at dwell `8`.
- Treat dwell `8–32` as the current continuous non-precision exact menu, with the exact `0.95` and `0.85` bands meeting cleanly at dwell `18/19`.
- Treat dwells below `2` and above `32` as outside the current exact certified menu unless new evidence is generated.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_coverage_topology_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_dwell_coverage_topology_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_dwell_coverage_topology.py`
