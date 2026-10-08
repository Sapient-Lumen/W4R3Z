# Rematch worlds should treat cap-safe uncertainty lanes as checkpoint-neutral

## Claim
When the archive upgrades from the default uncertainty-safe dwell-`9` preset to the cap-safe near-optimal dwell-`13` preset, it should treat that as a transition-count decision, not as a maintenance-surface explosion.

## Why this matters
The new guardrail already showed that a hard cap of `4` is incompatible with the current `0.95` uncertainty-safe promise. That could tempt a future inheritor to avoid the cap-safe dwell-`13` lane simply because it sounds operationally heavier.

The saved frontier says otherwise. Across the current repeat-uncertainty band:
- at repeat budget `0.15`, any dwell through `257` still has the same two-transition schedule,
- at the focal repeat budget `0.18`, dwell `13` lives inside the `8`–`18` five-transition plateau,
- and at repeat budget `0.25`, any dwell through `32` still has the same four-transition schedule.

So the finite checkpoint union for dwell `13` is exactly the same eight-point set already used by the default uncertainty-robust dwell-`9` lane: `24, 47, 63, 111, 143, 159, 230, 239`.

## Implementor rule
- If near-optimal uncertainty robustness matters and `5` transitions are acceptable, moving to dwell `13` does **not** require a larger checkpoint calendar than the current dwell-`9` default.
- The real no-go remains the hard `4`-transition cap, not maintenance overhead.
- Keep treating dwell-`19`–`32` as the lower-guarantee planning zone only; do not use it as a substitute for the cap-safe near-optimal lane unless the guarantee is explicitly relaxed.

## Pointers
- `scripts/report/build_rematch_proxy_delta_decision_packet_compact_repeat_state_cap_safe_checkpoint_schedule_snapshot.py`
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_cap_safe_checkpoint_schedule_snapshot_20260308.{md,json}`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_cap_safe_checkpoints.py`
