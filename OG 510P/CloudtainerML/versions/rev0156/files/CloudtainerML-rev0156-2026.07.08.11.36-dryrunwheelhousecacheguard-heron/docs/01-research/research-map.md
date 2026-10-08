# Research map — CloudtainerML rev0002

The current research map is organized around testable tiny-scale mechanisms rather than product outcomes.

## architecture-primitive

- `SRC-0011` **Dynamic Short Convolutions Improve Transformers** (2606.03825). Priority: P0. Cloudtainer test: Add tiny dynamic local filters before Q/K/V in a small attention model; test if local context preconditioning helps associative recall at small scale.

## associative-memory-theory

- `SRC-0025` **Context-Gated Associative Retrieval: From Theory to Transformers** (2605.10970). Priority: P1. Cloudtainer test: Hopfield toy: compare ungated vs context-gated memory under ambiguous keys and category-conditioned recall.

## associative-model-editing

- `SRC-0026` **HoReN: Normalized Hopfield Retrieval for Large-Scale Sequential Model Editing** (2605.08143). Priority: P2. Cloudtainer test: Tiny parameter-preserving edit memory: store thousands of synthetic key edits, test interference/paraphrase/no-op stability.

## bounded-growable-memory

- `SRC-0032` **Key-Value Means: Transformers with Expandable Block-Recurrent Memory** (2605.09877). Priority: P0. Cloudtainer test: Block-level cluster/mean memory: grow compressed state only when novelty exceeds threshold; test retention and interference.

## bounded-writable-kv

- `SRC-0031` **Trellis: Learning to Compress Key-Value Memory in Attention Models** (2512.23852). Priority: P0. Cloudtainer test: Fixed-slot KV memory with learned write/forget gate; compare to ring buffer, reservoir, and top-attention eviction.

## cache-as-representation

- `SRC-0002` **Beyond Speedup -- Utilizing KV Cache for Sampling and Reasoning** (2601.20326). Priority: P0. Cloudtainer test: Treat KV tensors from a tiny model as embeddings; test whether cache-derived features predict answer correctness, uncertainty, or need-more-steps on generated tasks.

## constant-memory-recall

- `SRC-0005` **Echo: KV-Cache-Free Associative Recall with Spectral Koopman Operators** (2605.06997). Priority: P0. Cloudtainer test: Implement the smallest kernel-ridge/spectral-memory analog and benchmark against attention, additive linear attention, and delta-rule memory on multi-query associative recall.

## context-absorption

- `SRC-0037` **Absorber LLM: Harnessing Causal Synchronization for Test-Time Training** (2604.20915). Priority: P2. Cloudtainer test: Teacher-full-context vs student-absorbed-memory toy; match future logits after streaming context is removed.

## grokking-geometry

- `SRC-0056` **The Geometric Inductive Bias of Grokking** (2603.05228). Priority: P2. Cloudtainer test: Modular arithmetic grokking with bounded residual stream, uniform attention, and negative-control noncommutative tasks.

- `SRC-0057` **Latent Algorithmic Structure Precedes Grokking** (2603.23784). Priority: P2. Cloudtainer test: Probe early-trained models for Fourier/square-wave structure before validation accuracy rises.

## head-budgeting

- `SRC-0045` **Which Heads Matter for Reasoning? RL-Guided KV Cache Compression** (2510.08525). Priority: P1. Cloudtainer test: Head-drop ablations in tiny multi-head model; learn a head budget policy from final-task reward.

## hybrid-score-fusion

- `SRC-0012` **Forget Attention: Importance-Aware Attention Is All You Need** (2606.02332). Priority: P1. Cloudtainer test: Score-level fusion toy: add a learned recurrent importance scalar/vector to attention logits; test if needle retrieval converges faster.

## hybrid-sequence-axis

- `SRC-0013` **Multi-Mixer Models: Flexible Sequence Modeling with Shared Representations** (2605.28769). Priority: P0. Cloudtainer test: Synthetic router: decide per segment whether to use attention or cheap recurrence; train/evaluate routing masks under memory and accuracy budgets.

## hybrid-theory

- `SRC-0014` **Expressivity-Efficiency Tradeoffs for Hybrid Sequence Models** (2603.08859). Priority: P1. Cloudtainer test: Reproduce tiny separations: pure attention vs pure recurrence vs hybrid on selective copying and associative recall at matched working-memory budgets.

