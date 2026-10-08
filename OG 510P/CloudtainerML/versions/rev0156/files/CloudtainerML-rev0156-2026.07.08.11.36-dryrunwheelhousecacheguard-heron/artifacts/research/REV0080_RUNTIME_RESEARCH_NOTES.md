# Runtime research notes — rev0080

Generated: 2026-07-06T02:35:00-04:00

Purpose: keep the trace lane tied to current runtime reality, not registry language.

## Findings used in this revision

1. Current Hugging Face Llama source applies rotary position embedding to query/key before calling the attention interface. The eager implementation then repeats grouped KV heads, computes `query @ key.T * scaling`, adds the attention mask, softmaxes, and multiplies by values before `o_proj`. That confirms the public capture boundary must be after RoPE and must record scale and additive score bias, not just raw projection Q/K.
   - Source: https://github.com/huggingface/transformers/blob/main/src/transformers/models/llama/modeling_llama.py

2. Current Hugging Face attention backends are selected through an attention interface, with options including eager, SDPA, FlashAttention variants, FlexAttention, and paged variants. This makes a module-only monkey patch risky: the capture wrapper should also install a unique registry/backend path or fail closed if no calls are captured.
   - Source: https://huggingface.co/docs/transformers/en/attention_interface

3. PyTorch FlexAttention for inference discusses BlockMask and paged attention conversion from logical to physical KV blocks; the correctness issue is index/mask semantics under indirection, while the performance issue is avoiding redundant materialization/copies. That reinforces that CloudtainerML must measure sparse/index/mask construction costs, not only selector quality.
   - Source: https://pytorch.org/blog/flexattention-for-inference/

4. vLLM's PagedAttention documentation stores KV cache in fixed-size blocks per head and assigns warps/thread blocks over those blocks. Any CloudtainerML sparse-runtime claim must therefore name the KV layout, page/block size assumptions, and hardware path.
   - Source: https://docs.vllm.ai/en/latest/design/paged_attention/

5. Recent sparse-attention-serving work such as SPIN reports end-to-end gains only when sparse attention is co-designed with hierarchical KV storage, metadata layout, and locality-aware management. This is a useful outside pressure: algorithm-only sparsity is not enough evidence for promotion.
   - Source: https://arxiv.org/abs/2604.26837

## Decision pressure

The next non-wasteful move is still execution: provide or download a reviewed immutable public Llama-family snapshot, run the hardened adapter, pass the public trace gate, then measure named-hardware sparse-vs-dense including index/mask construction. If that cannot happen, stop or pivot the sparse-attention lane rather than adding more trace governance.
