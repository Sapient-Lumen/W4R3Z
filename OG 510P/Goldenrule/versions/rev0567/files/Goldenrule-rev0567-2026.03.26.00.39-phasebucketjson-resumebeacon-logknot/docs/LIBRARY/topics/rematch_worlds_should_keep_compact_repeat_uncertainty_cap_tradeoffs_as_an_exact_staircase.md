# Rematch worlds should keep compact repeat uncertainty-cap tradeoffs as an exact staircase

The archive now has enough exact compact repeat-sidecar certifications that future inheritors should stop carrying them as scattered notes. The current repeat-uncertainty story is best remembered as one small **exact staircase**:

- hard cap `11` buys the near-exact `0.99` lane at dwell `2`
- hard cap `5` buys the near-optimal `0.95` lane on dwell `8`–`18` with representative anchor `13`
- hard cap `3` buys the relaxed `0.85` lane on dwell `19`–`32` with representative anchor `25`

Why this matters:

- The archive had started to drift into an inconsistent state: the old guardrail report still carried a lower-guarantee **planning** cap of `4`, even after the exact three-cap certification had landed.
- The new staircase card lets the inheritor cite one coherent object instead of mentally merging older and newer notes.
- The middle `0.95` tier remains checkpoint-neutral relative to the dwell-`9` uncertainty default, so the main difference between the `5`-cap and `3`-cap lanes is guarantee level, not checkpoint sprawl.

Implementor rule:

- Keep the staircase itself in durable memory.
- Treat older lower-guarantee four-cap language as historical context, not current truth.
- Only reopen the frontier if the repeat band changes, the gain-share targets change, or a future world materially alters the compact sidecar schedule.

Primary artifacts:

- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_staircase_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_cap_staircase_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_cap_staircase.py`
