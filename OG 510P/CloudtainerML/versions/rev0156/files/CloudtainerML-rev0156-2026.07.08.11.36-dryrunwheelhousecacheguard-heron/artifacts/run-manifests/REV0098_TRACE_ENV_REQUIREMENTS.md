# Trace environment requirements — REV0098

Status: `requirements_recorded_not_installed_here`  
Promotion allowed: `false`

Current command:

```bash
ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```

The trace extraction backend is intentionally pinned to `eager`. Modern SDPA/Flash/Flex backends remain important for later timing/baseline work, but they are not accepted trace-capture surfaces for this adapter.
