# Mission audit — CloudtainerML rev0094 — TinyLlama trace packet / capture-surface refactor

**Package:** `CloudtainerML-rev0094-2026.07.06.11.23-tinyllamatracepacket-lynx`  
**Generated:** 2026-07-06T11:23:00Z  
**Status:** non-promotional. This revision does not include an accepted public/pretrained trace and does not include named-hardware sparse-vs-dense timing.

## What changed

rev0094 turns the riskiest unresolved path into a concrete run packet. rev0093 reduced the lane to one generic launch script, but the handoff could still stall on `MODEL_ID`, source review, and immutable revision choice. This revision removes that ambiguity by adding:

- `artifacts/capture-kit/REV0094_RUN_TINYLLAMA_PUBLIC_TRACE.sh`
- `artifacts/run-manifests/REV0094_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json`
- `tools/trace_run_packet_audit.py`
- `tools/capture_surface_refactor_audit.py`
- `artifacts/audit/REV0094_TRACE_RUN_PACKET_AUDIT.json/.md`
- `artifacts/audit/REV0094_CAPTURE_SURFACE_REFACTOR_AUDIT.json/.md`
- `artifacts/run-logs/REV0094_TINYLLAMA_LOCAL_ATTEMPT.log`

The current target is `TinyLlama/TinyLlama-1.1B-Chat-v1.0` pinned to full commit `fe8a4ea1ffedaf415f4da2f062534de366a451e6`, with `apache-2.0` as the reviewed license label from the online model tree.

## Why this is the right risk-first move

The cube's danger is no longer lack of doctrine. It is failure to complete the decisive public trace and hardware timing. A generic public-trace launcher was still too easy to postpone. A concrete target packet is harder to evade: either it runs, or it fails for a named environmental reason.

The local capsule still cannot complete the capture because `transformers` is absent, no reviewed HF snapshot is cached, and CUDA timing hardware is unavailable here. rev0094 therefore records a local attempted run and exact blockers rather than claiming progress that did not happen.

## Current command

```bash
ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/REV0094_RUN_TINYLLAMA_PUBLIC_TRACE.sh
```

Use `ALLOW_DOWNLOAD=1` only after source/license review. With the default `ALLOW_DOWNLOAD=0`, the script requires a suitable local cache and will fail closed.

## Audit/refactor result

The refactor did not delete historical artifacts. It changed the live surface:

- top-level docs now point to `REV0094_RUN_TINYLLAMA_PUBLIC_TRACE.sh` rather than a registry reading path;
- the run packet audit rejects mutable `main`-style revisions and short hashes;
- the capture-surface audit marks old capture scripts as retained provenance, not active instructions;
- the next turn has a concrete command and a specific checkpoint instead of another choice point.

## Remaining blockers

- `transformers_dependency_absent_in_validation_environment`
- `no_cached_hf_model_snapshot_with_config_weights_tokenizer_detected`
- `actual_public_pretrained_prefill_plus_cached_decode_exact_length_greedy_generation_trace_missing`
- `cuda_gpu_not_available_for_named_hardware_timing_in_this_capsule`
- `named_hardware_sparse_vs_dense_timing_missing`

## Stop/go rule

The next material move is to run the TinyLlama packet in a capable environment. If that cannot be done, write a stop/pivot memo; do not spend another turn adding registry-only doctrine.
