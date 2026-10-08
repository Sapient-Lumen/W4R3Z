# Trace environment requirements — REV0096

Status: `requirements_recorded_not_installed_here`  
Promotion allowed: `false`

This is not a registry addition; it is the minimal runtime contract needed to stop failing late:

```bash
python tools/transformers_llama_surface_probe.py --strict
ALLOW_DOWNLOAD=1 python tools/hf_snapshot_materializer.py --download --strict
ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```

The key change is the compatibility probe. Current Transformers releases can move internal surfaces; the public trace hook must prove the Llama eager attention function and mask/cached-decode signatures are present before capture.
