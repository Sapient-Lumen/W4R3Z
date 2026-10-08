# Public trace runtime RoPE position audit — rev0086

**Status:** pass_with_blockers

rev0087 prevents a cached-decode false green: a trace can contain correct post-RoPE Q/K/V rows and still mislabel the runtime RoPE position_id as local q_len position 0. The public gate now requires row-level rotary_position_id evidence and rejects a same-math forged bundle whose decode RoPE id no longer matches the runtime/global position semantics. This remains trace-fidelity hardening; it is not a substitute for a real public checkpoint capture.

## What was exercised

- mixed rows checked: `6`
- rotary position contract verified: `True`
- cached-decode rows with global RoPE offset: `2`
- gate accepts temporary runtime-RoPE bundle: `True`
- gate rejects local q_len RoPE-id forgery: `True`
- dense math same but local RoPE label rejected: `False`

## Global decode RoPE rows

- active position `4`, rotary_position_id `7`, active_key_len `5`
- active position `4`, rotary_position_id `7`, active_key_len `5`

## Remaining blockers

- `actual_public_pretrained_prefill_plus_cached_decode_bundle_missing`
- `verified_adapter_not_executed_against_public_pretrained_checkpoint_in_this_capsule`
- `named_hardware_end_to_end_sparse_vs_dense_measurement_missing`

## Research inputs

- Hugging Face current Llama modeling source
- Hugging Face RoPE utilities documentation
- Hugging Face KV cache documentation
