# Rematch worlds should stream exact normalized half-step interval states as near-seven-bit prefix codes

The archive already had an exact standalone codec for normalized downstream feasible interval states:
- dense triangular index `0..152`,
- fixed width `8` bits,
- exact recovery of the full `153`-state catalog.

That codec was already small and exact.
What it did **not** yet exploit was that `153` is only `25` symbols above `2^7 = 128`.
So the fixed `8`-bit transport was leaving a substantial fraction of a bit unused on average.

The new pass closes that gap with a canonical prefix wrapper over the **existing** dense interval-state index order.
The code is:
- dense indices `0..102` → raw `7`-bit binaries,
- dense indices `103..152` → split `8`-bit leaves under the remaining `7`-bit prefixes `103..127`.

So the full exact interval-state catalog is now streamable as a self-delimiting prefix code with:
- `103` seven-bit states,
- `50` eight-bit states,
- mean length `1121 / 153 = 7.326797385620915` bits.

Against the older fixed `8`-bit dense-index transport, that saves:
- `103` bits over the full `153`-state exact catalog,
- `103 / 153 = 0.673202614379085` bits on average per interval state,
- `103 / 1224 = 0.08415032679738563` share of the old fixed transport budget.

Decode is also tiny.
Read `7` bits first.
If the value is below `103`, stop and reuse the existing dense-index arithmetic interval-state decode.
If the value is at least `103`, read one more bit and return dense index `103 + 2*(value-103) + suffix`.
So this pass shortens standalone state transport without changing any of the earlier exact-state, shortest-word, or arithmetic-decode machinery.

The first two long-form states under the canonical split are:
- dense index `103` → `[8,11]`
- dense index `104` → `[8,12]`

Operationally this means:
- keep the dense interval-state codec when exact downstream state is what matters,
- keep the local choice and shortest-word codecs for script-level transport,
- but when an exact interval state itself must travel alone as a self-delimiting bitstream, prefer this new near-seven-bit prefix transport over writing all `8` dense bits unconditionally.

Companion artifacts:
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_law_snapshot_20260309.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_law.py`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_feasible_interval_state_prefix_law.py`
