# Priority list — REV0156

Current revision: `rev0156`

1. Run `BOOTSTRAP_RUNTIME=1 PUBLIC_TRACE_BOOTSTRAP_DRY_RUN=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh` to verify the bootstrap path through the actual one-command wrapper without pip/network side effects.
2. Run `BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh` from this tree or the external runner.
3. Use `PUBLIC_TRACE_WHEELHOUSE=/path/to/wheels` if the capable host requires no-index package installation.
4. If it fails, fix `first_blocker_candidate` in `artifacts/audit/REV0156_PUBLIC_TRACE_FIRST_REAL_TRACE_STATUS.json` before adding doctrine.
5. Preserve the cache-duplication guard: `HF_HUB_DISABLE_SYMLINKS=1` must require explicit `PUBLIC_TRACE_ALLOW_CACHE_DUPLICATION=1`.
6. Preserve the prepare/capture split: network and snapshot materialization may occur only before capture; evidence capture must be local-only and digest-bound.
7. Promotion requires trace/provenance, evaluation receipt, selector-entry receipt, replay result, handoff archive, and named-hardware timing.

Capture alias: `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`.
