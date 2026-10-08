# Rev0026 scout notes — performance core

This revision keeps CloudtainerML focused on tiny-scale performance and architecture surprise. The fresh hunt emphasized sparse FFN designs, adaptive low-rank KV compression, sparse-state linear attention, and critical-layer compression.

## New sources

- `SRC-0301`: Sparsity Moves Computation — FFN architecture can redistribute computation into attention in small transformers.
- `SRC-0302`: STAR-KV — adaptive soft-thresholded rank control, K/V-asymmetric decomposition, and low-rank-aware mixed precision.
- `SRC-0303`: Sparsely gated tiny linear experts — single-neuron linear experts selected sparsely may improve isoFLOP performance and interpretability.
- `SRC-0304`: Sparse State Expansion — row-sparse linear-attention state partitions as an interference repair.
- `SRC-0305`: AutoCompress / Critical Layer Isolation — protecting task-critical layers can beat uniform bottlenecks, but the critical layer may move.
- `SRC-0306`: Routing-consistent MoE quantization — preserve expert selection, not just MSE.

## New code

- `experiments/ffn_attention_redistribution/ffn_attention_redistribution.cpp`
- `experiments/starkv_soft_threshold_hpo/starkv_soft_threshold_hpo.cpp`
- `experiments/sgatlin_tiny_linear_experts/sgatlin_tiny_linear_experts.cpp`
- `experiments/sparse_state_expansion/sparse_state_expansion.cpp`
- `experiments/critical_layer_isolation/critical_layer_isolation.cpp`

## Recommendation

The strongest next trained-tiny escalation is either **FFN/attention redistribution** or **STAR-KV rank allocation**. The strongest native HPO hardening target is **STAR-KV soft-threshold rank selection with real random matrices/SVD**.
