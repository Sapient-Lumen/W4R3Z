# Trace environment requirements — REV0101

Status: `requirements_recorded_not_installed_here`  
Promotion allowed: `false`

Current command:

```bash
ALLOW_NETWORK_DRY_RUN=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```

Optional bootstrap:

```bash
bash artifacts/capture-kit/REV0101_BOOTSTRAP_PUBLIC_TRACE_ENV.sh
```

The trace extraction backend is intentionally pinned to `eager`. rev0101 adds a dependency/capability lock and a no-download Hugging Face snapshot dry-run before any full TinyLlama materialization.