## icl-geometry

- `SRC-0059` **Geometric Scaling of Bayesian Inference in LLMs** (2512.23752). Priority: P2. Cloudtainer test: Bayesian coin/urn wind-tunnel: train tiny Transformer and probe entropy-aligned value axes.

## in-context-learning

- `SRC-0058` **Dissecting Multimodal In-Context Learning** (2601.20796). Priority: P2. Cloudtainer test: Non-image toy modality pairing: symbol stream plus numeric/code stream; test cross-channel in-context binding.

## kv-compression

- `SRC-0047` **Mixed-Dimension Budget Allocation for Efficient KV Cache Compression** (2603.20616). Priority: P2. Cloudtainer test: Dimension dropout per token: test whether keeping a few dimensions from many tokens beats keeping full vectors for fewer tokens.

## kv-quantization

- `SRC-0001` **KVarN: Variance-Normalized KV-Cache Quantization Mitigates Error Accumulation in Reasoning Tasks** (2606.03458). Priority: P0. Cloudtainer test: Pseudo-decode tiny-transformer/tensor-only probe: measure scale error, top-error outliers, and accuracy collapse vs decode length under fp32/int4/int2 variants.

- `SRC-0046` **Adaptive KV-Cache Quantization for Lightweight On-Device LLMs** (2604.04722). Priority: P1. Cloudtainer test: Feature-based bit controller: allocate fp16/int8/int4/int2 to synthetic cache tokens, optimize accuracy-memory Pareto.

## kv-quantization-geometry

- `SRC-0048` **OCTOPUS: Optimized KV Cache for Transformers via Joint Coordinate Quantization** (2605.21226). Priority: P2. Cloudtainer test: Toy compare scalar quantization vs grouped-coordinate quantization under attention-inner-product preservation.

- `SRC-0050` **Offline Spectral Covariance-Aware Rotation for 2-bit KV Cache Quantization** (2605.17757). Priority: P1. Cloudtainer test: Estimate covariance from calibration traces; compare random/Hadamard/PCA/covariance rotations under 2-bit cache.

## kv-transform-coding

- `SRC-0049` **KV Cache Transform Coding for Compact Storage in LLM Serving** (2511.01815). Priority: P1. Cloudtainer test: KV transform coding on collected tiny-model cache tensors: PCA/DCT/identity transforms vs quantization error and task loss.

## latent-attention

- `SRC-0015` **Compressed Convolutional Attention: Efficient Attention in a Compressed Latent Space** (2510.04476). Priority: P1. Cloudtainer test: Latent attention zoo: MHA/GQA/MLA/CCA variants at equal latent dimension and memory bytes on recall and induction tasks.

- `SRC-0016` **Towards Economical Inference: Enabling Multi-Head Latent Attention in Any Transformer-based LLMs** (2502.14837). Priority: P2. Cloudtainer test: Train-from-scratch tiny MLA instead of conversion; isolate how latent rank affects content-addressed recall.

## learned-forgetting

- `SRC-0003` **Neural Garbage Collection: Learning to Forget while Learning to Reason** (2604.18002). Priority: P0. Cloudtainer test: Mini RL/bandit forgetting loop on generated arithmetic or symbolic tasks: choose which scratch/KV slots to drop, reward final accuracy plus memory budget.

- `SRC-0004` **Self-Pruned Key-Value Attention** (2605.14037). Priority: P1. Cloudtainer test: Supervised utility predictor from synthetic traces: can early token features predict later attention/retrieval utility better than attention mass alone?

## learned-retention

- `SRC-0042` **Cache What Lasts: Token Retention for Memory-Bounded KV Cache in LLMs** (2512.03324). Priority: P1. Cloudtainer test: Train a small retention gate from an oracle full-attention model on synthetic tasks; test transfer to longer contexts.

## length-generalization-theory

- `SRC-0020` **Length Generalization Bounds for Transformers** (2603.02238). Priority: P2. Cloudtainer test: Use as caution: never infer true length-generalization from short sweeps; include adversarial length sweeps and exact finite automata baselines.

## linear-attention

- `SRC-0006` **Kaczmarz Linear Attention** (2605.08587). Priority: P1. Cloudtainer test: Toy row-projection memory update: compare iterative correction vs additive/delta writes under key collisions and increasing pair count.

