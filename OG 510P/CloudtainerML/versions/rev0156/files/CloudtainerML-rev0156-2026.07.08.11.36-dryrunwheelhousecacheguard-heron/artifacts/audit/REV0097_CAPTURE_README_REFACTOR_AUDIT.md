# Capture README refactor audit — REV0097

Status: `pass`  
Promotion allowed: `false`

Refactored `experiments/public_trace_capture/README.md`, which was still framed as a rev0049 helper. The current entrypoint is now the readiness gate:

```bash
python tools/public_trace_readiness_gate.py --local-only
```

Then, only after readiness passes:

```bash
ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```
