# Mission audit — REV0098

Status: `pass_with_blockers`  
Promotion allowed: `false`

## What changed

This revision moved the riskiest unfinished lane from “ready-ish” to a tighter stop/go gate. The gate now asks not only whether source, env, surface, and snapshot are plausible, but whether the capture backend is exactly the accepted trace surface and whether the stable aliases point at the current wrapper.

## Why it matters

The latest online check reinforced that backend identity is semantic, not cosmetic: Transformers backends have different mask conventions, and PyTorch SDPA/Flash-style paths are optimized dense/baseline paths rather than the eager Llama hook this adapter captures. Without a backend identity gate, a future operator could produce a good-looking trace from the wrong surface.

## Still blocked here

- `transformers_not_importable_runtime_surface_unchecked`
- `complete_tinyllama_snapshot_not_available`
- `cuda_not_available_named_hardware_timing_unchecked`

## Refactor performed

Top-level guidance now points to one stable command: `ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`. Historical revision-specific wrappers remain as provenance only.

## Decision

Do not add more doctrine before repairing the runtime/snapshot blockers or running the current alias in a suitable environment.
