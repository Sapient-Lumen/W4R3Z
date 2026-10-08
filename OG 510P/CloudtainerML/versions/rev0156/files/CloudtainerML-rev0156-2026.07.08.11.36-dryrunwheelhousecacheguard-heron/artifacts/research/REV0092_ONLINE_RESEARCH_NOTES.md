# Online research notes — rev0092

Purpose: contextual support for the mission/waste/pivot read.

- Hugging Face Transformers GenerationConfig defines `max_new_tokens` as a maximum and `min_new_tokens` as a minimum number of new tokens, supporting the rev0091 exact-length generated-token gate.
- Hugging Face generation strategy docs distinguish greedy search, sampling, and beam search; the cube is right to pin greedy single-beam settings for replayable cached decode.
- Hugging Face AttentionInterface docs warn that registering custom attention without a matching mask function can drop mask creation and pass `attention_mask=None`; the cube is right to treat mask preservation as a semantic veto.
- PyTorch/Hugging Face SDPA and FlashAttention docs/papers emphasize fused kernels, memory traffic, and IO-awareness; sparse proxy arithmetic is not promotion evidence.
- PagedAttention/vLLM and newer sparse-serving work make KV-cache memory management and retrieval substrate part of the real baseline frontier.

Use these notes as context only; they do not promote the sparse-attention lane.
