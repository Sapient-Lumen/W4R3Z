# Named hardware timing contract — REV0117

Status: `blocked_missing_named_hardware_timing`  
Promotion allowed: `false`

Trace capture timing is diagnostic provenance only. Promotion timing requires a separate named-hardware sparse-vs-dense run after the public trace gate accepts a real model trace.

## Required fields
- `hardware_run_id`
- `machine_owner_or_lab`
- `gpu_name`
- `gpu_uuid_or_redacted_stable_id`
- `gpu_count`
- `driver_version`
- `cuda_runtime_version`
- `torch_version`
- `transformers_version`
- `attention_backend_dense`
- `attention_backend_sparse_candidate`
- `model_id`
- `model_revision`
- `trace_gate_artifact_sha256`
- `dtype`
- `batch_shape`
- `context_lengths`
- `decode_steps`
- `warmup_iterations`
- `measured_iterations`
- `timing_clock`
- `cuda_event_timing_used`
- `torch_cuda_synchronize_before_after`
- `dense_latency_ms_p50_p95`
- `sparse_latency_ms_p50_p95`
- `quality_or_exactness_delta`
- `raw_command_log`
