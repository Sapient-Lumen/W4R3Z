# Public trace absolute-position audit — rev0086

**Status:** pass_with_blockers

rev0083 prevents a dense-parity blind spot: cached-decode rows must export absolute key positions. The gate now rejects a bundle whose Q/K/V/scale/bias/reference math is still correct but whose decode row is labeled with the local q_len=1 index. This is row-identity hardening, not public-model evidence.

## What was exercised

- mixed rows checked: `6`
- absolute position semantics verified: `True`
- gate accepts temporary absolute-position bundle: `True`
- gate rejects local decode-position bundle: `True`
- dense math same but position label rejected: `True`

## Remaining blockers

- `actual_public_pretrained_prefill_plus_cached_decode_bundle_missing`
- `verified_adapter_not_executed_against_public_pretrained_checkpoint_in_this_capsule`
- `named_hardware_end_to_end_sparse_vs_dense_measurement_missing`

## Research inputs

- Hugging Face cache explanation documentation
- Hugging Face KV cache documentation
- TensorRT-LLM disaggregated serving documentation
