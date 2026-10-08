# Mission audit — REV0102

Status: `pass_with_blockers`  
Promotion allowed: `false`

## What changed

rev0102 advances the riskiest unfinished lane: the real public TinyLlama trace. The prior packet pinned eager attention, dynamic cache, immutable source identity, generated-token counts, and token digests, but prompt text itself was still too easy to recover only from command history rather than a gate-checked replay manifest.

This revision adds:

- `prompt_manifest_contract = prompt_text_tokenizer_call_manifest_v1`
- `token_provenance_contract = prompt_input_ids_attention_mask_digest_v2`
- explicit tokenizer call settings: `add_special_tokens=True`, `padding=False`, `truncation=False`, `return_attention_mask=True`, `return_tensors=pt`, `chat_template_applied=False`
- `tools/public_trace_prompt_manifest_audit.py`, which rejects a forged prompt-text manifest while leaving dense Q/K/V parity intact

## Online research basis

Hugging Face tokenizer docs describe tokenizers as the model-input preparation layer and distinguish fast/Rust and Python implementations. Chat-template docs warn that special tokens and chat templates can interact incorrectly when tokenization is applied later. That makes prompt text plus tokenization settings part of trace provenance, not cosmetic metadata.

## Refactor performed

Top-level reentry now says one thing: run `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`. The stable alias points at REV0102 wrappers, and the readiness gate runs the prompt-manifest audit before capture.

## What remains blocked here

- `transformers_not_importable_runtime_surface_unchecked`
- `complete_tinyllama_snapshot_not_available`
- `hf_snapshot_network_dry_run_not_successful_here`
- `cuda_not_available_for_named_hardware_timing`
- `actual_public_pretrained_prefill_plus_cached_decode_dynamic_cache_prompt_manifest_trace_missing`

## Decision

Do not add another registry. Repair the environment/snapshot blockers, keep eager attention and dynamic cache, preserve the raw-prompt tokenization contract, then run the stable public-trace alias. Static/offloaded/quantized caches and chat-template variants are later baseline/timing lanes unless they receive separate contracts.
