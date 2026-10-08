# Public trace generation determinism audit — rev0091

**Status:** pass_with_blockers

The gate now rejects a dense-parity-valid cached-decode trace when the generation metadata indicates beam search or another non-greedy path. This prevents inherited model generation_config values from masquerading as deterministic greedy replay merely because generated token digests, exact-length counts, and local attention math match.

- deterministic generation contract: `greedy_exact_length_cached_decode_generation_config_v2`
- trace claim version: `public_trace_claim_v13`
- good bundle determinism verified: `True`
- good bundle generated-token provenance verified: `True`
- good dense error: `5.021374283042945e-08`
- forged beam-count bundle rejected: `True`
- forged rejection reason: `generation determinism contract was not verified: generation_num_beams must be 1; do_sample=False with num_beams>1 is beam search, not greedy replay`

## Remaining blockers

- `actual_public_pretrained_prefill_plus_cached_decode_generation_determinism_trace_missing`
- `verified_adapter_not_executed_against_public_pretrained_checkpoint_in_this_capsule`
- `named_hardware_end_to_end_sparse_vs_dense_measurement_missing`
