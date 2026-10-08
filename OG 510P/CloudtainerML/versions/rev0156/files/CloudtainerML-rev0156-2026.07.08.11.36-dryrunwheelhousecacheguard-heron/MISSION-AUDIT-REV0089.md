# Mission audit — CloudtainerML rev0089 — generated-token replay provenance gate

**Package:** `CloudtainerML-rev0089-2026.07.06.08.12-generationtokenreplay-marshwren`  
**Generated:** 2026-07-06T08:12:00-04:00  
**Status:** non-promotional. No accepted public/pretrained checkpoint trace and no named-hardware sparse-vs-dense timing are claimed.

## Heart of this turn

rev0089 removes the next replayability false-positive from the real-trace lane. rev0088 bound rows to the tokenizer prompt, but cached decode is not produced by the prompt alone: every decode row is driven by the prior generated tokens and KV state. A trace can have valid post-transform Q/K/V, mask, active-key length, GQA/KV ownership, RoPE position IDs, probability semantics, dense parity, and prompt-token provenance, yet still be unreplayable if the generated continuation that feeds cached decode is not bound to the rows.

## Priority change

The public trace contract advanced to `public_trace_claim_v11` and now requires `generated_sequence_digest_v1` in addition to `prompt_input_ids_attention_mask_digest_v1`. The capture path records per-prompt full generated sequence digest, generated new-token suffix digest, generated suffix count, generated sequence token count, and prompt-prefix verification. The public gate independently checks that cached-decode rows lie inside the prompt-plus-generated-token range and that at least one decode row is covered by the generated suffix.

## Audit/refactor performed

- Refactored `experiments/public_trace_capture/hf_attention_trace_capture.py` so real HF generation returns are harvested for sequence-level and generated-suffix digests.
- Refactored `experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py` to verify generated-token replay provenance instead of trusting self-attestation.
- Updated `tools/public_trace_token_provenance_audit.py` so its good fixture carries both prompt and generated-token contracts.
- Added `tools/public_trace_generation_token_audit.py`, a negative-control audit that accepts a good prompt+generated bundle and rejects a dense-parity-preserving forged generated-token boundary bundle.
- Updated capture readiness and smoke validation so v11 generated-token replay provenance is part of the executable handoff rather than a documentation note.

## What remains riskiest

The riskiest missing artifact is still the real immutable public Llama-family checkpoint capture. rev0089 makes that run harder to fake but does not replace it. Promotion remains blocked until a real public checkpoint trace passes v11 and a named-hardware end-to-end sparse-vs-dense measurement includes tokenization, prompt and generated-token replay, cache ownership, active-key length, mask/index construction, RoPE position handling, probability semantics, and quality.

## Validation target

Run:

```bash
python tools/public_trace_token_provenance_audit.py
python tools/public_trace_generation_token_audit.py
python tools/public_trace_capture_readiness_audit.py
python tools/smoke_validate.py
sha256sum -c CHECKSUMS.sha256
```
