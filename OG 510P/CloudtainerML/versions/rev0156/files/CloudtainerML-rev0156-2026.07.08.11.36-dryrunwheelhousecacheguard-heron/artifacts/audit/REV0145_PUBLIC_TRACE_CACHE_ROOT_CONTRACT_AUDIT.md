# Public trace cache-root contract audit — REV0145

Status: `fail`  
Promotion allowed: `false`

Verifies that the active first-trace, snapshot, bootstrap, and capture surfaces default Hugging Face/Transformers/Xet caches to a project-local root instead of silently relying on user-global ~/.cache state. Operators can still override PUBLIC_TRACE_CACHE_ROOT or individual HF_* variables, but the default path is trace-bound and easier to delete or move.

Default cache root: `artifacts/runtime/public-trace-hf-cache`

## Errors

- `artifacts/capture-kit/REV0145_BOOTSTRAP_PUBLIC_TRACE_ENV.sh missing cache-root marker: PUBLIC_TRACE_CACHE_ROOT`
- `artifacts/capture-kit/REV0145_BOOTSTRAP_PUBLIC_TRACE_ENV.sh missing cache-root marker: artifacts/runtime/public-trace-hf-cache`
- `artifacts/capture-kit/REV0145_BOOTSTRAP_PUBLIC_TRACE_ENV.sh missing cache-root marker: HF_HOME`
- `artifacts/capture-kit/REV0145_BOOTSTRAP_PUBLIC_TRACE_ENV.sh missing cache-root marker: HF_HUB_CACHE`
- `artifacts/capture-kit/REV0145_BOOTSTRAP_PUBLIC_TRACE_ENV.sh missing cache-root marker: HF_XET_CACHE`
- `artifacts/capture-kit/REV0145_BOOTSTRAP_PUBLIC_TRACE_ENV.sh missing cache-root marker: HF_ASSETS_CACHE`
- `artifacts/capture-kit/REV0145_BOOTSTRAP_PUBLIC_TRACE_ENV.sh missing cache-root marker: mkdir -p "$HF_HOME" "$HF_HUB_CACHE" "$HF_XET_CACHE" "$HF_ASSETS_CACHE"`
- `artifacts/capture-kit/REV0145_FIRST_REAL_TRACE_ONE_COMMAND.sh missing cache-root marker: PUBLIC_TRACE_CACHE_ROOT`
- `artifacts/capture-kit/REV0145_FIRST_REAL_TRACE_ONE_COMMAND.sh missing cache-root marker: artifacts/runtime/public-trace-hf-cache`
- `artifacts/capture-kit/REV0145_FIRST_REAL_TRACE_ONE_COMMAND.sh missing cache-root marker: HF_HOME`
- `artifacts/capture-kit/REV0145_FIRST_REAL_TRACE_ONE_COMMAND.sh missing cache-root marker: HF_HUB_CACHE`
- `artifacts/capture-kit/REV0145_FIRST_REAL_TRACE_ONE_COMMAND.sh missing cache-root marker: HF_XET_CACHE`
- `artifacts/capture-kit/REV0145_FIRST_REAL_TRACE_ONE_COMMAND.sh missing cache-root marker: HF_ASSETS_CACHE`
- `artifacts/capture-kit/REV0145_FIRST_REAL_TRACE_ONE_COMMAND.sh missing cache-root marker: mkdir -p "$HF_HOME" "$HF_HUB_CACHE" "$HF_XET_CACHE" "$HF_ASSETS_CACHE"`
- `artifacts/capture-kit/REV0145_PREPARE_TINYLLAMA_SNAPSHOT.sh missing cache-root marker: PUBLIC_TRACE_CACHE_ROOT`
- `artifacts/capture-kit/REV0145_PREPARE_TINYLLAMA_SNAPSHOT.sh missing cache-root marker: artifacts/runtime/public-trace-hf-cache`
- `artifacts/capture-kit/REV0145_PREPARE_TINYLLAMA_SNAPSHOT.sh missing cache-root marker: HF_HOME`
- `artifacts/capture-kit/REV0145_PREPARE_TINYLLAMA_SNAPSHOT.sh missing cache-root marker: HF_HUB_CACHE`
- `artifacts/capture-kit/REV0145_PREPARE_TINYLLAMA_SNAPSHOT.sh missing cache-root marker: HF_XET_CACHE`
- `artifacts/capture-kit/REV0145_PREPARE_TINYLLAMA_SNAPSHOT.sh missing cache-root marker: HF_ASSETS_CACHE`
- `artifacts/capture-kit/REV0145_PREPARE_TINYLLAMA_SNAPSHOT.sh missing cache-root marker: mkdir -p "$HF_HOME" "$HF_HUB_CACHE" "$HF_XET_CACHE" "$HF_ASSETS_CACHE"`
- `artifacts/capture-kit/REV0145_RUN_TINYLLAMA_PUBLIC_TRACE.sh missing cache-root marker: PUBLIC_TRACE_CACHE_ROOT`
- `artifacts/capture-kit/REV0145_RUN_TINYLLAMA_PUBLIC_TRACE.sh missing cache-root marker: artifacts/runtime/public-trace-hf-cache`
- `artifacts/capture-kit/REV0145_RUN_TINYLLAMA_PUBLIC_TRACE.sh missing cache-root marker: HF_HOME`
- `artifacts/capture-kit/REV0145_RUN_TINYLLAMA_PUBLIC_TRACE.sh missing cache-root marker: HF_HUB_CACHE`
- `artifacts/capture-kit/REV0145_RUN_TINYLLAMA_PUBLIC_TRACE.sh missing cache-root marker: HF_XET_CACHE`
- `artifacts/capture-kit/REV0145_RUN_TINYLLAMA_PUBLIC_TRACE.sh missing cache-root marker: HF_ASSETS_CACHE`
- `artifacts/capture-kit/REV0145_RUN_TINYLLAMA_PUBLIC_TRACE.sh missing cache-root marker: mkdir -p "$HF_HOME" "$HF_HUB_CACHE" "$HF_XET_CACHE" "$HF_ASSETS_CACHE"`
- `artifacts/capture-kit/REV0145_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh missing cache-root marker: PUBLIC_TRACE_CACHE_ROOT`
- `artifacts/capture-kit/REV0145_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh missing cache-root marker: artifacts/runtime/public-trace-hf-cache`
- `artifacts/capture-kit/REV0145_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh missing cache-root marker: HF_HOME`
- `artifacts/capture-kit/REV0145_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh missing cache-root marker: HF_HUB_CACHE`
- `artifacts/capture-kit/REV0145_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh missing cache-root marker: HF_XET_CACHE`
- `artifacts/capture-kit/REV0145_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh missing cache-root marker: HF_ASSETS_CACHE`
- `artifacts/capture-kit/REV0145_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh missing cache-root marker: mkdir -p "$HF_HOME" "$HF_HUB_CACHE" "$HF_XET_CACHE" "$HF_ASSETS_CACHE"`
- `artifacts/run-manifests/REV0145_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json missing project_local_hf_cache_root_v1 contract`
- `artifacts/run-manifests/REV0145_TINYLLAMA_SOURCE_LOCK.json missing project_local_hf_cache_root_v1 contract`

## Warnings

- `bootstrap_env_not_yet_generated_here`

## Interpretation

This is not a new registry layer. It removes a concrete completion risk: a successful first trace should not secretly depend on whichever Hugging Face cache happened to exist in a user home directory, and a failed/materialized run should be easy to clean without guessing where 2GB+ of model/Xet chunks went.
