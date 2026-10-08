# Mission audit — REV0129

Package: `CloudtainerML-rev0129-2026.07.07.18.17-snapshotlocalgatefix-sable`  
Status: `pass_with_blockers` / non-promotional

## Focus

Work the riskiest incomplete lane: getting from offline/mounted model material to real public trace without another avoidable preflight deadlock.

## Finding

Rev0128 correctly moved env preflight to the shared snapshot integrity contract, but the earlier fast-prereq gate still had a contradiction: snapshot phase always required `huggingface_hub`, even in local-only verification mode. That means an external runner could mount a complete exact TinyLlama snapshot and still be stopped before the local integrity checker reads it, just because the Hub client is missing.

That is wasteful and backwards. `huggingface_hub` is required to download/materialize from the Hub; it is not required to verify existing local files with `hf_snapshot_integrity.py`.

## Changes made

- Refactored `tools/public_trace_fast_prereq_gate.py` so `huggingface_hub_not_importable_for_snapshot_materialization` is a hard blocker only in download mode.
- Added `tools/public_trace_snapshot_local_only_gate_audit.py`.
- Wired the new audit into `REV0129_PREPARE_TINYLLAMA_SNAPSHOT.sh` and `REV0129_RUN_TINYLLAMA_PUBLIC_TRACE.sh`.
- Updated `tools/smoke_validate.py` to prevent the unconditional snapshot-module blocker from returning.
- Updated `artifacts/run-manifests/REV0129_TINYLLAMA_PUBLIC_TRACE_RUN_PACKET.json` and `tools/trace_run_packet_audit.py` with explicit local-only/download gate contract markers.
- Added online-grounded research notes in `artifacts/research/REV0129_SNAPSHOT_LOCAL_ONLY_GATE_RESEARCH.*`.

## What remains blocked here

- No complete digest-authenticated TinyLlama snapshot exists in this cloudtainer.
- `transformers` is not available here for real capture.
- No immutable NPZ/provenance trace, selector/evaluation receipts, handoff archive, or named-hardware timing exists.

## Next useful command

```bash
LOCAL_SNAPSHOT_DIR=/path/to/TinyLlama-snapshot HASH_WEIGHTS=1 bash artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh
bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```

If no local snapshot is mounted, use:

```bash
HASH_WEIGHTS=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh
bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh
```

Do not add doctrine unless this live path yields a new concrete failure.
