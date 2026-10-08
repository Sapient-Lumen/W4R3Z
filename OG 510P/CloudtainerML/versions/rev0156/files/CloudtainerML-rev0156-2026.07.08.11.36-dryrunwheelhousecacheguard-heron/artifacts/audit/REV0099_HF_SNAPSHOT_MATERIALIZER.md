# REV0099 TinyLlama snapshot materialization

Status: `skipped_after_dry_run_failure`  
Promotion allowed: `false`

The full TinyLlama snapshot materializer is intentionally skipped in this capsule because the rev0099 Hugging Face dry-run/network preflight cannot reach `huggingface.co` here. This prevents a late or expensive full-snapshot attempt after readiness has already failed.

Locked model: `TinyLlama/TinyLlama-1.1B-Chat-v1.0`  
Locked model revision: `fe8a4ea1ffedaf415f4da2f062534de366a451e6`

Next action:

```bash
ALLOW_NETWORK_DRY_RUN=1 ALLOW_DOWNLOAD=1 python tools/public_trace_readiness_gate.py --download --strict
```
