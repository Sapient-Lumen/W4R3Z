# Rematch worlds should stream state-conditional shortest-word choices as prefixes

The archive already had a sharp normalized downstream split for exact shortest scripts:
- one exact feasible interval state `[a,b]`, and
- one local shortest-word choice index once that state is known.

That local choice codec was already tiny:
- `33` states needed `0` bits,
- `105` states needed `1` bit,
- `15` interior singleton states needed `5` bits.

But the old `5`-bit interior-singleton field was still fixed width.
That left a little slack because those states have only `18` legal local choices, not `32`.

The new pass closes that gap with a **state-conditional prefix code** for the local choice field itself.
The interval state still has to be known first.
Once it is known, the exact shortest script can be streamed by this smaller local code:

- unique states: only choice `0`, encoded by the empty string,
- interior nonsingleton states: choices `0` and `1`, encoded by `0` and `1`,
- interior singleton states: choices `0..13` use raw `4`-bit binaries and choices `14..17` use the four `5`-bit leaves `11100`, `11101`, `11110`, `11111`.

So the full exact local-choice catalog now has this exact bit-length spectrum over all `513` shortest words:
- `33` words at `0` bits,
- `210` words at `1` bit,
- `210` words at `4` bits,
- `60` words at `5` bits.

Against the older fixed-width local choice field, that reduces the exact local transport cost from:
- `1560` bits total over the full `513`-word catalog,

to:
- `1350` bits total,
- mean `1350 / 513 = 2.6315789473684212` bits per exact shortest word,
- saving `210` bits total,
- and `210 / 513 = 0.4093567251461988` bits per word on average.

The sharp operational boundary is important.
This new codec is **only** the right tool when interval state is already present or carried separately.
If a future inheritor tries to prepend interval-state transport and use this as a standalone exact-script codec, the combined cost becomes:
- `3809 + 1350 = 5159` bits over the full catalog,
- mean `10.056530214424951` bits per word,
which is strictly worse than the archive’s earlier standalone global exact-word prefix transport at `4619` total bits and mean `9.003898635477582` bits.

So the codec boundary is now explicit:
- if exact interval state is already known, prefer this new local choice prefix over a fixed local field,
- if an exact shortest script must travel alone, keep using the earlier global exact-word prefix codec,
- and do not store or search per-state shortest-word arrays.

Companion artifacts:
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_law_snapshot_20260309.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_law.py`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_shortest_generator_word_choice_prefix_law.py`
