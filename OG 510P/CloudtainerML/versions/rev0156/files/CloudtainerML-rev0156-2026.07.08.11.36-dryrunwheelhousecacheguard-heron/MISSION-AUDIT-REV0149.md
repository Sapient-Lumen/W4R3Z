# Mission audit — REV0149 runnerclosuretrim-hawk

Status: `runner-surface-refactor-not-evidence`  
Promotion allowed: `false`

## Heart of the mission

The cube should compile claims into executable, hostile-to-itself evidence: locked public model material, digest-bound capture, local-only replay, selector receipts, and named-hardware timing. The riskiest unfinished step is still the first real TinyLlama trace; every turn should remove a blocker on that path or reduce waste around it.

## What changed

REV0149 attacks two concrete waste/failure modes.

First, the external runner packet was described as compact but still copied the whole `tools/` tree. That makes the next operator carry stale probes and doctrine surface unrelated to first trace completion. The runner builder now targets the first-real-trace live-script closure instead: stable aliases, current REV0149 capture/prepare/bootstrap scripts, reachable tool scripts, and the public-trace experiment files plus their attention-core dependency.

Second, the runtime import smoke could spend CPU importing heavy libraries even when a cheaper missing-module check had already doomed the run. It now does cheap module discovery first and only imports the heavy stack when all required modules are present. In this cloudtainer it blocks immediately on `transformers_not_present_in_runtime_python` and records `heavy_runtime_imports_skipped_until_required_modules_are_present` instead of burning CPU proving irrelevant imports.

## Online research basis

The current Hugging Face Hub docs still make project-local cache binding and early env export materially important: Hub environment variables are read at import time, and `HF_HOME`, `HF_HUB_CACHE`, `HF_XET_CACHE`, plus download/offline controls determine cache and network behavior. The download docs also support `snapshot_download` filtering/dry-run and note `hf_xet` for large-file transfer, so the runner should plan bytes and bind cache before capture. Current Transformers attention docs keep `attn_implementation` and attention-mask behavior backend-sensitive, so the first trace remains an eager-attention evidence lane rather than a fused-kernel timing claim.

## Why this is substance, not registry work

The change is executable. The builder now emits a closure audit that fails if reachable scripts/imports are missing or if unrelated `tools/`/`experiments/` files creep back into the runner. Extracted-runner smoke passes closure, first-trace surface, cache-root, runtime-lock, runtime-import, snapshot-download-plan, stable public-run, and direct-current-alias checks. The first-real-trace full command is syntax-smoked in the builder and was separately run in the source tree; it now reaches the intended runtime blocker rather than a packaging, shell, or heavy-import hang.

## Validation snapshot

- `revision_metadata_coherence_audit.py`: pass.
- `current_live_script_dependency_audit.py`: pass.
- `public_trace_external_runner_closure_audit.py --strict --runner-root artifacts/external-runner/REV0149_PUBLIC_TRACE_EXTERNAL_RUNNER`: pass.
- `public_trace_first_real_trace_audit.py --mode surface`: pass.
- `public_trace_runtime_requirement_lock_audit.py --strict`: pass.
- `public_trace_snapshot_download_plan_gate_audit.py`: pass.
- `current_external_runner_retention_audit.py`: pass with zero stale external-runner packets.
- `RUN_CURRENT_FIRST_REAL_TRACE.sh`: reaches `blocked_here_runtime_import_smoke` with `transformers_not_present_in_runtime_python` here.
- `RUN_CURRENT_PUBLIC_TRACE.sh`: reaches intended preflight blockers here: missing digest-verified TinyLlama snapshot, missing local snapshot integrity, and missing `transformers`.

## Remaining blocker

This environment still lacks the digest-verified TinyLlama snapshot and capture runtime. The next capable-machine action is still:

```bash
BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash RUN_FIRST_REAL_TRACE.sh
```

If that fails, repair the first receipt-backed blocker it returns before adding more doctrine.
