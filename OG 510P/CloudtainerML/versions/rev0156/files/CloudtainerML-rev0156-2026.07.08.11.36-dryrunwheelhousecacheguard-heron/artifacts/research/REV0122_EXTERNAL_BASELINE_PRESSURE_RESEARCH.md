# External baseline pressure research — REV0122

Status: `research_applied_non_promotional`  
Promotion allowed: `false`

Online research supports two conclusions: snapshot preparation and capture runtime should remain separate phases, and sparse-attention promotion must face modern exact-attention, compiled-mask, paged-KV, KV-eviction, and dynamic sparse prefill baselines.

- hf_snapshot_download: https://huggingface.co/docs/huggingface_hub/en/guides/download — snapshot_download supports pinned revision and filtered file download patterns
- transformers_offline: https://huggingface.co/docs/transformers/en/installation — offline Transformers requires downloaded/cached files ahead of time
- safetensors_header: https://huggingface.co/docs/safetensors/en/metadata_parsing — headers can be parsed cheaply without full tensor loading
- flashattention: https://arxiv.org/abs/2205.14135 — exact IO-aware attention is a baseline pressure for sparse claims
- pytorch_flexattention: https://pytorch.org/blog/flexattention/ — compiled flexible attention masks reduce the novelty/performance moat for custom variants
- vllm_pagedattention: https://arxiv.org/abs/2309.06180 — KV-cache memory management is a required serving baseline
- h2o: https://arxiv.org/abs/2306.14048 — KV eviction/heavy-hitter methods are a required efficient-memory baseline
- minference: https://arxiv.org/abs/2407.02490 — dynamic sparse attention for long-context prefill is a required sparse baseline
