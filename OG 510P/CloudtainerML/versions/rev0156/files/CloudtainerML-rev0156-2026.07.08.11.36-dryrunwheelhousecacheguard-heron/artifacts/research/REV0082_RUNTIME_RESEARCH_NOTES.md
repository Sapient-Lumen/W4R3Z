# Runtime research notes — REV0082 cached-decode phase gate

## Finding 1 — cached decode changes the mask/length contract

Source: https://huggingface.co/docs/transformers/en/cache_explanation

Hugging Face explains that, during iterative cached forward passes, the attention mask must cover the combined past KV length plus the new token length. `generate()` normally handles this internally. For CloudtainerML, this means a real trace must preserve live KV length semantics, not just serialize a square prefill attention row.

## Finding 2 — KV-cache behavior is a generation-path concern, not a prefill footnote

Source: https://huggingface.co/docs/transformers/en/kv_cache

Hugging Face documents cache classes used for generation, including `DynamicCache` as a common/default strategy. A public sparse/KV-cache claim that only validates prefill math is incomplete, because the runtime value is in cached generation/decode.

## Finding 3 — Llama cached decode only feeds unprocessed tokens

Source: https://huggingface.co/docs/transformers/model_doc/llama

The Llama documentation describes `past_key_values` as cache instances containing precomputed hidden states, and when cache values are supplied, `input_ids` should contain only tokens that do not already have past values. That creates the characteristic decode shape: a short query length, often one token, attending over a longer live KV cache.

## Change driven by research

- Add `--decode-steps` to the capture helper and require it to be positive for public/pretrained trace acceptance.
- Export per-row `capture_phase`, `valid_key_len`, and `query_len`.
- Require `capture_phase_contract="prefill_and_cached_decode_v1"`.
- Require both prefill and cached-decode phase coverage.
- Require at least one cached-decode row with `query_len=1` and live KV length greater than one.
- Pad mixed-length K/V/bias rows with finite sentinel masking and verify `valid_key_len` semantics in the public gate.

## Remaining execution blocker

The refactor closes a prefill-only false-positive path, but it does not create public evidence. The next real step is still a captured immutable public Llama-family checkpoint, gate acceptance, and named-hardware timing.
