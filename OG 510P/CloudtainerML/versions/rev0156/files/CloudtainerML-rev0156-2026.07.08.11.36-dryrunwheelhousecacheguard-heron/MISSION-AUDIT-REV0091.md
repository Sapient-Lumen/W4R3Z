# Mission audit — CloudtainerML rev0091 — exact decode-count gate

**Package:** `CloudtainerML-rev0091-2026.07.06.10.18-exactdecodecountgate-amberthrush`  
**Generated:** 2026-07-06T10:18:00-04:00  
**Status:** non-promotional. No accepted public/pretrained checkpoint trace and no named-hardware sparse-vs-dense timing are claimed.

## Heart of this turn

rev0091 removes the next replayability false-positive after rev0090. Generated-token digests and greedy generation settings are necessary, but they are still not sufficient if the continuation can terminate early. Current generation semantics treat `max_new_tokens` as a maximum, not a guarantee that the requested number of decode steps were actually produced. That matters because cached-decode evidence is row-based: if a two-step decode request emits only one new token, then the trace has not covered the requested cached-decode horizon even if the surviving row has dense parity.

## Priority change

The public trace contract advanced to `public_trace_claim_v13`. The generation-token contract is now `generated_sequence_digest_exact_length_v2`, and the deterministic generation contract is now `greedy_exact_length_cached_decode_generation_config_v2`. The capture helper forces `min_new_tokens=max_new_tokens=decode_steps_requested` and exports exact-length flags. The gate requires every prompt's generated-new-token count to equal `decode_steps_requested` exactly; a count lower than requested is rejected as incomplete cached-decode coverage.

## Audit/refactor performed

- Refactored `experiments/public_trace_capture/hf_attention_trace_capture.py` so real HF Llama capture requests exact generated-token length and exports `generation_min_new_tokens`, `generation_exact_new_tokens_required`, and `generated_new_token_exact_count_verified`.
- Refactored `experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py` to parse and verify `min_new_tokens`, the exact-length flag, and generated-token count min/max against `decode_steps_requested`.
- Updated token-provenance, generation-token, generation-determinism, and capture-readiness audits around a two-token decode fixture.
- Added an early-stop negative control: a bundle with otherwise valid provenance but `generated_new_token_count=1` for `decode_steps_requested=2` is rejected.
- Updated readiness, smoke validation metadata, handoff docs, and research notes so exact decode count is part of the executable acceptance path rather than prose.

## What remains riskiest

The riskiest missing artifact remains the actual immutable public Llama-family checkpoint capture. rev0091 makes that run harder to fake but does not replace it. The next acceptable move is to execute the capture script in an environment with `transformers`, a reviewed immutable cached model/tokenizer snapshot, and then pass the public gate. If that succeeds, the next move is named-hardware sparse-vs-dense timing, including tokenization, generated-token replay, exact generated-token count, generation config, cache ownership, index/mask construction, active-key length, RoPE position handling, probability path, and quality.

## Validation target

Run:

```bash
python tools/public_trace_token_provenance_audit.py
python tools/public_trace_generation_token_audit.py
python tools/public_trace_generation_determinism_audit.py
python tools/public_trace_capture_readiness_audit.py
python tools/smoke_validate.py
sha256sum -c CHECKSUMS.sha256
```
