# Public trace acceptance-bundle audit — REV0105

Status: `pass_with_blockers`  
Promotion allowed: `false`

This audit closes a false-green path where an NPZ/provenance pair could be captured but not complete enough to replay, verify, and evaluate.

## What is now required

- `core_qkv_and_rows`: 11 fields
- `public_source_identity`: 15 fields
- `runtime_device_dtype_timing`: 19 fields
- `prompt_and_tokenizer_replay`: 21 fields
- `generation_cache_replay`: 27 fields
- `phase_mask_position_kv`: 24 fields
- `score_fidelity_and_dense_reference`: 20 fields

## Blockers

- `real_public_trace_npz_and_provenance_pair_missing`
- `accepted_trace_bundle_required_before_named_hardware_timing`

## Errors

- none
