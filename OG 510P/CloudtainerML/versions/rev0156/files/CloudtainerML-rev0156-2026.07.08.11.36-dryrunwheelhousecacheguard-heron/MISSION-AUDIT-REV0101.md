# Mission audit — REV0101

Status: `pass_with_blockers`  
Promotion allowed: `false`

## What changed

rev0101 advances the riskiest unfinished lane: the real public TinyLlama trace. The prior packet pinned deterministic greedy generation (`do_sample=false`, `num_beams=1`, exact `min_new_tokens=max_new_tokens=DECODE_STEPS`) but still trusted the generation cache implementation to be the runtime default or inherited config. That is too loose for a public score-path trace.

This revision adds an explicit cache contract:

- `cache_implementation_contract = hf_generate_dynamic_cache_v1`
- `generation_cache_implementation = dynamic`
- `generation_cache_implementation_source = explicit_generate_argument`
- `generation_cache_config_present = false`

The capture helper now passes `cache_implementation="dynamic"` to `model.generate(...)`, records it in the NPZ/provenance, and the surrogate gate rejects forged static/offloaded/quantized-cache metadata.

## Online research basis

Hugging Face generation documents `use_cache` and `cache_implementation`; supported cache implementations include `dynamic`, `static`, `offloaded`, `offloaded_static`, and `quantized`. The cache-strategy docs also show offloaded cache modes can be selected from `GenerationConfig` or `generate()`, and the cache explanation notes cache layer types differ in how sequence length is handled and updated. Those facts make cache implementation part of trace semantics, not an incidental runtime detail.

Sources reviewed:

- https://huggingface.co/docs/transformers/en/main_classes/text_generation
- https://huggingface.co/docs/transformers/kv_cache
- https://huggingface.co/docs/transformers/cache_explanation
- https://huggingface.co/docs/transformers/en/attention_interface

## Refactor performed

Top-level reentry now says one thing: run `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh` with `CACHE_IMPLEMENTATION=dynamic`. Historical wrappers remain as provenance only. The new audit is `tools/public_trace_cache_implementation_audit.py`; it writes `artifacts/audit/REV0101_PUBLIC_TRACE_CACHE_IMPLEMENTATION_AUDIT.*`.

## What remains blocked here

- `transformers_not_importable_runtime_surface_unchecked`
- `complete_tinyllama_snapshot_not_available`
- `hf_snapshot_network_dry_run_not_successful_here`
- `cuda_not_available_for_named_hardware_timing`
- `actual_public_pretrained_prefill_plus_cached_decode_dynamic_cache_trace_missing`

## Decision

Do not add another registry. Repair the environment/snapshot blockers, keep `ATTENTION_IMPLEMENTATION=eager` and `CACHE_IMPLEMENTATION=dynamic`, then run the stable public-trace alias. Static/offloaded/quantized caches are useful timing/baseline lanes after the public score-path trace is accepted, not before.
