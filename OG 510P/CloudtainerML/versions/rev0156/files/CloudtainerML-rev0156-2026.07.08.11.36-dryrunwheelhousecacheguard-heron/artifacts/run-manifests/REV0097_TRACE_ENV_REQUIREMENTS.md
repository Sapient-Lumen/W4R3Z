# Trace environment requirements — REV0097

Status: `requirements_recorded_not_installed_here`  
Promotion allowed: `false`

Current gate:

```bash
python tools/public_trace_readiness_gate.py --local-only
ALLOW_DOWNLOAD=1 python tools/public_trace_readiness_gate.py --download --strict
```

Then, only after the gate passes:

```bash
ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```

Research basis: Hugging Face Hub `snapshot_download()` is revision-addressed and cached; Transformers exposes `attn_implementation`; current Transformers/PyTorch may use SDPA by default; and exact generation requires pinned greedy controls plus exact new-token count.
