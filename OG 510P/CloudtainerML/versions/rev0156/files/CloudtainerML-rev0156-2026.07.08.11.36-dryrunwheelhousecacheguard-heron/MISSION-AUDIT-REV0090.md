# Mission audit — CloudtainerML rev0090 — generation determinism gate

**Package:** `CloudtainerML-rev0090-2026.07.06.09.06-generationdeterminismgate-redstart`  
**Generated:** 2026-07-06T09:06:00-04:00  
**Status:** non-promotional. No accepted public/pretrained checkpoint trace and no named-hardware sparse-vs-dense timing are claimed.

## Heart of this turn

rev0090 removes a replayability false-positive that survived rev0089. Generated-token digests prove which token IDs were emitted, but not which generation path emitted them. In current Hugging Face generation semantics, `do_sample=False` is not by itself a greedy guarantee: `do_sample=False, num_beams=1` is greedy decoding, while `do_sample=False, num_beams>1` is beam search. A public cached-decode trace can therefore bind prompt tokens, generated tokens, masks, active-key length, GQA ownership, RoPE positions, probability semantics, and dense parity, yet still be unreplayable if an inherited model `generation_config` silently changes the decode strategy.

## Priority change

The public trace contract advanced to `public_trace_claim_v12` and now requires `greedy_cached_decode_generation_config_v1`. The capture helper forces `num_beams=1`, `num_return_sequences=1`, `do_sample=False`, `use_cache=True`, and `max_new_tokens=decode_steps` for cached decode. It exports canonical `generation_config_json`, its SHA-256 digest, generation strategy, beam count, return-sequence count, max-new-token count, and sampling-disabled status into both the NPZ and provenance manifest.

## Audit/refactor performed

- Refactored `experiments/public_trace_capture/hf_attention_trace_capture.py` so the real HF Llama capture path records hash-checked greedy single-beam generation settings instead of a loose config digest.
- Refactored `experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py` to independently parse and verify `generation_config_json`, reject `num_beams>1`, reject non-single return sequences, and require `max_new_tokens == decode_steps_requested`.
- Updated token/generation fixture audits so their dense-parity controls now carry v12 deterministic-generation metadata.
- Added `tools/public_trace_generation_determinism_audit.py`, a negative-control audit that accepts a good greedy bundle and rejects a dense-parity-preserving forged beam-count bundle.
- Updated capture readiness, smoke validation, handoff script, and research notes so deterministic generation is part of the executable acceptance path rather than prose.

## What remains riskiest

The riskiest missing artifact remains the actual immutable public Llama-family checkpoint capture. rev0090 makes that run harder to fake but does not replace it. The next acceptable move is to execute the capture script in an environment with `transformers`, a reviewed immutable cached model/tokenizer snapshot, and then pass the public gate. If that succeeds, the next move is named-hardware sparse-vs-dense timing, including tokenization, generated-token replay, generation config, cache ownership, index/mask construction, active-key length, RoPE position handling, probability path, and quality.

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
