# CloudtainerML rev0080 — attention registry seam/readiness hardening

**Package:** `CloudtainerML-rev0080-2026.07.06.02.35-registryseamreadiness-goldfinch`  
**Archive:** `CloudtainerML-rev0080-2026.07.06.02.35-registryseamreadiness-goldfinch.zip`  
**Generated:** 2026-07-06T02:35:00-04:00  
**Status:** non-promotional adapter hardening; no accepted public/pretrained trace and no GPU/fused timing.  
**Primary new artifact:** `MISSION-AUDIT-REV0080.md`  
**Substantive code change:** AttentionInterface registry-aware wrapper in `experiments/public_trace_capture/hf_attention_trace_capture.py`.  
**Next acceptable deliverable:** provide/run an immutable public Llama-family checkpoint through the hardened adapter and gate, or stop/pivot the lane.

---

# Mission audit — rev0080

## What changed

rev0080 targets the riskiest live failure mode: the real-model capture helper might have appeared ready while silently missing the current Hugging Face AttentionInterface backend path. The helper now installs a unique `cloudtainer_trace_eager` backend when the registry exists and still patches the module-level eager fallback for older releases. The capture output/provenance records the active backend and whether registry installation happened.

## Why this is substantive

The cube does not need another registry pass. It needs the real post-transform trace path to either run or fail honestly. A module-only monkey patch could have failed to observe real attention calls under current backend selection. This revision makes that seam executable and audited: `tools/real_model_trace_adapter_audit.py` now checks dense parity and a fake registry-wrapper fixture; `tools/public_trace_capture_readiness_audit.py` checks whether the capsule can actually run a public checkpoint capture.

## Online research pressure

Current Hugging Face Llama source applies RoPE before the attention interface, then eager attention repeats KV heads, computes scaled QK scores, adds the mask, softmaxes, and multiplies by V. Hugging Face's attention backend docs also make clear that runtime backend dispatch is now a first-class path, so capture code must install at that seam or fail closed. PyTorch FlexAttention/PagedAttention and vLLM PagedAttention material also reinforce the same direction: correctness depends on exact mask/index/KV-layout semantics, and performance claims require named runtime evidence, not selector-only results. See `artifacts/research/REV0080_RUNTIME_RESEARCH_NOTES.md`.

## Audit/refactor performed

- Hardened `experiments/public_trace_capture/hf_attention_trace_capture.py` with an AttentionInterface registry wrapper and restore path.
- Extended `tools/real_model_trace_adapter_audit.py` with a fake registry fixture to prove wrapper selection/restoration without needing Transformers.
- Added `tools/public_trace_capture_readiness_audit.py` to scan dependencies and local Hugging Face cache snapshots.
- Added `artifacts/capture-kit/REV0080_RUN_CACHE_PREFLIGHT_AND_CAPTURE.sh` as the shortest execution path once a reviewed immutable model snapshot is present.

## What is still missing

- No `transformers` dependency is available in this capsule.
- No cached immutable public Llama-family snapshot is available in this capsule.
- No public/pretrained post-transform Q/K/V bundle was captured or accepted.
- No GPU/fused or named-hardware sparse-vs-dense measurement exists.

## Next move

Install/provide `transformers` plus a reviewed immutable public Llama-family snapshot, then run `artifacts/capture-kit/REV0080_RUN_CACHE_PREFLIGHT_AND_CAPTURE.sh`. If the gate accepts the public trace, move immediately to named-hardware measurement. If capture remains unavailable, stop/pivot rather than adding more doctrine.
