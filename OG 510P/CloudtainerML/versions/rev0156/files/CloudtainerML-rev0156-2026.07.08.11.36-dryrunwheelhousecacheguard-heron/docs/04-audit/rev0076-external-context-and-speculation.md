# rev0076 external context and speculation

This note records the online comparison used during the mission audit. It is contextual research, not evidence that CloudtainerML has reproduced any external result.

## What current practice says

### Tensor provenance is not enough; the replay equation must also be exact

The current Hugging Face Llama implementation forms projected Q/K/V, applies rotary position embeddings to Q/K, updates cache state, and only then passes those tensors to the attention interface. It also passes the attention scaling factor separately. A hook on `q_proj`/`k_proj` therefore captures an earlier object, while a bundle containing only post-transform Q/K can still be insufficient if scale and score bias/mask are omitted.

Architectures may vary further. GPT-2 configuration exposes options that change attention scaling by layer, and other families may apply score soft-capping or related transforms. `qkv_npz_v2` therefore supports one explicit rule—scaled dot product plus additive bias—and must reject unsupported transforms rather than quietly approximate them.

Hugging Face repositories support revisions that may be commits, tags, or branches. Reproducible public evidence should resolve and record immutable model and tokenizer commits; trusted remote model code must also be pinned independently when applicable.

### Competitive sparse attention is systems co-design

MInference combines dynamically constructed sparse indices with optimized GPU kernels and evaluates downstream tasks and named A100 prefill latency. Quest frames sparsity as query-aware KV-page selection and measures attention and inference latency. Native Sparse Attention explicitly co-designs hierarchical sparsity around arithmetic intensity and now has an experimental NVIDIA cuDNN Frontend implementation for Blackwell-class GPUs. SpargeAttention likewise evaluates an implemented training-free sparse/quantized path across models.

The common lesson is not that any one method is the answer. It is that selector quality alone is not the unit of proof. Index/mask construction, memory traffic, kernel shape, serving phase, model quality, sequence-length regime, and hardware are part of the mechanism.

PyTorch's FlexAttention documentation reinforces this: data-dependent BlockMask construction can be expensive, and its cost is only amortizable in specific reuse patterns. Any CloudtainerML cost model must charge construction and state when it is reused.

MLPerf Inference provides a useful reporting model: named systems, standard load scenarios, explicit metrics, quality targets, and compliance rules. CloudtainerML need not become MLPerf, but a promotional result should be similarly explicit about hardware and serving conditions.

## Internal lineage implication

The external emphasis on named configurations and immutable model revisions exposed a parallel internal weakness: a retained historical runner is not a fresh run merely because it executes in the current cube. The static audit found 60 Python runners/reports that can derive artifact names from the live revision, including 12 that combine that live revision with a hard-coded historical timestamp. The public-trace historical surfaces are now pinned; the rest should migrate only when touched, using explicit run identity, runtime timestamps, code/dependency hashes, and separate output namespaces.

## Speculation

1. **The enduring product may be the evaluator, not the sparse mechanism.** CloudtainerML's strongest distinctive asset is its insistence on hostile falsifiers and deployment vetoes. That machinery could become a general architecture claim compiler for KV compression, quantization, routing, recurrent memory, and cache policies.
2. **This sparse-attention lane is at the co-design threshold.** More NumPy/CPU selector variants are unlikely to resolve the remaining question. The next information gain comes from architecture-aware traces and a real GPU substrate—possibly FlexAttention/Triton or an NSA-like vendor path—not finer proxy arithmetic.
3. **A tiny gold corpus beats registry expansion.** A versioned set of real post-transform traces, exact score contracts, reference dense outputs, prompts across lengths/positions, and replay kernels would probably create more cumulative leverage than hundreds of loosely typed questions and source families.
4. **Negative results are already a deliverable.** Dense-score selection, metadata scans, materialization, and selector setup repeatedly erase nominal sparsity wins. Those failures should be consolidated into compact design laws rather than kept alive as many overlapping lanes.
5. **The current provenance gate is policy, not cryptographic proof of origin.** Hashes and immutable revisions protect consistency, while `provenance_reviewed=true` still relies on a reviewer. A future gold corpus should record reviewer identity, source retrieval receipts, runtime/package versions, and ideally independently reproducible exports.

## Sources

- Hugging Face Transformers Llama implementation: https://github.com/huggingface/transformers/blob/main/src/transformers/models/llama/modeling_llama.py
- Hugging Face model repository versioning: https://huggingface.co/docs/transformers/model_sharing
- Hugging Face GPT-2 configuration/implementation: https://github.com/huggingface/transformers/blob/main/src/transformers/models/gpt2/configuration_gpt2.py
- MInference 1.0: https://arxiv.org/abs/2407.02490
- Quest: https://arxiv.org/abs/2406.10774
- Native Sparse Attention paper: https://arxiv.org/abs/2502.11089
- NVIDIA cuDNN Frontend NSA: https://docs.nvidia.com/deeplearning/cudnn/fe-oss-apis/nsa.html
- SpargeAttention: https://arxiv.org/abs/2502.18137
- PyTorch FlexAttention: https://pytorch.org/blog/flexattention/
- MLPerf Inference Datacenter: https://mlcommons.org/benchmarks/inference-datacenter/
