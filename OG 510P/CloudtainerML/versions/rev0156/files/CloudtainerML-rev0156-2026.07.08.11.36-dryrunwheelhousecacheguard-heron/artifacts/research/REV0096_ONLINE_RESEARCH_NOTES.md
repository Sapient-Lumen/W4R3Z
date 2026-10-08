# Online research notes — REV0096

Status: `research_applied_to_runtime_snapshot_probe`  
Promotion allowed: `false`

## Findings applied to code

1. TinyLlama remains a suitable small public target for a first real trace because its Hugging Face page exposes a normal Transformers loading path, Apache-2.0 license, safetensors model file, and Llama-family architecture/tokenizer claim. Sources: `https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0`, `https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0`.
2. The exact snapshot blocker is now concrete. The HF files page shows this target needs `config.json`, `generation_config.json`, `model.safetensors`, `special_tokens_map.json`, `tokenizer.json`, `tokenizer.model`, and `tokenizer_config.json`; rev0096 adds `tools/hf_snapshot_materializer.py` to verify or download those exact files at the locked revision. Source: `https://huggingface.co/TinyLlama/TinyLlama-1.1B-Chat-v1.0/tree/main`.
3. Offline use is not just a boolean. Transformers docs require files downloaded/cached ahead of time for offline/firewalled use, while Hugging Face Hub download docs emphasize version-aware cache paths and `snapshot_download`; rev0096 moves that into an executable materializer rather than leaving it as prose. Sources: `https://huggingface.co/docs/transformers/en/installation`, `https://huggingface.co/docs/huggingface_hub/en/guides/download`.
4. The compatibility risk got sharper: current Transformers documentation and releases have moved forward from the older TinyLlama-card minimum (`transformers>=4.34`). Because this cube hooks internal Llama eager-attention surfaces, rev0096 adds `tools/transformers_llama_surface_probe.py` before capture instead of assuming any installed version works. Sources: `https://huggingface.co/docs/transformers/en/installation`, `https://github.com/huggingface/transformers/releases`.
5. Generation and cache semantics remain part of evidence, not convenience flags. `max_new_tokens`, `min_new_tokens`, greedy single-beam controls, `use_cache`, and cache class behavior are execution facts that affect rows and token provenance. Sources: `https://huggingface.co/docs/transformers/en/main_classes/text_generation`, `https://huggingface.co/docs/transformers/en/kv_cache`.
6. Timing still cannot be promoted by theoretical sparsity. PyTorch SDPA and vLLM/PagedAttention-style cache-management baselines make dense/backend/KV-layout costs central; the trace path must later compare on named hardware. Sources: `https://docs.pytorch.org/docs/stable/generated/torch.nn.functional.scaled_dot_product_attention.html`, `https://arxiv.org/abs/2309.06180`.

## Speculative call

The highest risk is no longer choosing the wrong public model. It is failing late because the runtime surface changed or the exact snapshot is absent. This revision therefore spends its effort on runtime/snapshot probes and a stable active wrapper, not another registry pass.
