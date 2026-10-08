# Online research notes — REV0095

Status: non-promotional. These notes inform execution hardening only; they are not evidence of a successful public trace.

## Source lock

- Hugging Face renders `TinyLlama/TinyLlama-1.1B-Chat-v1.0` with `License: apache-2.0` and classifies it as a Transformers/Safetensors text-generation model. Source: https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0
- The selected tree `https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0/tree/fe8a4ea1ffedaf415f4da2f062534de366a451e6` renders short label `fe8a4ea`, marks the tree verified, and shows the model is about `2.2 GB`. This supports the existing full commit pin `fe8a4ea1ffedaf415f4da2f062534de366a451e6` and warns that a real runner needs disk/cache planning. Source: https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0/tree/fe8a4ea1ffedaf415f4da2f062534de366a451e6
- The card says TinyLlama adopts the same architecture and tokenizer family as Llama 2 and requires `transformers>=4.34` for basic use. The capture packet has stricter needs because it relies on modern attention-interface/mask behavior.

## Generation and cache implications

- HF generation docs define `max_new_tokens` and `min_new_tokens`; rev0091+ was right to require exact generated-token counts rather than treating `max_new_tokens` as proof of exactly produced tokens. Source: https://huggingface.co/docs/transformers/en/main_classes/text_generation
- The same docs define `do_sample`, `num_beams`, and `use_cache`; the packet should continue forcing greedy, single-beam, single-return-sequence, cached decoding.
- HF cache docs explain that KV cache avoids recomputing past K/V during autoregressive generation and that attention masks must cover past plus current tokens. This justifies the cube's insistence on active-key length, valid-key length, and decode-position provenance. Source: https://huggingface.co/docs/transformers/en/cache_explanation

## Attention backend implications

- HF attention-interface docs say `attn_implementation` selects the attention backend and that a custom attention backend must register a corresponding `AttentionMaskInterface`; otherwise mask creation can be skipped and `attention_mask=None` can reach layers. This is a severe semantic hazard for public trace capture, so the current packet preserves the built-in eager mask backend rather than introducing a custom backend name. Source: https://huggingface.co/docs/transformers/en/attention_interface
- PyTorch SDPA, FlashAttention, FlexAttention, and PagedAttention-style serving baselines make a pure algorithmic sparse-vs-dense FLOP story insufficient. The future timing lane must measure end-to-end prefill+decode, mask/block construction, cache layout, value path, and memory movement on named hardware.
- vLLM/PagedAttention research emphasizes KV-cache fragmentation/layout and serving throughput, not just row-wise score pruning. A sparse claim that ignores KV layout and batching can be wasteful even if a selector looks good in isolation. Sources: https://docs.vllm.ai/en/latest/design/paged_attention/ and https://arxiv.org/abs/2309.06180

## Actionable conclusion

rev0095 should not add another conceptual gate. The useful move is the `public_trace_env_preflight.py` gate: before attempting capture, it records imports, versions, HF cache state, download policy, free disk, and CUDA hardware. That makes the next failure precise and repairable.
