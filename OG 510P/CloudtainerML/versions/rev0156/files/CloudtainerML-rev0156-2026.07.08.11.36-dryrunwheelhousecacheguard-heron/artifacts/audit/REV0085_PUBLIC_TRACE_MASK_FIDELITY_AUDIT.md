# Public trace mask-fidelity audit — rev0085

**Status:** pass_with_blockers

rev0083 keeps the mask-fidelity contract executable and extends its fixture to mixed prefill plus cached-decode rows: a public claim must prove that a masked score row was captured, the built-in eager mask backend was preserved, no custom attention backend was used, dense attention recomputes from exported q/k/v/scale/bias, and valid_key_len padding semantics survived the mixed phase bundle. The accepted temporary bundle in this audit is only a gate harness sanity check; it is not public model evidence.

## What was exercised

- rows checked: `6`
- finite negative mask sentinel seen: `True`
- dense reconstruction max abs error: `2.0336090089667636e-08`
- decode phase present: `True`
- valid_key_len padding exercised: `True`
- gate accepts temporary masked bundle: `True`
- gate rejects missing-mask-challenge bundle: `True`

## Remaining blockers

- `actual_public_pretrained_post_transform_qkv_bundle_missing`
- `verified_adapter_not_executed_against_public_pretrained_checkpoint_in_this_capsule`
- `named_hardware_end_to_end_sparse_vs_dense_measurement_missing`

## Research inputs

- Hugging Face AttentionInterface / AttentionMaskInterface documentation
- Hugging Face Transformers Llama eager attention source
- Hugging Face Transformers issue #40362 on custom AttentionInterface behavior
