# Mission audit — REV0100

Status: `pass_with_blockers`  
Promotion allowed: `false`

## What changed

rev0100 advances the riskiest unfinished lane: the real public TinyLlama trace. The previous packet still assumed that the model string passed to `from_pretrained` and the public model id written into provenance were the same thing. That is fragile in real operator environments: a reviewed snapshot may be mounted locally, pre-seeded by a build step, or provided through a controlled cache path.

This revision separates:

- `MODEL_ID`: canonical public identity written into trace provenance.
- `MODEL_REVISION`: immutable public commit/hash.
- `LOCAL_SNAPSHOT_DIR`: optional loader-only path for a reviewed flat snapshot.

## Why it matters

A local path like `/mnt/models/TinyLlama` is a valid loader source but a poor public evidence identity. If that path leaks into provenance as the model id, the trace becomes harder to audit, compare, or reproduce. rev0100 adds `--public-model-id` to the capture helper and statically audits the wrappers so a local loader path cannot silently replace canonical HF identity.

## What remains blocked here

- `transformers_not_importable_runtime_surface_unchecked`
- `hf_snapshot_network_dry_run_not_successful_here`
- `complete_tinyllama_snapshot_not_available`
- `cuda_not_available_for_named_hardware_timing`

## Refactor performed

The live capture surface is now:

```bash
ALLOW_NETWORK_DRY_RUN=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
LOCAL_SNAPSHOT_DIR=/path/to/TinyLlama-snapshot bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```

Historical revision wrappers remain as provenance only. Top-level docs point to the stable alias.

## Decision

Do not add another registry before running one of the two concrete capture paths above in a capable environment. If local snapshot intake fails, repair the snapshot directory. If it passes, capture immediately and let the public trace gate decide.
