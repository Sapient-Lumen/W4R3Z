# Public trace cache-root contract audit — REV0155

Status: `pass`  
Promotion allowed: `false`

Verifies that the active first-trace, snapshot, bootstrap, and capture surfaces default Hugging Face/Transformers/Xet caches to a project-local root instead of silently relying on user-global ~/.cache state. Operators can still override PUBLIC_TRACE_CACHE_ROOT or individual HF_* variables, but the default path is trace-bound and easier to delete or move.

Default cache root: `artifacts/runtime/public-trace-hf-cache`

## Errors

- none

## Warnings

- `bootstrap_env_not_yet_generated_here`

## Interpretation

This is not a new registry layer. It removes a concrete completion risk: a successful first trace should not secretly depend on whichever Hugging Face cache happened to exist in a user home directory, and a failed/materialized run should be easy to clean without guessing where 2GB+ of model/Xet chunks went.
