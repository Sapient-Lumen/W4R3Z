# Public trace cache implementation audit — REV0101

Status: `pass_with_blockers`  
Promotion allowed: `false`

The public trace gate now rejects dense-parity-valid bundles whose only forged field is a non-dynamic generation cache implementation. Static/offloaded/quantized caches remain valid timing/baseline research lanes, but they cannot be the score-path evidence lane until separately contracted.

- contract: `hf_generate_dynamic_cache_v1`
- required cache implementation: `dynamic`
- good dynamic-cache bundle verified: `True`
- forged static-cache bundle rejected: `True`
- forged rejection reason: `generation_cache_implementation must be explicit dynamic cache for public trace replay`

## Remaining blockers

- `actual_public_pretrained_prefill_plus_cached_decode_dynamic_cache_trace_missing`
- `verified_adapter_not_executed_against_public_pretrained_checkpoint_in_this_capsule`
- `named_hardware_end_to_end_sparse_vs_dense_measurement_missing`
