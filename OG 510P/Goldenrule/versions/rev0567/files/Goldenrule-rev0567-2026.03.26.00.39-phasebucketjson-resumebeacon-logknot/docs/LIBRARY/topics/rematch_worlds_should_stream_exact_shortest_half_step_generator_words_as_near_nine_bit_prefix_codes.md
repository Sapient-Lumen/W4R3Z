# Rematch worlds should stream exact shortest half-step generator words as near-nine-bit prefix codes

The archive already had an exact standalone codec for normalized shortest downstream half-step generator words:
- dense global index `0..512`,
- fixed width `10` bits,
- exact recovery of the full `513`-word catalog.

That codec was already simple and exact.
What it did **not** yet exploit was the fact that `513` is only one symbol above `2^9 = 512`.
So the fixed `10`-bit transport cost was leaving almost a full bit of slack on nearly every exact shortest word.

The new pass closes that gap with a canonical prefix wrapper over the **existing** dense index order.
The code is:
- dense indices `0..510` → raw `9`-bit binaries,
- dense index `511` → `1111111110`,
- dense index `512` → `1111111111`.

So the full exact shortest-word catalog is now streamable as a self-delimiting prefix code with:
- `511` nine-bit words,
- `2` ten-bit words,
- mean length `4619 / 513 = 9.003898635477582` bits.

Against the older fixed `10`-bit dense-index transport, that saves:
- `511` bits over the full `513`-word exact catalog,
- `511 / 513 = 0.9961013645224172` bits on average per exact shortest word,
- `511 / 5130 = 0.09961013645224172` share of the old fixed transport budget.

Decode is also tiny.
Read `9` bits first.
If the value is below `511`, stop and reuse the existing dense-index decode laws.
If the value is exactly `511`, read one more bit and return dense index `511` or `512` accordingly.
So this pass shortens transport cost without changing any of the earlier exact-state, local-choice, dense-word, or arithmetic-decode machinery.

Only two exact words pay the tenth bit under the canonical split:
- dense index `511` → `[[0,1],[15,16]]`
- dense index `512` → `[[0,0],[15,16]]`

Operationally this means:
- keep the dense interval-state codec when exact downstream state is what matters,
- keep the local choice index when interval state is already stored elsewhere,
- but when an exact shortest script must travel alone as a self-delimiting bitstream, prefer this new near-nine-bit prefix transport over writing all `10` dense bits unconditionally.

Companion artifacts:
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law_snapshot_20260309.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law.py`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_prefix_law.py`
