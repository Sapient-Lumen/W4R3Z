# Runtime research notes — REV0089 generated-token replay provenance gate

Generated: 2026-07-06T08:12:00-04:00

## Online sources consulted

- Hugging Face Transformers internal generation utilities: https://huggingface.co/docs/transformers/internal/generation_utils
- Hugging Face cache explanation: https://huggingface.co/docs/transformers/cache_explanation
- Hugging Face Llama model docs: https://huggingface.co/docs/transformers/model_doc/llama
- Hugging Face generation/cache best-practices docs: https://huggingface.co/docs/transformers/v4.47.1/kv_cache

## Findings used in this revision

1. `generate()` returns generated token IDs/sequences that are then decoded by the tokenizer in normal examples. That makes the generated continuation an observable artifact, not an optional note.
2. KV cache generation stores key/value pairs from previous tokens and reuses them for subsequent token decoding. A cached-decode trace is therefore a trace over the prompt plus the generated continuation that has already entered the cache.
3. Llama cache docs say that when `past_key_values` are used, the caller passes only the unprocessed `input_ids` rather than the full prior sequence. That means decode-row replay needs both the prompt boundary and the generated-token suffix boundary to know which token stream the row belongs to.
4. `max_new_tokens` bounds generated-token count, but it does not by itself bind a trace to the actual generated suffix. A digest/count/prefix contract is needed.

## Speculation / risk interpretation

The datacube’s next likely waste pattern would be a convincing but unrepeatable public trace: prompt hashes match, dense attention replay matches, but the cached decode rows came from an unknown or altered generated continuation. That would be enough to poison sparse-attention quality or cost conclusions while looking green in every matrix-level gate. rev0089 makes the next public checkpoint capture prove that its decode rows are attached to the actual generated sequence, or remain non-promotional.
