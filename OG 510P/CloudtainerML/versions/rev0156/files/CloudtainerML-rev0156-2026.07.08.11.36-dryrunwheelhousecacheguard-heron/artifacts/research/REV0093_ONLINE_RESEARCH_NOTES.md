# Online research notes — REV0093

Generated: 2026-07-06T11:14:00-04:00  
Purpose: risk-first context for the public trace and hardware timing lane. These notes are not promotion evidence.

## Sources consulted

1. Hugging Face Transformers generation docs: https://huggingface.co/docs/transformers/en/main_classes/text_generation
   - Relevant facts: `max_new_tokens` is a maximum number of new tokens; `min_new_tokens` is separate; `do_sample=False` means greedy decoding unless beam search is enabled; `num_beams=1` means no beam search; `use_cache` controls past-key/value cache use; cache implementations include dynamic, static, offloaded, and quantized variants.
   - Cube implication: rev0091/rev0093 are right to require `min_new_tokens=max_new_tokens=decode_steps_requested`, single beam, single returned sequence, `use_cache=true`, and generated-token digests. A ceiling without exact-count verification is not a cached-decode coverage proof.

2. Hugging Face Transformers attention backend docs: https://huggingface.co/docs/transformers/en/attention_interface and https://huggingface.co/docs/transformers/attention_interface
   - Relevant facts: attention backends are configurable; mask creation is routed through `AttentionMaskInterface`; without a registered mask formatter for an active custom backend, mask creation can be skipped and `attention_mask=None` can reach attention layers; 4D masks have backend-specific conventions.
   - Cube implication: the capture path must preserve the built-in eager mask backend or prove equivalent mask construction. A custom attention hook that changes mask semantics invalidates public acceptance even when tensors have plausible shapes.

3. PyTorch SDPA docs: https://docs.pytorch.org/docs/2.12/generated/torch.nn.functional.scaled_dot_product_attention.html and https://docs.pytorch.org/docs/2.12/generated/torch.nn.attention.sdpa_kernel.html
   - Relevant facts: SDPA applies scale, additive/boolean masks, optional GQA broadcasting, softmax, dropout, and value multiplication; it can auto-select optimized kernels on CUDA; `sdpa_kernel` can constrain backend choice; dropout is applied according to `dropout_p`, so callers must pass `0.0` for eval behavior.
   - Cube implication: public trace rows must record scale, mask/bias, GQA ownership, probability dtype/softmax/dropout semantics, and backend constraints. Dense parity with unpinned dropout/backend semantics is not enough.

4. FlashAttention paper: https://arxiv.org/abs/2205.14135 and FlashAttention-2 paper: https://arxiv.org/abs/2307.08691
   - Relevant facts: the speed story is IO-aware exact attention, tiling, reduced HBM traffic, and better GPU work partitioning. The papers explicitly frame memory traffic and implementation details as decisive.
   - Cube implication: a sparse mechanism has to beat strong IO-aware exact baselines end to end. Skipping theoretical QK work but adding metadata/materialization/value-path traffic can lose.

5. vLLM/PagedAttention paper: https://arxiv.org/abs/2309.06180 and vLLM project page: https://vllm.ai/
   - Relevant facts: serving throughput is constrained by KV-cache memory growth, fragmentation, scheduling, and sharing. PagedAttention attacks cache allocation waste and can materially improve throughput under serving conditions.
   - Cube implication: named-hardware timing must include cache ownership, allocation, page/block metadata, reuse, request scheduling assumptions, and memory/tail latency. A row-level sparse replay is not a serving claim.

6. PyTorch FlexAttention docs and blog: https://docs.pytorch.org/docs/2.12/nn.attention.flex_attention.html and https://pytorch.org/blog/flexattention/
   - Relevant facts: FlexAttention exposes `score_mod`, `mask_mod`, `block_mask`, and block-mask utilities for custom attention patterns. Mask creation and kernel options are explicit parts of the API.
   - Cube implication: FlexAttention is the right modern comparison path for block/sparse patterns, but it also makes construction and block-mask costs measurable rather than ignorable.

## Risk conclusion

The external landscape makes the cube's next move sharper: do not add another registry-only trace gate unless a fresh source defect is found. The public-trace lane should be run through a real model with pinned generation/cache/mask semantics, then the performance lane should compare against SDPA/Flash/Flex/Paged-style implementations on named hardware.
