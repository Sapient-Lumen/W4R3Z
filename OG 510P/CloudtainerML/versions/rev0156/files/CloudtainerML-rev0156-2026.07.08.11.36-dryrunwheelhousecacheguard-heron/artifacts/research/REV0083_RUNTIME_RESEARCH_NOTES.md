# Runtime research notes — REV0083 absolute-position cached-decode trace gate

## Finding 1 — cached decode rows are absolute KV-cache rows, not local q_len indices

Source: https://huggingface.co/docs/transformers/en/cache_explanation

Hugging Face explains that cached attention combines current token K/V with past cached K/V, producing attention over `past_kv_length + new_tokens_length`. The same document says iterative cached forward passes need an attention mask matching that combined past-plus-current length. For CloudtainerML, a q_len=1 decode row therefore needs an absolute live-KV position, not merely local query index 0.

## Finding 2 — cache strategy changes live-length behavior

Source: https://huggingface.co/docs/transformers/en/kv_cache

Hugging Face documents DynamicCache as the default generation cache and notes that static/sliding/chunked cache variants can alter growth or fixed-size masking behavior. That means the trace surface must explicitly preserve `valid_key_len`, `query_len`, `capture_phase`, and absolute `position`, rather than depending on shape guesses after padding.

## Finding 3 — production serving treats prefill and decode as separate phases with KV identity

Source: https://github.com/NVIDIA/TensorRT-LLM/blob/main/docs/source/features/disagg-serving.md

TensorRT-LLM describes context/prefill as computing prompt KV cache and generation/decode as generating tokens one by one from cached values. It also discusses KV exchange/request identity in disaggregated serving. This strengthens the conclusion that CloudtainerML's public trace path must preserve phase and row identity, not just numerical parity.

## Finding 4 — vLLM disaggregated prefill makes KV transfer explicit

Source: https://docs.vllm.ai/en/latest/features/disagg_prefill/

vLLM's disaggregated prefill documentation describes prefill and decode instances connected by KV-cache transfer abstractions. This reinforces that the evidence target is a serving-phase trace with live KV semantics, not a square prefill-only matrix.

## Change driven by research

- Add `position_contract="absolute_key_position_v1"` to the public trace claim.
- Add `absolute_position_verified=true` to capture output and public gate requirements.
- Compute cached-decode row positions as `query_start_position + local_query_index`, falling back to `key_len - query_len` when runtime cache_position is not available.
- Gate-recompute position semantics from arrays, so a forged manifest/NPZ boolean cannot pass alone.
- Add a negative-control audit where dense math remains correct but decode positions are relabeled as local q_len positions; the public gate rejects it.

## Remaining execution blocker

The refactor closes a position-label false-positive path, but it does not create public evidence. The next real step is still a captured immutable public Llama-family checkpoint, gate acceptance, and named-hardware timing.
