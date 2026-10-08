# Revision lineage static audit — rev0077

**Status:** pass_with_debt  
**Promotion:** blocked

The three historical public-trace experiments and their audits are now pinned to their original revisions, so they cannot silently mint rev0076 artifacts. Other legacy runners still inherit the current revision and must be migrated incrementally; this is integrity debt, not evidence for promotion.

## Counts

- Python files scanned: 160
- Dynamic current-revision scripts: 83
- Historical artifact-minting hazards still present: 63
- Of those, experiment runners: 28
- Of those, audits/reports: 35
- Dynamic revision plus hard-coded timestamp hazards: 12
- Protected public-trace surfaces pinned safely: 6/6

## Why this matters

A historical script that reads the live cube revision can write a current-revision artifact even though its assumptions, timestamp, and experiment contract belong to an older revision. That creates a plausible but false lineage surface and can waste later work debugging evidence that never belonged to the stated run.

## Migration rule

Historical runners should pin their original revision and remain immutable. A genuine rerun should use an explicit new run revision, a runtime execution timestamp, source/code/dependency hashes, and a separate output namespace.

## Remaining high-risk experiment runners

- `experiments/attention_end_to_end_cpu_microbench/run_attention_end_to_end_cpu_microbench.py` (fallback rev0047)
- `experiments/attention_mass_frontier/attention_mass_frontier.py` (fallback rev0044)
- `experiments/attention_row_compiler_benchmark/attention_row_compiler_benchmark.py` (fallback rev0044)
- `experiments/attention_selector_cpu_microbench/run_selector_cpu_microbench.py` (fallback rev0046)
- `experiments/fused_streaming_schedule/run_fused_streaming_schedule.py` (fallback rev0058)
- `experiments/lane_decision_matrix/lane_decision_matrix.py` (fallback rev0072; hard-coded 2026-06-18T17:18:00-04:00)
- `experiments/learned_trace_block_bounds/learned_trace_block_bounds.py` (fallback rev0053)
- `experiments/mass_certified_attention_compiler/mass_certified_attention_compiler.py` (fallback rev0045)
- `experiments/platform_cost_calibration/run_platform_cost_calibration.py` (fallback rev0057)
- `experiments/public_trace_acceptance_preflight/public_trace_acceptance_preflight.py` (fallback rev0076)
- `experiments/router_cost_frontier/router_cost_frontier.py` (fallback rev0056)
- `experiments/router_shift_stress/router_shift_stress.py` (fallback rev0055)
- `experiments/row_adaptive_attention_router/row_adaptive_attention_router.py` (fallback rev0054)
- `experiments/score_path_block_pruning/run_score_path_block_pruning.py` (fallback rev0051)
- `experiments/tiny_transformer_attention_traces/tiny_transformer_attention_trace_probe.py` (fallback rev0044)
- `experiments/trace_packet_boundary_refined_selector/trace_packet_boundary_refined_selector.py` (fallback rev0068; hard-coded 2026-06-18T14:06:00-04:00)
- `experiments/trace_packet_certified_support_reuse/trace_packet_certified_support_reuse.py` (fallback rev0069; hard-coded 2026-06-18T15:04:00-04:00)
- `experiments/trace_packet_deployable_selector_layout/trace_packet_deployable_selector_layout.py` (fallback rev0065; hard-coded 2026-06-18T12:26:00-04:00)
- `experiments/trace_packet_dispatch_replay/trace_packet_dispatch_replay.py` (fallback rev0060; hard-coded 2026-06-18T08:35:00-04:00)
- `experiments/trace_packet_native_replay/trace_packet_native_replay.py` (fallback rev0061; hard-coded 2026-06-18T09:22:00-04:00)
- `experiments/trace_packet_qk_native_replay/trace_packet_qk_native_replay.py` (fallback rev0062; hard-coded 2026-06-18T10:04:00-04:00)
- `experiments/trace_packet_speed_envelope/trace_packet_speed_envelope.py` (fallback rev0063; hard-coded 2026-06-18T10:47:00-04:00)
- `experiments/trace_packet_stage_prune_cert_policy/trace_packet_stage_prune_cert_policy.py` (fallback rev0070; hard-coded 2026-06-18T16:33:00-04:00)
- `experiments/trace_packet_support_reuse/trace_packet_support_reuse.py` (fallback rev0066; hard-coded 2026-06-18T13:04:00-04:00)
- `experiments/trace_packet_twostage_cert_reuse/trace_packet_twostage_cert_reuse.py` (fallback rev0070; hard-coded 2026-06-18T15:55:00-04:00)
- `experiments/trace_packet_value_layout_envelope/trace_packet_value_layout_envelope.py` (fallback rev0064; hard-coded 2026-06-18T11:32:00-04:00)
- `experiments/value_norm_guarded_attention/value_norm_guarded_attention.py` (fallback rev0046)
- `experiments/value_norm_sidecar_cpu_path/run_value_norm_sidecar_cpu_path.py` (fallback rev0050)
