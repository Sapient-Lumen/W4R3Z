# Mission audit — REV0132

Package: `CloudtainerML-rev0132-2026.07.07.19.43-selectedsnapshotcontract-fox`  
Status: `pass_with_blockers` / non-promotional

## Focus

Work the riskiest live-lane seam left after REV0131: a gate could prove that *some* digest-verified TinyLlama snapshot exists while the actual loader still receives the public model id and resolves a different cache candidate. That would make the hash proof about one local path and the captured tensors potentially about another.

## Changes made

- Refactored `tools/public_trace_capture_start_preflight_report.py` so it selects a concrete digest-verified local snapshot path and writes `artifacts/runtime/CURRENT_PUBLIC_TRACE_CAPTURE_ENV.sh` plus `artifacts/run-manifests/REV0132_PUBLIC_TRACE_CAPTURE_ENV.sh`.
- Updated `REV0132_RUN_TINYLLAMA_PUBLIC_TRACE.sh` and `REV0132_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh` to source the fresh capture env after strict preflight and before model loading.
- Changed one-shot capture to require the selected `LOCAL_SNAPSHOT_DIR`; it no longer falls back to loading by model id after a digest proof.
- Added `tools/public_trace_selected_snapshot_contract_audit.py` and smoke coverage for the selected-snapshot contract.
- Kept downloads confined to snapshot preparation; evidence capture remains `ALLOW_DOWNLOAD=0`, local-only, digest-gated, and non-promotional until a real trace is produced.

## Online-grounded basis

- Transformers offline/firewalled use requires model files to be downloaded/cached ahead of time: https://huggingface.co/docs/transformers/en/installation
- Hugging Face Hub downloads return local cache paths and cache files in a version-aware way: https://huggingface.co/docs/huggingface_hub/en/guides/download
- Hugging Face Hub cache layout has explicit `snapshots/<commit>` directories: https://huggingface.co/docs/hub/en/local-cache

## Remaining blockers here

- No complete local digest-authenticated TinyLlama snapshot is present in this cloudtainer.
- `transformers` is not available in this capture runtime.
- No real public trace NPZ/provenance, selector/evaluation receipts, handoff archive, or named-hardware timing exists.

## Next useful command

```bash
HASH_WEIGHTS=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh
ALLOW_DOWNLOAD=0 CAPTURE_LOCAL_ONLY=1 bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```