- `SRC-0007` **Variational Linear Attention: Stable Associative Memory for Long-Context Transformers** (2605.11196). Priority: P1. Cloudtainer test: Implement the normalized write + Sherman-Morrison update in small dimensional settings; chart capacity boundary vs head dimension.

- `SRC-0008` **Gated DeltaNet-2: Decoupling Erase and Write in Linear Attention** (2605.22791). Priority: P1. Cloudtainer test: Tiny delta-rule fast-weight arena with separate erase/write gates: does disentangling erase/write reduce interference in repeated-key updates?

- `SRC-0009` **Kimi Linear: An Expressive, Efficient Attention Architecture** (2510.26692). Priority: P1. Cloudtainer test: Abstract the gate granularity knob only; compare scalar, channel-wise, and low-rank gates on controlled recall/update tasks.

## local-linear-attention

- `SRC-0051` **Parallax: Parameterized Local Linear Attention for Language Modeling** (2605.29157). Priority: P2. Cloudtainer test: Local-linear estimator attention toy: does covariance probing help on noisy key-value retrieval?

## looped-transformers

- `SRC-0022` **Looped Transformers for Length Generalization** (2409.15647). Priority: P1. Cloudtainer test: Compare fixed-depth vs looped tiny models on addition/parity/pointer-chasing; track step budget vs extrapolation.

- `SRC-0023` **Chain-of-Thought and Compressed Looped Transformers** (2605.30757). Priority: P1. Cloudtainer test: Compressed-loop arena: hidden-state-only loops vs full sequence-state loops vs explicit scratchpad tokens.

## mechanistic-algorithms

- `SRC-0019` **Discovering Interpretable Algorithms by Decompiling Transformers to RASP** (2602.08857). Priority: P0. Cloudtainer test: Train tiny models on sort/select/parity/bracket tasks; attempt hand-lite decompilation by tracing attention masks, MLP thresholds, and ablation sufficiency.

## memory-consolidation

- `SRC-0035` **Mela: Test-Time Memory Consolidation based on Transformation Hypothesis** (2605.10537). Priority: P1. Cloudtainer test: Two-rate memory toy: separate slow gist slots and fast episodic slots; test corrections, abstraction, and distractor resistance.

## memory-driven-reasoning

- `SRC-0038` **MemCoT: Test-Time Scaling through Memory-Driven Chain-of-Thought** (2604.08216). Priority: P2. Cloudtainer test: Not an LLM benchmark target; adapt as planner over a synthetic evidence graph where each step chooses search radius and memory state.

## memory-geometry

- `SRC-0024` **Attractor Geometry of Transformer Memory: From Conflict Arbitration to Confident Hallucination** (2605.05686). Priority: P0. Cloudtainer test: Create synthetic fact-memory task with installed facts and absent facts; compare output entropy, nearest-basin distance, and hidden-state margins.

## parametric-memory

- `SRC-0053` **STEM: Scaling Transformers with Embedding Modules** (2601.10639). Priority: P2. Cloudtainer test: Token-indexed memory table in a tiny decoder/sequence model; test editable facts and retrieval interference.

## persistent-memory-bank

- `SRC-0052` **Mixture of Chapters: Scaling Learnt Memory in Transformers** (2603.21096). Priority: P2. Cloudtainer test: Tiny routed memory-bank model: do chapter routers specialize on synthetic fact families and resist forgetting?

## position-encoding

- `SRC-0017` **CoPE: Clipped RoPE as A Scalable Free Lunch for Long Context LLMs** (2602.05258). Priority: P1. Cloudtainer test: RoPE vs hard clip vs soft clip on train-short/eval-long key-value retrieval, induction, and formal-language tasks.

## prefix-scannable-models

- `SRC-0060` **Sequential-Parallel Duality in Prefix Scannable Models** (2506.10918). Priority: P2. Cloudtainer test: Use prefix-scan framing as an implementation sanity lens for recurrence variants; prefer associative update operators when possible.

## reasoning-cache

- `SRC-0039` **Crystal-KV: Efficient KV Cache Management for Chain-of-Thought LLMs via Answer-First Principle** (2601.16986). Priority: P1. Cloudtainer test: Generated proof/task traces: label tokens that affect final answer vs flow only; test answer-first eviction against recency/attention baselines.

