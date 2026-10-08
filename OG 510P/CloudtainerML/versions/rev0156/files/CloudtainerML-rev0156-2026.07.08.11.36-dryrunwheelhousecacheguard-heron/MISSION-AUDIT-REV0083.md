# CloudtainerML rev0083 — absolute-position cached-decode trace gate

**Package:** `CloudtainerML-rev0083-2026.07.06.04.05-absolutepositiontrace-cedarwaxwing`  
**Archive:** `CloudtainerML-rev0083-2026.07.06.04.05-absolutepositiontrace-cedarwaxwing.zip`  
**Generated:** 2026-07-06T04:05:00-04:00  
**Status:** non-promotional trace-identity hardening; no accepted public/pretrained trace and no GPU/fused timing.  
**Primary new artifact:** `MISSION-AUDIT-REV0083.md`  
**Substantive code change:** cached-decode trace rows now export and gate-check absolute key positions, preventing the old q_len=1 local-position false green.  
**Next acceptable deliverable:** run the rev0083 capture path with `--decode-steps 2` on an immutable public Llama-family checkpoint, pass the gate with absolute decode positions, then move directly to named-hardware sparse-vs-dense timing.

---

## Heart of the mission

CloudtainerML is still a claim compiler and falsification wind tunnel. The useful output is not a thicker registry; it is a trustworthy stop/go/pivot decision about whether an ML architecture claim survives exact semantics, hostile controls, provenance, row identity, and cost. The cube should spend its remaining energy on executable gates that can reject false positives before any public or performance claim is made.

## Risk found after rev0082

rev0082 correctly blocked prefill-only public trace promotion, but it still left a row-identity blind spot: cached-decode rows have `query_len=1`, so a naive exporter can label every decode row as local position `0` while the row is actually the newest token at the end of a longer live KV cache. Dense Q/K/V parity does not catch that bug because the `position` label is metadata, not part of the dot product.

That label matters because downstream sparse-attention analysis uses row identity to reason about context position, cache growth, cost, and phase behavior. A q_len-local decode position can make a real cached-generation trace look like a prompt-start row. That is the kind of subtle evidence corruption the cube exists to prevent.

## Priority change made in rev0083

rev0083 adds an absolute-position contract:

- `trace_claim_version="public_trace_claim_v5"`;
- `position_contract="absolute_key_position_v1"`;
- `absolute_position_verified=true` required in the manifest and NPZ self-attestation;
- capture rows compute `position = query_start_position + local_query_index`;
- when the runtime does not expose `cache_position`, cached-decode rows infer `query_start_position = key_len - query_len`;
- gate-side `verify_qkv_score_contract()` recomputes position semantics from `position`, `query_len`, `valid_key_len`, and `capture_phase`;
- public/pretrained bundles are rejected if a `decode_cached` row with `query_len=1` is not labeled at `valid_key_len - 1`.

## Audit/refactor performed

- Refactored `experiments/public_trace_capture/hf_attention_trace_capture.py` to export absolute key positions for cached decode.
- Refactored `experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py` to require and recompute the absolute-position contract.
- Added `tools/public_trace_absolute_position_audit.py`, a negative-control audit where dense math still passes but decode rows are relabeled to local position `0`; the gate must reject it.
- Updated mask, decode, adapter, readiness, smoke, and run-handoff surfaces around the new position contract.
- Kept the revision non-promotional: the accepted temporary bundles in audits are fixtures only.

## What remains missing

- No actual immutable public/pretrained checkpoint was loaded in this capsule.
- `transformers` is still unavailable in this validation environment.
- No cached immutable public Llama-family snapshot is present.
- No public/pretrained prefill+cached-decode absolute-position trace bundle has been accepted by the gate.
- No GPU/fused kernel or named-hardware sparse-vs-dense measurement exists.

## Online research pressure

- Hugging Face cache documentation says cached attention combines present and past KV, with attention matrices shaped over current query length by past-plus-current key length; it also says the attention mask must match that combined length.
- Hugging Face KV-cache documentation says `DynamicCache` grows during generation by default, while static/sliding cache variants change live-length behavior.
- TensorRT-LLM and vLLM serving documentation treat prefill/context and decode/generation as distinct operational phases, with KV transfer/cache identity becoming first-class in production serving.

See `artifacts/research/REV0083_RUNTIME_RESEARCH_NOTES.md` for source URLs and how they affected this revision.

## Next move

Do not add a doctrine-only layer. Provide or install `transformers` plus a reviewed immutable public Llama-family snapshot, then run `artifacts/capture-kit/REV0083_RUN_CACHE_PREFLIGHT_AND_CAPTURE.sh`. If the gate accepts the public prefill+cached-decode absolute-position trace, move immediately to named-hardware timing. If this remains unavailable, stop or pivot.
