# Mission audit — REV0128 integrity preflight refactor

Status: `pass_with_blockers`  
Promotion allowed: `false`

## What changed

Rev0128 fixes the next live-run waste risk after rev0127's valid-size threshold repair. `tools/public_trace_env_preflight.py` previously had its own weak snapshot check: a handful of filenames, either tokenizer file, and no shared structural inspection. That could mark the trace environment ready even though the materializer/capture path would later reject the same snapshot for missing required files, invalid JSON/config, truncated/sparse `model.safetensors`, wrong Llama architecture fields, or bad safetensors header/offsets.

The env preflight now uses the shared import-light `hf_snapshot_integrity.py` contract through `inspect_snapshot()` and `snapshot_candidate_paths()`. It reports `found_complete_integrity_snapshot`, mirrors that value into the old compatibility key, and emits a stronger blocker: `no_integrity_valid_local_hf_snapshot_and_download_not_allowed`.

## Online basis

- Hugging Face Transformers offline docs say offline/firewalled use requires downloaded and cached model files ahead of time, with `HF_HUB_OFFLINE=1` or `local_files_only=True` used to prevent Hub calls during loading.
- Hugging Face Hub download docs say `snapshot_download()` downloads a repository at a selected revision, caches it locally, and supports filtered file materialization with `allow_patterns`/`ignore_patterns`.
- The TinyLlama file tree publishes concrete sizes for the required snapshot files, including the small 608-byte `config.json` and 2.2 GB `model.safetensors`; those source-observed sizes justify structural integrity checks rather than loose filename presence.

## Audit/refactor performed

- `tools/public_trace_env_preflight.py`
  - Replaced the local filename/minimum-file cache probe with `integrity_snapshot_status()` backed by `hf_snapshot_integrity.inspect_snapshot()`.
  - Exposes `snapshot_integrity_contract: hf_snapshot_integrity_v1`, `shared_integrity_snapshot_preflight: true`, and `found_complete_integrity_snapshot`.
  - Keeps the old `found_complete_minimum_snapshot` field as a stricter compatibility mirror, not as the decision source.
- `tools/public_trace_env_snapshot_integrity_audit.py`
  - New static audit to prevent the weak cache check from returning.
  - Verifies the current run and snapshot-prepare wrappers execute the audit.
- `artifacts/capture-kit/REV0128_*`
  - Current wrappers updated to run the new audit and to target rev0128 prompt/run assets.
- `tools/smoke_validate.py`
  - Adds regression checks for shared snapshot integrity markers and absence of `cache_snapshot_status`.

## What remains blocked here

- The complete digest-authenticated TinyLlama snapshot is still absent in this cloudtainer.
- `transformers` runtime is still absent here.
- No real public TinyLlama trace, selector/evaluation receipts, handoff archive, or named-hardware timing were generated in this environment.

## Next command

```bash
HASH_WEIGHTS=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh && bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```

If this still cannot materialize a valid snapshot/runtime, the next useful move is to package a minimal external runner checklist rather than adding more doctrine.
