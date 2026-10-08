# Trace packet dispatch replay audit — rev0060

**Status: pass**

rev0060 closes the learned-trace dispatch-gate gap with a replayable local trace packet while keeping public/pretrained, GPU, and fused-kernel promotion blocked.

## Key metrics
- `trace_packet_rows`: `256`
- `strict_materialization_free_sparse_row_count`: `0`
- `score_storage_allowed_sparse_row_rate`: `0.7890625`
- `public_pretrained_trace_loaded`: `False`
- `oracle_leakage_rows`: `0`
