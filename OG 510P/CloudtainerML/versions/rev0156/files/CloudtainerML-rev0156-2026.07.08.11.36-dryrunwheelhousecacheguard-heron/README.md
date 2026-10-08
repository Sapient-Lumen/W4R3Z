# CloudtainerML — REV0156 dry-run, wheelhouse, and cache-duplication guard

Current revision: `rev0156`  
Package: `CloudtainerML-rev0156-2026.07.08.11.36-dryrunwheelhousecacheguard-heron.zip`  
Live command: `BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh`  
Bootstrap dry run: `BOOTSTRAP_RUNTIME=1 PUBLIC_TRACE_BOOTSTRAP_DRY_RUN=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh`  
Wheelhouse path: `PUBLIC_TRACE_WHEELHOUSE=/path/to/wheels BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh`  
Capture-only alias: `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`  
External runner: `artifacts/external-runner/REV0156_PUBLIC_TRACE_EXTERNAL_RUNNER.zip`

## Mission heart

CloudtainerML is a claim compiler. The live product is a small, digest-bound TinyLlama public-trace evidence packet, not more registry bureaucracy. The chain remains: reviewed snapshot → local-only capture → evaluation receipt → selector-entry receipt → replay gate → portable handoff archive → named-hardware timing.

## What changed in REV0156

- Fixed the one-command dry-run regression: `BOOTSTRAP_RUNTIME=1 PUBLIC_TRACE_BOOTSTRAP_DRY_RUN=1` now exits cleanly after bootstrap-path validation instead of demanding a venv that dry-run intentionally did not create.
- Added optional `PUBLIC_TRACE_WHEELHOUSE=/path/to/wheels` bootstrap support using `--no-index --find-links`, so an external runner can avoid system Python and public-index dependence.
- Added a Hugging Face cache duplication guard: `HF_HUB_DISABLE_SYMLINKS=1` is refused unless `PUBLIC_TRACE_ALLOW_CACHE_DUPLICATION=1` is explicit, because disabling Hub symlinks can duplicate huge model files.
- Added `tools/public_trace_cache_duplication_guard_audit.py` and wired it into first-trace, snapshot, capture, external-runner closure, and smoke validation.

## Current action

```bash
BOOTSTRAP_RUNTIME=1 PUBLIC_TRACE_BOOTSTRAP_DRY_RUN=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh
BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh
```

With an already reviewed local snapshot:

```bash
LOCAL_SNAPSHOT_DIR=/path/to/TinyLlama-snapshot bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh
```

This package remains non-promotional: this container still lacks the complete digest-verified TinyLlama snapshot and a passing Transformers capture runtime.
