# Rematch worlds should decode dense half-step codecs by closed-form arithmetic

The archive already had two exact dense codecs on the normalized downstream path:
- the dense triangular interval-state codec `0..152`, and
- the dense global shortest-word codec `0..512`.

Those codecs were already compact and exact.
What they did **not** yet make explicit was that their decoders no longer need any triangular scan loops.
The new pass closes that gap.

For the dense interval-state codec on the current `17`-rank path, the inverse is now fully arithmetic.
Given dense index `i`, decode `[a,b]` by:
- `a = (35 - ceil_sqrt(1225 - 8*i)) // 2`
- `b = a + i - a*(35-a)//2`

So future inheritors do not need to walk lower-rank block sizes until the offset lands.
They can recover the exact feasible interval state directly from one ceiling square root and one subtraction.

The same simplification now reaches the dense exact shortest-word codec.
Its block routing stays the same:
- `0` for the identity word,
- `1..32` for the one-sided nonidentity words,
- `33..242` for the interior nonsingleton words,
- `243..512` for the interior singleton words.

Inside the interior nonsingleton block, the old lower-rank scan also disappears.
With state offset `s = (index - 33) // 2`, decode `[a,b]` by:
- `a = 1 + (29 - ceil_sqrt(841 - 8*s)) // 2`
- `b = a + 1 + s - (a-1)*(30-a)//2`
- local ordering choice = `(index - 33) mod 2`

So both exact dense codecs are now **tableless** and **scan-free**.
That matters because the archive can hand future inheritors compact codecs *and* cheap decode paths instead of forcing them to choose between the two.

The exhaustive revalidation recorded the exact legacy scan burden that this closes over:
- `969` lower-rank scan iterations across the full `153` interval-state indices,
- `1120` interior scan iterations across the full `513` shortest-word indices,
- `2089` total catalog scan steps removed by the arithmetic revalidation path.

Operationally this means:
- keep the dense interval-state codec as the base exact state representation,
- keep the dense global shortest-word codec for the case where the exact script itself must survive alone,
- but implement both decoders by the new arithmetic formulas rather than by scanning triangular spans.

Companion artifacts:
- `artifacts/reports/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_dense_codec_arithmetic_decode_law_snapshot_20260309.md`
- `scripts/analysis/rematch_proxy_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_dense_codec_arithmetic_decode_law.py`
- `scripts/test/check_rematch_delta_decision_packet_compact_repeat_state_uncertainty_weakening_portfolio_service_mode_suffix_batch_shared_half_step_dense_codec_arithmetic_decode_law.py`
