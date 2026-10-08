# Mission audit — CloudtainerML rev0088 — prompt/token provenance gate

**Package:** `CloudtainerML-rev0088-2026.07.06.07.24-tokenprovenancegate-kingfisher`  
**Generated:** 2026-07-06T07:24:00-04:00  
**Status:** non-promotional. No accepted public/pretrained checkpoint trace and no named-hardware sparse-vs-dense timing are claimed.

## Heart of this turn

rev0088 removes a replayability false-positive from the real-trace lane. A trace can now have correct post-transform Q/K/V, cache, mask, active-key, GQA/KV, RoPE-position, probability, and dense-reference math, yet still be unusable if the rows are not bound to the exact tokenizer prompt that produced them. The cube now treats that as a blocker rather than a footnote.

## Priority change

The public trace contract advanced to `public_trace_claim_v10` and now requires `prompt_input_ids_attention_mask_digest_v1`. The capture path exports per-prompt prompt-text, `input_ids`, `attention_mask`, token-count, attention-mask-sum, and generation-config digests. The gate recomputes whether prefill rows fall inside the prompt boundary and cached-decode rows start after the prompt boundary. A self-attested bundle that keeps dense math intact but forges the prompt token count is rejected.

## Audit/refactor performed

- Refactored `experiments/public_trace_capture/hf_attention_trace_capture.py` to export exact token provenance fields and fold them into public self-attestation.
- Refactored `experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py` to independently verify token-provenance row semantics.
- Added `tools/public_trace_token_provenance_audit.py`, a negative-control audit that accepts a good synthetic prefill+decode bundle and rejects a dense-parity-preserving forged prompt-boundary bundle.
- Refactored the capture-readiness handoff so the next executable path starts with the v10 token-provenance audit instead of historical fixture churn.

## What remains riskiest

The riskiest missing artifact is still the real immutable public Llama-family checkpoint capture. rev0088 makes that run harder to fake but does not replace it. Promotion remains blocked until a real public checkpoint trace passes v10 and a named-hardware end-to-end sparse-vs-dense measurement includes tokenization/prompt boundaries, cache ownership, active-key length, mask/index construction, RoPE position handling, probability semantics, and quality.

## Validation target

Run:

```bash
python tools/public_trace_token_provenance_audit.py
python tools/public_trace_capture_readiness_audit.py
python tools/smoke_validate.py
sha256sum -c CHECKSUMS.sha256
```
