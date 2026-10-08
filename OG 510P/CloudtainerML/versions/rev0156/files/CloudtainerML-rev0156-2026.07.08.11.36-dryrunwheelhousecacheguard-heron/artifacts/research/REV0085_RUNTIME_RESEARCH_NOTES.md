# Runtime research notes — REV0085 GQA/KV group map

Retrieved July 6, 2026.

## Findings used in this revision

1. Hugging Face Transformers Llama config documents `num_key_value_heads` as the field that implements MHA/MQA/GQA semantics. Equal key-value heads and attention heads means MHA; one key-value head means MQA; intermediate values mean GQA. Source: https://huggingface.co/docs/transformers/en/model_doc/llama2

2. Current Transformers Llama eager attention defines `repeat_kv`, converting hidden states from `(batch, num_key_value_heads, seqlen, head_dim)` to `(batch, num_attention_heads, seqlen, head_dim)`, and calls it for key and value states before computing attention weights. Source: https://github.com/huggingface/transformers/blob/main/src/transformers/models/llama/modeling_llama.py

3. PyTorch `torch.nn.functional.scaled_dot_product_attention` exposes `enable_gqa`, so grouped-query semantics are an active runtime API concern. Source: https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html

4. PyTorch's GQA API discussion says GQA reduces KV-cache memory, math kernels may repeat-interleave K/V to match query heads, and flash attention does not need the same materialized repeat. Source: https://dev-discuss.pytorch.org/t/added-grouped-query-attention-to-scaled-dot-product-attention-api/2340

## Why this matters for CloudtainerML

A trace can contain per-query-row K/V tensors that are numerically sufficient for dense attention reconstruction while still being ambiguous or wrong for cache ownership. For a grouped-query model, heads 0 and 1 may share compact KV head 0, while heads 2 and 3 share compact KV head 1. If the trace omits that ownership, downstream sparse/cost analysis can overcount K/V storage, misattribute cache eviction, or claim a selector saved per-query-head storage that never existed.

## Revision implication

Rev0085 makes query-head to compact-KV-head mapping part of public trace admissibility. The gate recomputes expected `kv_head = head // num_key_value_groups` under declared head-count metadata and rejects mismatches, including forged bundles where dense Q/K/V parity remains unchanged.
