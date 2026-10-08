# CloudtainerML rev0081 — mask-fidelity capture refactor

**Package:** `CloudtainerML-rev0081-2026.07.06.03.06-maskfidelitycapture-ivoryheron`  
**Archive:** `CloudtainerML-rev0081-2026.07.06.03.06-maskfidelitycapture-ivoryheron.zip`  
**Generated:** 2026-07-06T03:06:00-04:00  
**Status:** non-promotional capture-seam correction; no accepted public/pretrained trace and no GPU/fused timing.  
**Primary new artifact:** `MISSION-AUDIT-REV0081.md`  
**Substantive code change:** preserve the built-in Hugging Face eager attention mask backend and require an exercised causal-mask challenge row before any public trace self-attestation.  
**Next acceptable deliverable:** run the rev0081 capture path on an immutable public Llama-family checkpoint, pass the gate, then measure named hardware.

---

## Heart of the mission

CloudtainerML is still a claim compiler and falsification wind tunnel. Its useful output is not a fuller registry. Its useful output is a trustworthy yes/no/stop decision about whether a sparse-attention or trace-reuse claim survives exact score semantics, hostile controls, provenance, and cost.

## Risk found after rev0080

rev0080 made the attention capture seam registry-aware, but the safest-looking implementation was still too risky. Current Hugging Face documentation says a custom `attn_implementation` name must have a matching attention-mask registration; otherwise Transformers can skip mask creation and pass `attention_mask=None` to attention layers. That would let a trace path pass dense parity against the wrong unmasked semantics.

That is the kind of severe wrongness this cube is supposed to catch: a green gate that verifies a trace while losing causal or padding constraints.

## Priority change made in rev0081

rev0081 removes the custom backend path. The Llama capture helper now temporarily overrides the built-in `eager` attention entry and sets the model to `eager`, while preserving the built-in eager mask backend. It still patches the module-level eager fallback for older releases and restores both registry/config state afterward.

Public self-attestation now requires all of the following:

- post-model-transform Q/K/V capture;
- explicit attention scale and additive score bias;
- finite serialization of negative-infinity mask entries using a sentinel;
- `mask_challenge_exercised=true` from at least one row where the mask matters;
- `attention_mask_backend_preserved=true`;
- `custom_attention_backend_used=false`;
- recomputed dense-reference parity within tolerance;
- immutable model/tokenizer/code provenance and reviewed source/license fields.

## Audit/refactor performed

- Refactored `experiments/public_trace_capture/hf_attention_trace_capture.py` from custom backend registration to built-in `eager` override/restore.
- Updated `experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py` to require the mask challenge and mask-backend preservation fields in manifest and NPZ metadata.
- Added/updated `tools/real_model_trace_adapter_audit.py` so its fixture exercises causal `-inf` masks and confirms registry/config restoration.
- Added `tools/public_trace_mask_fidelity_audit.py`, which builds a deterministic masked Q/K/V case, verifies finite sentinel conversion, recomputes dense attention, and proves the gate rejects missing mask challenge metadata.
- Updated `tools/public_trace_capture_readiness_audit.py` and the run script to make mask fidelity a preflight step.

## What remains missing

- No actual immutable public/pretrained checkpoint was loaded in this capsule.
- `transformers` is still unavailable in this validation environment.
- No cached immutable public Llama-family snapshot is present.
- No public/pretrained post-transform trace bundle has been accepted by the gate.
- No GPU/fused kernel or named-hardware sparse-vs-dense measurement exists.

## Online research pressure

- Hugging Face AttentionInterface docs warn that custom attention names need matching `AttentionMaskInterface` registration or mask creation can be skipped.
- Current Hugging Face Llama source applies rotary embeddings before the attention interface and eager attention adds `attention_mask` into scaled QK scores before softmax.
- Hugging Face issue #40362 reports changed Llama computation when registering a custom AttentionInterface backend, matching the risk this revision now avoids.

See `artifacts/research/REV0081_RUNTIME_RESEARCH_NOTES.md` for research notes and source URLs.

## Next move

Do not add another doctrine-only layer. Provide or install `transformers` plus a reviewed immutable public Llama-family snapshot, then run `artifacts/capture-kit/REV0081_RUN_CACHE_PREFLIGHT_AND_CAPTURE.sh`. If the gate accepts the public trace, move immediately to named-hardware timing. If this remains unavailable, stop or pivot.
