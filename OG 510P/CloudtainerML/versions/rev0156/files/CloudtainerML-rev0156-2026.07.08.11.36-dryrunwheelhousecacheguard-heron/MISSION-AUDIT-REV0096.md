# Mission audit — CloudtainerML rev0096 — runtime/snapshot probe

**Package:** `CloudtainerML-rev0096-2026.07.06.11.48-runtimesnapshotprobe-heron`  
**Generated:** 2026-07-06T11:48:00Z  
**Status:** non-promotional. No accepted public/pretrained trace and no named-hardware sparse-vs-dense timing are included.

## What changed

rev0096 focuses on the highest-risk unfinished lane: the real public TinyLlama trace can still fail before science begins if the installed Transformers internals do not expose the expected Llama eager-attention surface or if the exact Hugging Face snapshot is absent. This revision adds executable checks for both.

Added or materially changed:

- `tools/transformers_llama_surface_probe.py`
- `tools/hf_snapshot_materializer.py`
- `artifacts/capture-kit/REV0096_RUN_TINYLLAMA_PUBLIC_TRACE.sh`
- `artifacts/capture-kit/REV0096_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh`
- `artifacts/capture-kit/REV0096_PREPARE_TINYLLAMA_SNAPSHOT.sh`
- `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`
- `artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh`
- `artifacts/run-manifests/REV0096_TRACE_ENV_REQUIREMENTS.json/.md`
- `artifacts/run-manifests/REV0096_TINYLLAMA_SNAPSHOT_MATERIALIZATION.json`
- `artifacts/audit/REV0096_TRANSFORMERS_LLAMA_SURFACE_PROBE.json/.md`
- `artifacts/audit/REV0096_HF_SNAPSHOT_MATERIALIZER.json/.md`
- `artifacts/audit/REV0096_ACTIVE_SURFACE_TRIM_AUDIT.json/.md`
- `artifacts/research/REV0096_ONLINE_RESEARCH_NOTES.md`

## Why this is risk-first

The previous blocker list said “missing transformers” and “missing snapshot.” That was true but too coarse. A future runner could install a modern Transformers release and still fail because the Llama eager-attention hook signature moved, or could download an incomplete repo subset and fail during tokenizer/model load. rev0096 converts those into machine-readable probes before capture.

## Local result in this capsule

Expected blockers remain:

- `transformers_not_importable_runtime_surface_unchecked`
- `complete_tinyllama_snapshot_not_available`
- `no_complete_local_hf_snapshot_and_download_not_allowed`
- CUDA unavailable for named-hardware timing

This is still forward motion because the next executor now has a precise sequence: install/import runtime, pass the Llama surface probe, materialize the exact snapshot, then run capture.

## Audit/refactor result

The active capture surface is now stable:

```bash
ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```

The stable alias delegates to the current revision-specific wrapper. Historical revision-numbered scripts stay as provenance, but top-level docs no longer require browsing old wrappers.

## Next stop/go rule

Run:

```bash
python tools/transformers_llama_surface_probe.py --strict
ALLOW_DOWNLOAD=1 python tools/hf_snapshot_materializer.py --download --strict
ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```

If those cannot be satisfied in the next capable environment, write a stop/pivot memo instead of adding doctrine.
