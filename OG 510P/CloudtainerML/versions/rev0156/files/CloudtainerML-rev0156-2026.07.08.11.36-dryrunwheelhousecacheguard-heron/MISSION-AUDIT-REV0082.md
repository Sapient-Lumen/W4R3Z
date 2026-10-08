# CloudtainerML rev0082 — cached-decode phase gate

**Package:** `CloudtainerML-rev0082-2026.07.06.03.40-decodephasegate-bluejay`  
**Archive:** `CloudtainerML-rev0082-2026.07.06.03.40-decodephasegate-bluejay.zip`  
**Generated:** 2026-07-06T03:40:00-04:00  
**Status:** non-promotional cached-decode gate hardening; no accepted public/pretrained trace and no GPU/fused timing.  
**Primary new artifact:** `MISSION-AUDIT-REV0082.md`  
**Substantive code change:** public trace acceptance now requires prefill plus cached-decode phase coverage, positive decode steps, and `valid_key_len` padding semantics across mixed live KV lengths.  
**Next acceptable deliverable:** run the rev0082 capture path with `--decode-steps 2` on an immutable public Llama-family checkpoint, pass the gate, then move directly to named-hardware sparse-vs-dense timing.

---

## Heart of the mission

CloudtainerML is still a claim compiler and falsification wind tunnel. Its useful output is a trustworthy yes/no/stop decision about whether an ML architecture claim survives exact semantics, hostile controls, provenance, and cost. The mission is harmed whenever the cube replaces a missing experiment with more registry doctrine.

## Risk found after rev0081

rev0081 made mask fidelity executable, but it still left a serious false-green path: a trace could be perfectly valid for prompt prefill while saying almost nothing about the cached decode path where KV-cache sparse/dense value is actually spent. Sparse attention and KV-cache claims live in generation, where each new token usually attends over a growing cache. A prefill-only public bundle would therefore be too easy to over-read.

Current Hugging Face documentation says iterative cached forward passes need masks shaped over past plus current KV length, and `generate()` manages KV cache use internally. The Llama docs also describe `past_key_values` as cache instances where decode inputs contain only tokens not already represented in the cache. That means CloudtainerML's real trace lane must capture both the prefill phase and cached decode rows before the gate can accept a public/pretrained claim.

## Priority change made in rev0082

rev0082 extends the public trace schema and gate with a phase contract:

- `capture_phase_contract="prefill_and_cached_decode_v1"`;
- per-row `capture_phase` labels;
- per-row `valid_key_len` and `query_len`;
- `prefill_phase_present=true`;
- `decode_phase_present=true`;
- `cache_decode_verified=true` from at least one `q_len=1` row with live KV length greater than one;
- positive `decode_steps_requested`;
- `valid_key_len_semantics_verified=true`, including finite sentinel masking for padded KV tails.

The capture helper now supports `--decode-steps`; when positive it uses the generation path with `use_cache=True` so the wrapper can collect prefill and cached-decode rows. The gate rejects public/pretrained bundles that lack cached-decode coverage even if their prefill dense math is valid.

## Audit/refactor performed

- Refactored `experiments/public_trace_capture/hf_attention_trace_capture.py` to emit phase metadata, `valid_key_len`, `query_len`, and decode-step provenance.
- Refactored `experiments/public_trace_gate_surrogate/public_trace_gate_surrogate.py` to require the cached-decode phase contract for public/pretrained trace acceptance.
- Added `tools/public_trace_decode_phase_audit.py`, which accepts a temporary mixed prefill+cached-decode bundle and rejects a prefill-only negative control.
- Updated `tools/public_trace_mask_fidelity_audit.py` so its fixture also exercises mixed prefill/decode padding semantics.
- Updated `tools/real_model_trace_adapter_audit.py` and `tools/public_trace_capture_readiness_audit.py` so the execution path points at `--decode-steps 2` rather than a prefill-only run.
- Updated the run script to require positive decode steps before creating a public trace candidate.

## What remains missing

- No actual immutable public/pretrained checkpoint was loaded in this capsule.
- `transformers` is still unavailable in this validation environment.
- No cached immutable public Llama-family snapshot is present.
- No public/pretrained prefill+cached-decode trace bundle has been accepted by the gate.
- No GPU/fused kernel or named-hardware sparse-vs-dense measurement exists.

## Online research pressure

- Hugging Face cache documentation says cached forward passes need an attention mask covering past plus current KV length, with `generate()` usually handling that internally.
- Hugging Face KV-cache documentation describes generation cache strategies such as `DynamicCache`, reinforcing that decode/cache behavior is not a side issue.
- Hugging Face Llama documentation describes `past_key_values` as a cache and says decode inputs should include only unprocessed tokens when a cache is supplied.

See `artifacts/research/REV0082_RUNTIME_RESEARCH_NOTES.md` for research notes and source URLs.

## Next move

Do not add another doctrine-only layer. Provide or install `transformers` plus a reviewed immutable public Llama-family snapshot, then run `artifacts/capture-kit/REV0082_RUN_CACHE_PREFLIGHT_AND_CAPTURE.sh`. If the gate accepts the public prefill+cached-decode trace, move immediately to named-hardware timing. If this remains unavailable, stop or pivot.
