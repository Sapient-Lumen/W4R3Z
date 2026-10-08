# Mission audit — CloudtainerML rev0095 — environment preflight / source lock / active surface trim

**Package:** `CloudtainerML-rev0095-2026.07.06.11.32-envpreflightsourcelock-seal`  
**Generated:** 2026-07-06T11:32:00Z  
**Status:** non-promotional. This revision does not include an accepted public/pretrained trace and does not include named-hardware sparse-vs-dense timing.

## What changed

rev0095 focuses on the highest-risk unfinished work: getting from a concrete model packet to a real public trace. rev0094 picked a TinyLlama target, but it still allowed a future turn to fail late and vaguely. This revision adds an execution preflight that fails early and records exact blockers.

Added or materially changed:

- `tools/public_trace_env_preflight.py`
- `tools/source_lock_audit.py`
- `tools/active_surface_trim_audit.py`
- `artifacts/capture-kit/REV0095_RUN_TINYLLAMA_PUBLIC_TRACE.sh`
- `artifacts/capture-kit/REV0095_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh`
- `artifacts/run-manifests/REV0095_TINYLLAMA_SOURCE_LOCK.json`
- `artifacts/run-manifests/REV0095_PUBLIC_TRACE_ENV_LOCK.json`
- `artifacts/run-manifests/REV0095_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json`
- `artifacts/audit/REV0095_SOURCE_LOCK_AUDIT.json/.md`
- `artifacts/audit/REV0095_PUBLIC_TRACE_ENV_PREFLIGHT.json/.md`
- `artifacts/audit/REV0095_ACTIVE_SURFACE_TRIM_AUDIT.json/.md`
- `artifacts/audit/REV0095_CACHE_TRIM_AUDIT.json/.md`
- `artifacts/research/REV0095_ONLINE_RESEARCH_NOTES.md`
- `artifacts/run-logs/REV0095_LOCAL_PREFLIGHT_ATTEMPT.log`

## Why this is the right risk-first move

The riskiest incomplete deliverable is not another rule. It is the first immutable public/pretrained prefill+cached-decode trace that passes the gate. The model target is now specific and source-locked, so the live failure surface is environment readiness: `transformers`, HF cache/download policy, disk, and hardware timing context.

The new preflight turns that risk into a repair list. In this capsule it reports:

- `transformers_not_importable`
- `no_complete_local_hf_snapshot_and_download_not_allowed`
- CUDA unavailable for later named-hardware timing

This is forward motion because the next runner no longer needs to infer why the packet cannot execute.

## Online research incorporated

The revision records source facts from Hugging Face and systems/attention documentation in `artifacts/research/REV0095_ONLINE_RESEARCH_NOTES.md` and `artifacts/run-manifests/REV0095_TINYLLAMA_SOURCE_LOCK.json`. The important result is not a new claim; it is a tighter execution contract:

- TinyLlama source/license/commit are pinned and recorded.
- Exact generation controls remain necessary because `max_new_tokens`, `min_new_tokens`, `do_sample`, `num_beams`, and `use_cache` shape the token path.
- The attention-interface mask warning remains central: custom attention hooks can silently drop masks unless the matching mask interface is registered or the built-in eager backend is preserved.
- Timing promotion must compare against modern SDPA/Flash/Flex/Paged-style baselines with cache/layout costs included.

## Audit/refactor result

This revision performs a small but real cleanup:

- removes generated `__pycache__`/`.pyc` runtime churn;
- rewrites top-level docs to point to the rev0095 wrapper, not old rev0093/rev0094 paths;
- records old capture scripts as historical provenance, not current instructions;
- adds an active-surface audit so stale entrypoints are now machine-detectable.

## Remaining blockers

- `actual_public_pretrained_prefill_plus_cached_decode_exact_length_greedy_generation_trace_missing`
- `transformers_dependency_absent_in_validation_environment`
- `no_cached_hf_model_snapshot_with_config_weights_tokenizer_detected`
- `cuda_gpu_not_available_for_named_hardware_timing_in_this_capsule`
- `named_hardware_sparse_vs_dense_timing_missing`

## Stop/go rule

The next material move is to satisfy `tools/public_trace_env_preflight.py` and run the TinyLlama packet. If that cannot be done, write a stop/pivot memo. Do not spend another turn adding registry-only doctrine.
