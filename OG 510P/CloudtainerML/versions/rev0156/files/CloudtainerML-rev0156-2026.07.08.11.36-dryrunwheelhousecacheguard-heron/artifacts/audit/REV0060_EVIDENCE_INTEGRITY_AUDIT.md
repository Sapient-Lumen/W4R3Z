# Evidence integrity audit — rev0060

**Status: trace_packet_dispatch_replay_passed_promotion_still_blocked**

rev0060 adds a replayable learned trace packet and dispatch replay, while preserving public/pretrained and fused-kernel blockers. It also fixes the stale current-artifact surface by pointing status/audit checks at rev0060 artifacts.

## Blockers
- actual_public_pretrained_trace_bundle_missing
- gpu_fused_attention_kernel_timing_missing
- strict_materialization_free_sparse_schedule_has_no_learned_trace_speed_win
- materialized_sparse_cpu_path_requires_global_score_storage
- value_norm_sidecar_kernel_path_missing
