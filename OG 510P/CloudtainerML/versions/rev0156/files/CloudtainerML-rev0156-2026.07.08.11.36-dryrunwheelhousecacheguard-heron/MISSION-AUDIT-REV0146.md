# Mission audit — REV0146 localcachecontract-heron

## Heart of the mission

CloudtainerML is a claim compiler: claim → hostile falsifier → digest-bound trace/provenance receipts → replayable selector gates → named-hardware timing → promote/kill/pivot. The heart is still one real TinyLlama public trace that can be replayed and falsified, not more registry surface.

## What was riskiest this turn

The active runner had become much less likely to fail from shell drift, preflight duplication, or missing import checks, but it still carried a hidden-state risk: Hub, Transformers, and Xet bytes could live in the operator's global cache. That means a first trace might depend on stale machine-global files, contaminate future runs, or make cleanup/replay ambiguous. For a 2.2GB-ish model snapshot, that is both a reproducibility risk and a waste risk.

## Online grounding used

- Hugging Face documents that `huggingface_hub` environment variables are read at import time; therefore cache env vars must be set before Hub/Transformers imports.
- Hugging Face documents `HF_HOME`, `HF_HUB_CACHE`, `HF_XET_CACHE`, and `HF_ASSETS_CACHE` as cache/storage controls, with `HF_HUB_CACHE` defaulting under `HF_HOME`.
- Transformers documents that offline use requires the model repository to be downloaded/cached ahead of time, then loaded with `HF_HUB_OFFLINE=1` or `local_files_only=True`.
- Hugging Face's download guide documents `snapshot_download()` for entire-repository snapshots at a specific revision and notes custom cache locations through `cache_dir`/`HF_HOME`.
- TinyLlama's model card still confirms the target is a compact Llama-compatible model needing Transformers support.

## What changed

- Added `tools/public_trace_cache_root_contract_audit.py`.
- Defaulted public-trace cache state to `artifacts/runtime/public-trace-hf-cache` through `PUBLIC_TRACE_CACHE_ROOT`.
- Exported `HF_HOME`, `HF_HUB_CACHE`, `HF_XET_CACHE`, and `HF_ASSETS_CACHE` from active bootstrap, snapshot-prepare, one-command, run, and one-shot wrappers before the Python Hub stack can import.
- Persisted the cache-root contract into generated bootstrap/capture env files. The capture env now computes its root dynamically from `BASH_SOURCE[0]` instead of baking this cloudtainer's absolute extraction path.
- Added the cache-root contract to the TinyLlama run packet, source lock, and external runner builder/manifest.
- Removed stale derived external-runner rev0145 packets before rebuilding the current runner.

## Validation status

- `RUN_CURRENT_FIRST_REAL_TRACE.sh` reaches the expected cloudtainer blocker: runtime import smoke cannot import `transformers` here.
- `RUN_CURRENT_PUBLIC_TRACE.sh` reaches the expected capture-start blocker: no digest-verified local TinyLlama snapshot and no `transformers`.
- Static audits for live script dependencies, revision metadata coherence, run manifest coherence, bootstrap runtime, cache-root contract, offline quarantine, snapshot digest cache, source lock, and external runner retention are intended to be part of this revision's smoke surface.

## What is still missing

A real public trace is still missing. This revision does not promote any scientific claim. It reduces the chance that the first successful capable-machine trace will be non-reproducible because it quietly depended on a global cache.

## Next best move

Run `BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash RUN_FIRST_REAL_TRACE.sh` from `REV0146_PUBLIC_TRACE_EXTERNAL_RUNNER.zip` on a capable machine. Keep the project-local cache root unless there is a deliberate reason to set `PUBLIC_TRACE_CACHE_ROOT=/path/to/cache`, and preserve the resulting status/trace/receipt artifacts.
