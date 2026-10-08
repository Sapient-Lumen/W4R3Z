# Runtime research notes — REV0088 prompt/token provenance gate

Generated: 2026-07-06T07:24:00-04:00

## Online sources consulted

- Hugging Face Transformers text generation docs: https://huggingface.co/docs/transformers/en/main_classes/text_generation
- Hugging Face LLM tutorial generation section: https://huggingface.co/docs/transformers/en/llm_tutorial
- Hugging Face cache strategies docs: https://huggingface.co/docs/transformers/en/kv_cache
- Hugging Face AttentionInterface docs: https://huggingface.co/docs/transformers/en/attention_interface
- Hugging Face Transformers Llama implementation source: https://github.com/huggingface/transformers/blob/main/src/transformers/models/llama/modeling_llama.py
- Hugging Face Transformers cache utilities source: https://github.com/huggingface/transformers/blob/main/src/transformers/cache_utils.py

## Findings used in this revision

1. `max_new_tokens` is defined as the number of generated tokens while ignoring the number of tokens in the prompt. That makes prompt length and decode length separate quantities; a trace cannot be replayed from `decode_steps` alone.
2. Decoder-only generation returns the prompt plus generated tokens, so prompt-boundary accounting must be explicit when row positions are interpreted across prefill and cached-decode phases.
3. Transformers cache strategies distinguish dynamic, static, sliding/chunked, offloaded, and quantized caches. Because cache storage shape is not equivalent to active scored tokens, prompt/decode row provenance must be bound to tokenized inputs and masks.
4. AttentionInterface makes backend substitution possible, so the trace contract must describe observable runtime semantics rather than relying on an implementation name.
5. Llama attention applies RoPE using runtime position information before attention scoring; rev0087 separated RoPE `position_ids`. rev0088 adds the complementary tokenizer-bound prompt provenance needed to replay those positions.

## Speculation / risk interpretation

The datacube’s next failure mode is likely not a wrong matrix multiplication. It is an evidentiary mismatch: a trace produced by one prompt/tokenizer/generation boundary could be presented as if it came from another. That would contaminate any sparse-attention cost or quality conclusion even if local dense replay still passes. The v10 gate forces the next public checkpoint capture to carry enough token provenance to be replayed and falsified.
