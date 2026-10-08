# Runtime research notes — rev0091

## Question

After rev0090, are greedy single-beam generation settings enough to make cached-decode public traces replay-complete?

## Finding

No. The relevant runtime seam is generated-token count, not only decode strategy. Hugging Face text-generation documentation describes `max_new_tokens` as the maximum number of tokens to generate and `min_new_tokens` as the minimum number to generate. It also documents `do_sample`, `num_beams`, `num_return_sequences`, and cache settings as independent generation controls. Hugging Face cache documentation separately emphasizes that cached decoding reuses prior key/value state and that the attention mask must cover the combined past-plus-current key/value length.

## Implication for the cube

A trace can be greedy, single-beam, hash-checked, and token-digested yet still be incomplete if EOS/stop behavior produces fewer generated tokens than the requested cached-decode horizon. That would corrupt row coverage, per-step cost accounting, and sparse-vs-dense comparisons. Exact generated-token count must therefore be a gate condition, not a convenience metric.

## Change made

rev0091 advances the public trace claim version to `public_trace_claim_v13`, upgrades generated-token provenance to `generated_sequence_digest_exact_length_v2`, and upgrades generation determinism to `greedy_exact_length_cached_decode_generation_config_v2`. Public cached-decode traces now require `min_new_tokens=max_new_tokens=decode_steps_requested`, `generation_exact_new_tokens_required=true`, and `generated_new_token_count_min/max == decode_steps_requested`. The new negative control rejects an early-stopped one-token continuation for a two-step decode request while leaving the rest of the fixture intact.

## Sources checked

- Hugging Face Transformers text generation docs: https://huggingface.co/docs/transformers/en/main_classes/text_generation
- Hugging Face Transformers KV-cache strategies docs: https://huggingface.co/docs/transformers/en/kv_cache
- Hugging Face Transformers cache explanation: https://huggingface.co/docs/transformers/cache_explanation