- `SRC-0041` **LongFlow: Efficient KV Cache Compression for Reasoning Models** (2603.11504). Priority: P1. Cloudtainer test: Current-query-only importance estimator vs rolling history estimator in long generated traces.

- `SRC-0043` **LazyEviction: Lagged KV Eviction with Attention Pattern Observation for Efficient Long Reasoning** (2506.15969). Priority: P1. Cloudtainer test: Construct periodic-use tokens and delayed recurrence; measure when lagged eviction beats greedy eviction.

- `SRC-0044` **SkipKV: Selective Skipping of KV Generation and Storage for Chain-of-Thought Reasoning** (2512.07993). Priority: P2. Cloudtainer test: Segment-level vs token-level compression on generated structured explanations; track loop/revalidation behavior.

## reasoning-cache-benchmark

- `SRC-0040` **Semantic Integrity Matters: Benchmarking and Preserving High-Density Reasoning in KV Cache Compression** (2502.01941). Priority: P1. Cloudtainer test: Build high-density synthetic trace tasks where every step is semantically coupled; compare token-level vs segment-level cache dropping.

## sparse-attention

- `SRC-0018` **Long-Context Generalization with Sparse Attention** (2506.16640). Priority: P1. Cloudtainer test: Softmax vs entmax/sparsemax/top-k on increasing distractor length; measure focus collapse and wrong-needle rate.

## state-space

- `SRC-0010` **Mamba-3: Improved Sequence Modeling using State Space Principles** (2603.15569). Priority: P2. Cloudtainer test: Not reproduce full Mamba; test complex vs real recurrent state in a generated state-tracking microbench.

## state-tracking

- `SRC-0054` **Chess-World-Model: A 10M-Game Benchmark for Exact State Tracking from Chess Move Sequences** (2605.30100). Priority: P1. Cloudtainer test: Start smaller than chess: stack/automaton/grid move-state tracking; later use mini-board or public move generator if desired.

## test-time-memory

- `SRC-0028` **Titans: Learning to Memorize at Test Time** (2501.00663). Priority: P0. Cloudtainer test: Surprise-gated memory micro-version: compare attention-only, recurrent memory, and surprise-updated memory on associative recall with changing facts.

- `SRC-0029` **ATLAS: Learning to Optimally Memorize the Context at Test Time** (2505.23735). Priority: P0. Cloudtainer test: Batch/past-token memory optimization vs single-token online update on sequences with later corrections and multi-hop retrieval.

## test-time-memory-critical

- `SRC-0030` **Titans Revisited: A Lightweight Reimplementation and Critical Analysis of a Test-Time Memory Model** (2510.09551). Priority: P0. Cloudtainer test: Every Titans-like cell must include strong baselines and ablations; treat original claims as hypotheses, not facts.

## test-time-training

- `SRC-0033` **End-to-End Test-Time Training for Long Context** (2512.23675). Priority: P1. Cloudtainer test: Tiny fast-weight adapter updates over a stream; compare to explicit memory slots on held-out recall queries.

- `SRC-0034` **Test-Time Training Done Right** (2505.23884). Priority: P2. Cloudtainer test: Chunk-size sweep for fast-weight updates in CPU setting; measure capacity vs cost for generated memory tasks.

## training-dynamics

- `SRC-0055` **Slower Generalization, Faster Memorization: A Sweet Spot in Structured-Output Learning** (2605.14659). Priority: P2. Cloudtainer test: Structured-output matrix tasks at varied data sizes; look for non-monotonic data-size sweet spots on CPU.

## transformer-theory

- `SRC-0021` **Softmax Transformers are Turing-Complete** (2511.20038). Priority: P2. Cloudtainer test: Not a reproduction target; use to motivate tiny computational-language tasks and careful distinction between expressivity and trainability.

## working-memory

- `SRC-0036` **Gated Differentiable Working Memory for Long-Context Test-Time Adaptation** (2601.12906). Priority: P1. Cloudtainer test: Budgeted gradient allocation: can a tiny controller choose which chunks deserve memory-write steps?

## writable-memory

- `SRC-0027` **GradMem: Learning to Write Context into Memory with Test-Time Gradient Descent** (2603.13875). Priority: P0. Cloudtainer test: Write/read key-value task: compare learned forward writer, gradient-written tokens, recurrent memory, and full-context oracle at fixed memory slots.
