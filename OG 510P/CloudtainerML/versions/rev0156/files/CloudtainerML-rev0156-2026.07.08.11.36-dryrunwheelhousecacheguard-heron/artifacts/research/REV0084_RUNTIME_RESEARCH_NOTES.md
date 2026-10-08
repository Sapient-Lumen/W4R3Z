# Runtime research notes — rev0084

These notes record the online research used to guide the rev0084 trace-fidelity refactor.

## Hugging Face cache semantics

Source: https://huggingface.co/docs/transformers/cache_explanation

The current-token query attends over previously cached K/V plus the current K/V during autoregressive generation. The attention mask must match the combined past-plus-current K/V length. This supports the cube's split between prefill and cached decode and the requirement that decode rows carry active key identity, not merely local q_len identity.

## Hugging Face KV cache strategies

Source: https://huggingface.co/docs/transformers/en/kv_cache

Dynamic caches grow with generation, while static and sliding cache variants can use fixed storage or stop growing at a window/chunk. Some static-cache use cases include masked tokens. This is the direct reason rev0084 distinguishes `valid_key_len` as physical exported K/V width from `active_key_len` as the mask-derived scored prefix.

## Hugging Face attention interface / mask interface

Source: https://huggingface.co/docs/transformers/en/attention_interface

Custom attention backends may need matching mask-interface registration. Otherwise the attention backend can receive no mask or an incorrect mask. rev0084 keeps the earlier built-in eager backend preservation rule and adds active-key validation so a missing or malformed mask cannot silently overcount active keys.

## Llama attention path

Source: https://github.com/huggingface/transformers/blob/main/src/transformers/models/llama/modeling_llama.py

The Llama path projects Q/K/V, applies rotary embedding to Q/K, updates cache when enabled, then calls the selected attention interface with Q/K/V, attention mask, and scaling. This supports the cube's post-transform Q/K/V capture boundary and the refusal to treat raw projection tensors as public attention-score evidence.

## Speculative interpretation

The project is now less a benchmark generator than an admissibility system for architecture claims. Its remaining danger is not lack of policies; it is allowing mathematically correct but semantically mislabeled traces to reach cost/performance conclusions. Active-key-mask verification is a small execution-facing guard against that failure.
