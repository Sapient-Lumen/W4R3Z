# Runtime research notes — rev0087

## Research question

Can a public trace pass dense Q/K/V replay while still carrying wrong cached-decode position semantics?

## Sources checked

- Hugging Face Transformers current `modeling_llama.py`: `LlamaModel.forward` derives `position_ids` from `past_key_values.get_seq_length()` when `position_ids` is absent, computes rotary embeddings from those ids, and passes position data through the decoder layer.
- Hugging Face Transformers current `modeling_llama.py`: `LlamaAttention.forward` applies RoPE to query/key states before cache update and before the selected attention interface.
- Hugging Face Transformers current `modeling_llama.py`: eager attention repeats compact K/V heads, adds the attention mask, applies float32 softmax, applies dropout, and performs value matmul.
- Hugging Face RoPE utilities documentation: RoPE parameters and behavior are model/config-specific, so position handling should be captured rather than inferred from generic labels.
- Hugging Face KV cache documentation: cache strategy affects physical storage and decode behavior, so physical/active cache positions and runtime/global position ids must remain separate.

## Decision

Add `rotary_position_id` as a public trace field and gate it independently from `position`. Keep `position` for active scored-key row identity. Use `rotary_position_id` for runtime RoPE/global position evidence. Reject cached-decode rows that collapse runtime RoPE position to local q_len index `0`.
