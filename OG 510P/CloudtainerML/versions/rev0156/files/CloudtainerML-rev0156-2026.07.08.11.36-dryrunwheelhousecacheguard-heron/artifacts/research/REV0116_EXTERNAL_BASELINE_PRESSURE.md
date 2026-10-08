# External baseline pressure — REV0116

Status: `research_context_not_promotion_evidence`  
Promotion allowed: `false`

This pass researched current attention/runtime pressure so the cube does not keep adding bureaucracy around a weak or obsolete claim. These notes are intentionally framed as pressure on the next executable work, not as evidence that CloudtainerML wins anything.

## Bottom line

The strongest outside signal is that sparse-attention claims must now survive a systems baseline bracket: IO-aware exact attention, flexible compiler-generated masks, paged KV serving, attention-sink/window streaming, heavy-hitter KV retention, and dynamic sparse prefill systems. CloudtainerML should therefore spend turns on **trace -> receipt -> handoff -> timing**, not on more registry doctrine.

## Sources and pressure

### PyTorch FlexAttention and FlashAttention-4 pressure

- Source: FlexAttention + FlashAttention-4: Fast and Flexible
- URL: https://pytorch.org/blog/flexattention-flashattention-4-fast-and-flexible/
- Pressure on cube: Custom sparse/flexible masks are no longer enough; the cube must show exact semantics plus compiler/kernel-grade execution pressure, or explicitly stay in verifier/product mode.

### PyTorch FlexAttention inference backend

- Source: FlexAttention Part II: FlexAttention for Inference
- URL: https://pytorch.org/blog/flexattention-for-inference/
- Pressure on cube: Paged/decoding-oriented attention support means a sparse selector must be compared against runtime-aware baselines, not only dense math fixtures.

### vLLM / PagedAttention

- Source: vLLM project site and repository
- URL: https://vllm.ai/ ; https://github.com/vllm-project/vllm
- Pressure on cube: Serving systems attack latency through KV paging, scheduling, batching, graph execution, and memory management; CloudtainerML should make a named-hardware baseline bracket mandatory.

### PagedAttention paper

- Source: Efficient Memory Management for Large Language Model Serving with PagedAttention
- URL: https://arxiv.org/abs/2309.06180
- Pressure on cube: KV memory waste is a first-class baseline; sparse reads are not enough if paging and batching dominate end-to-end performance.

### FlashAttention-3

- Source: FlashAttention-3: Fast and Accurate Attention with Asynchrony and Low-precision
- URL: https://arxiv.org/abs/2407.08608 ; https://tridao.me/blog/2024/flash3/
- Pressure on cube: Exact dense attention is a moving target on modern GPUs; any sparse claim must compare against IO-aware kernels on named hardware.

### MInference

- Source: MInference 1.0: Accelerating Pre-filling for Long-Context LLMs via Dynamic Sparse Attention
- URL: https://arxiv.org/abs/2407.02490 ; https://github.com/microsoft/MInference
- Pressure on cube: Sparse long-context acceleration exists in stronger forms; this cube needs hostile comparisons and workload boundaries, not generic sparse wins.

### H2O / KV cache eviction

- Source: H2O: Heavy-Hitter Oracle for Efficient Generative Inference of Large Language Models
- URL: https://arxiv.org/abs/2306.14048 ; https://proceedings.neurips.cc/paper_files/paper/2023/file/6ceefa7b15572587b78ecfcebb2827f8-Paper-Conference.pdf
- Pressure on cube: The right comparison may be a KV retention policy, not a score sparsity policy. Decode-phase memory traffic is a central risk.

### StreamingLLM / attention sinks

- Source: Efficient Streaming Language Models with Attention Sinks
- URL: https://arxiv.org/abs/2309.17453 ; https://proceedings.iclr.cc/paper_files/paper/2024/hash/5e5fd18f863cbe6d8ae392a93fd271c9-Abstract-Conference.html
- Pressure on cube: Attention-sink plus window baselines can preserve behavior with bounded cache; generated-token/decode tests matter more than prefill-only fixtures.

### TinyLlama source identity

- Source: TinyLlama/TinyLlama-1.1B-Chat-v1.0 Hugging Face model card
- URL: https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0
- Pressure on cube: The real trace path must use immutable model/tokenizer revisions and local snapshot review; otherwise it is not public evidence.

## Speculation

The sparse lane is most likely to fail as a general-purpose claim and most likely to survive as either a narrow workload/hardware result or a reusable verifier discipline. If the real TinyLlama trace cannot be produced promptly, the honest pivot is to package the claim-compiler toolchain rather than keep generating audits around absent evidence.
