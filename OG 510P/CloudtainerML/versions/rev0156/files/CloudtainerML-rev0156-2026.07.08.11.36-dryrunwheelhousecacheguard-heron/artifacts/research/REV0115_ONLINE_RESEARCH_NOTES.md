# Online research notes — REV0115

Generated: `2026-07-06T18:05:00-04:00`  
Status: research notes only; no promotion evidence.

## Sources checked and pressure on the cube

- Hugging Face Transformers attention backends: `https://huggingface.co/docs/transformers/en/attention_interface`
  - The docs expose `attn_implementation` and runtime backend switching.
  - They also warn that a custom attention backend needs a matching mask registration or the attention layers can receive `attention_mask=None`. This strongly supports the cube's rev0081 decision to treat mask-preserving eager capture as a gate, not a convenience detail.
- Hugging Face KV-cache generation docs: `https://huggingface.co/docs/transformers/v4.47.1/kv_cache`
  - KV cache is described as a generation-time optimization that stores previous K/V states so token-by-token decoding does not recompute previous context. This supports the cube's emphasis on cached decode rather than prefill-only traces.
- TinyLlama model card: `https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0`
  - The card describes a 1.1B Llama-family model trained on 3T tokens and notes compatibility with Llama 2 architecture/tokenizer. It remains a reasonable small public target, but its small size means named-hardware timing should not be overgeneralized.
- FlashAttention: `https://arxiv.org/abs/2205.14135`
  - The paper's central pressure is IO awareness: exact attention can be much faster by reducing HBM traffic. Any sparse claim here must beat or fairly compare with IO-aware dense baselines.
- vLLM / PagedAttention: `https://arxiv.org/abs/2309.06180`
  - The paper highlights KV-cache fragmentation and duplication as serving bottlenecks and reports throughput gains from block/page-style memory management. CloudtainerML's cost lane must count KV layout and scheduling, not just mathematical score sparsity.
- PyTorch FlexAttention: `https://pytorch.org/blog/flexattention/`
  - FlexAttention makes new attention patterns easier to express and can use block masks, but the blog warns that data-dependent per-layer sparsity is harder because BlockMask construction may not amortize well. This is directly relevant to selector metadata overhead.
- H2O: `https://arxiv.org/abs/2306.14048`
  - H2O frames KV-cache eviction around recent plus heavy-hitter tokens. It is a relevant decode-time baseline if CloudtainerML's selector targets active working-set reduction.
- StreamingLLM: `https://arxiv.org/abs/2309.17453`
  - Attention sinks make naive sliding-window eviction risky; a sparse/cache policy that drops initial sink tokens can fail even when it looks efficient.
- MInference: `https://arxiv.org/abs/2407.02490`
  - MInference accelerates long-context prefill by using dynamic sparse patterns and custom kernels. It is a relevant prefill baseline but not a complete substitute for cached-decode evidence.
- SPIN: `https://arxiv.org/abs/2604.26837`
  - SPIN's abstract is especially aligned with this audit's speculation: sparse methods can fail to translate into system-level gains when granularities and CPU/GPU retrieval overhead are not co-designed.

## Research conclusion

The online check supports the cube's blockers rather than weakening them. Public trace semantics, exact cache/mask/position provenance, and named-hardware end-to-end timing are not bureaucratic extras. They are the only way to know whether a sparse mechanism survived the systems baseline.
