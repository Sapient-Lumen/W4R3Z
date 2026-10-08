# Public trace token provenance audit — rev0102

**Status:** pass_with_blockers

The gate now rejects a dense-parity-valid cached-decode trace when its row positions cannot be replayed against the exact tokenized prompt boundary. This prevents an unreplayable Q/K/V bundle from being accepted as public evidence merely because its local attention math matches.

- prompt contract: `prompt_input_ids_attention_mask_digest_v2`
- generation contract: `generated_sequence_digest_exact_length_v2`
- good bundle token provenance verified: `True`
- good bundle generated-token provenance verified: `True`
- good dense error: `5.021374283042945e-08`
- forged prompt-count bundle rejected: `True`
- forged rejection reason: `token provenance contract was not verified: row 6: decode position 3 not in generated-token window [99, 101)`

## Remaining blockers

- `actual_public_pretrained_prefill_plus_cached_decode_generated_token_trace_missing`
- `verified_adapter_not_executed_against_public_pretrained_checkpoint_in_this_capsule`
- `named_hardware_end_to_end_sparse_vs_dense_measurement_missing`
