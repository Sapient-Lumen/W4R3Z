# Public trace cached-decode phase audit — rev0085

**Status:** pass_with_blockers

rev0083 blocks a false green light: valid prefill math is not enough for a sparse/KV-cache claim. A public/pretrained trace must now show both prefill and cached-decode phases, include valid_key_len padding semantics across mixed live KV lengths, and request positive decode steps.

## What was exercised

- mixed rows checked: `6`
- phases seen: `decode_cached, prefill`
- cached decode row seen: `True`
- gate accepts temporary mixed bundle: `True`
- gate rejects prefill-only bundle: `True`

## Remaining blockers

- `actual_public_pretrained_prefill_plus_cached_decode_bundle_missing`
- `verified_adapter_not_executed_against_public_pretrained_checkpoint_in_this_capsule`
- `named_hardware_end_to_end_sparse_vs_dense_measurement_missing`

## Research inputs

- Hugging Face cache explanation documentation
- Hugging Face KV cache documentation
- Hugging Face Llama past_key_values documentation
