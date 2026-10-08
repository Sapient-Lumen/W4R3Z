# Mission audit — REV0099

Status: `pass_with_blockers`  
Promotion allowed: `false`

## What changed

This revision moves the riskiest unfinished lane closer to execution without adding doctrine. The readiness gate now checks runtime dependencies/capabilities and performs a Hugging Face snapshot dry-run before any full TinyLlama materialization. It also trims a duplicated open-question surface so the next operator sees one current set of questions.

## Why it matters

The previous gate could still fail late or expensively: after source/backend checks, it could attempt a large snapshot operation without first proving the network/token/revision/file plan. rev0099 inserts a bandwidth/time safety valve. A failed dry-run now blocks the materializer and names the problem before any full fetch.

## Still blocked here

- `transformers_not_importable_runtime_surface_unchecked`
- `hf_snapshot_network_dry_run_not_successful_here`
- `complete_tinyllama_snapshot_not_available`
- `cuda_not_available_named_hardware_timing_unchecked`

## Refactor performed

`OPEN-QUESTIONS.md` is canonical and `OPEN_QUESTIONS.md` is now only a current compatibility shim. The active capture path remains the stable alias:

```bash
ALLOW_NETWORK_DRY_RUN=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```

## Decision

Do not add more registries before running the dependency/dry-run/snapshot/capture chain in a capable reviewed environment. If the dry-run fails, repair network/token/revision access; if it passes and materialization succeeds, run the actual trace immediately.
