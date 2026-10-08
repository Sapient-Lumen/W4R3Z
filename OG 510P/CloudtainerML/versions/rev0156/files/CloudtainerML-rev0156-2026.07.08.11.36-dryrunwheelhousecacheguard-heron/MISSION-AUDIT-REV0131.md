# Mission audit — REV0131

Package: `CloudtainerML-rev0131-2026.07.07.19.12-preflightreportrefactor-raven`  
Status: `pass_with_blockers` / non-promotional

## Focus

Work the riskiest remaining live-lane mismatch: capture preflight could be run with `ALLOW_DOWNLOAD=1` and not complain about a missing local snapshot, while the actual public evidence capture wrapper does not pass `--allow-download` to the Hugging Face loader. That means the wrapper could pass too much preflight, then fail later in model loading.

## Changes made

- Added `tools/public_trace_capture_start_preflight_report.py` to emit a machine-readable start decision before model loading.
- Forced `REV0131_RUN_TINYLLAMA_PUBLIC_TRACE.sh` and `REV0131_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh` to treat evidence capture as local-only: `ALLOW_DOWNLOAD=0`, `CAPTURE_LOCAL_ONLY=1`, and no capture download branch.
- Added `--capture-local-only` semantics to `tools/public_trace_env_preflight.py` and `tools/public_trace_fast_prereq_gate.py`.
- Added `tools/public_trace_capture_local_only_contract_audit.py` and smoke coverage so the download lane stays confined to snapshot preparation.
- Refactored `tools/revision_metadata_coherence_audit.py` to catch mixed-case stale current revision references such as `Rev0129`, not only `rev0129` or `REV0129`.

## Online-grounded basis

- Hugging Face Transformers offline mode requires model files to be downloaded and cached ahead of time: https://huggingface.co/docs/transformers/en/installation
- Hugging Face Hub `snapshot_download()` is the materialization/cache path for repository snapshots: https://huggingface.co/docs/huggingface_hub/en/guides/download
- Safetensors metadata parsing is cheap structural evidence, but full-byte digest verification is still needed for authenticity: https://huggingface.co/docs/safetensors/en/metadata_parsing

## Remaining blockers here

- No complete local digest-authenticated TinyLlama snapshot is present in this cloudtainer.
- `transformers` is not available in this capture runtime.
- No real public trace NPZ/provenance, selector/evaluation receipts, handoff archive, or named-hardware timing exists.

## Next useful command

```bash
HASH_WEIGHTS=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh
ALLOW_DOWNLOAD=0 CAPTURE_LOCAL_ONLY=1 bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```
