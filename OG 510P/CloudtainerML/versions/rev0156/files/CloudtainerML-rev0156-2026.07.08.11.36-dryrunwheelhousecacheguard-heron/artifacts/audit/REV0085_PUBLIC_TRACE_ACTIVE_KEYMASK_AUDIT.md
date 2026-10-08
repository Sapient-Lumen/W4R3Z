# Public trace active-key-mask audit — rev0085

**Status:** pass_with_blockers

rev0084 prevents a cost/identity false green: dense Q/K/V parity can pass while a trace counts masked static-cache slots as active keys. The public gate now requires mask-derived active_key_len and rejects a same-math bundle whose active length is forged to the physical K/V width. This is cached-decode trace-fidelity hardening, not public-model evidence.

## What was exercised

- mixed rows checked: `6`
- active_key_len semantics verified: `True`
- absolute position uses active_key_len: `True`
- gate accepts temporary active-key bundle: `True`
- gate rejects physical-width forged bundle: `True`
- dense math same but active-key label rejected: `True`

## Static-tail decode rows

- position `4`, active_key_len `5`, physical valid_key_len `8`
- position `4`, active_key_len `5`, physical valid_key_len `8`

## Remaining blockers

- `actual_public_pretrained_prefill_plus_cached_decode_bundle_missing`
- `verified_adapter_not_executed_against_public_pretrained_checkpoint_in_this_capsule`
- `named_hardware_end_to_end_sparse_vs_dense_measurement_missing`

## Research inputs

- Hugging Face cache explanation documentation
- Hugging Face KV cache documentation
- Hugging Face attention interface documentation
