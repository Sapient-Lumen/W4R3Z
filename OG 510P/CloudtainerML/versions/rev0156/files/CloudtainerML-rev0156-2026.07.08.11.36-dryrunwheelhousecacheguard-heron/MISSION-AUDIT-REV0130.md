# Mission audit — REV0130

Package: `CloudtainerML-rev0130-2026.07.07.18.46-hashpreflightcontract-puma`  
Status: `pass_with_blockers` / non-promotional

## Focus

Work the riskiest incomplete lane: prevent a mounted or newly materialized TinyLlama snapshot from advancing to public trace capture merely because it is structurally plausible. This turn should reduce wasted live-run time, not add another registry layer.

## Finding

Rev0129 fixed a real local-only deadlock: a mounted snapshot no longer requires `huggingface_hub` just to be inspected. The next hole was digest timing and enforcement. Several gates could still distinguish “snapshot files exist and parse” from “snapshot bytes are exactly the pinned public model” only late in the one-shot capture path. That leaves an avoidable failure mode: a wrong-weight or unhashed 2.2GB safetensors file can survive too much preflight, only to fail when the model capture helper finally enforces `--require-model-safetensors-sha256`.

The second practical problem was timeout shape. The readiness gate used a short generic probe timeout for all steps, even though snapshot materialization and full SHA-256 over a 2.2GB weight file are not the same kind of operation as a static probe. That can make the reviewed download/digest path fail for scheduler reasons rather than evidence reasons.

## Changes made

- Refactored `tools/public_trace_fast_prereq_gate.py` with `--require-weight-hash`, `hash_verified_snapshot_available`, and pinned `EXPECTED_MODEL_SAFETENSORS_SHA256` reporting.
- Refactored `tools/public_trace_env_preflight.py` with `--require-weight-hash`, `found_digest_verified_integrity_snapshot`, and local-only digest blockers.
- Refactored `tools/public_trace_readiness_gate.py` so snapshot materialization receives `SNAPSHOT_GATE_STEP_TIMEOUT` instead of the short generic `TRACE_GATE_STEP_TIMEOUT`; readiness materialization also passes `--include-hashes` by default when `HASH_WEIGHTS=1`.
- Updated `REV0130_RUN_TINYLLAMA_PUBLIC_TRACE.sh` and `REV0130_ONE_SHOT_PUBLIC_TRACE_CAPTURE.sh` to require hash-aware preflight before capture.
- Updated `REV0130_PREPARE_TINYLLAMA_SNAPSHOT.sh` so `HASH_WEIGHTS` defaults to `1`, while allowing operators to override it only for structural/debug runs.
- Added `tools/public_trace_hash_preflight_contract_audit.py` and smoke checks so the digest preflight contract cannot silently regress.
- Updated the run packet and trace-run packet audit with explicit hash-preflight and snapshot-timeout contract markers.

## Online-grounded basis

The external docs reinforce the direction: Transformers offline mode requires downloaded/cached files ahead of time; Hub downloads are cached/versioned and `snapshot_download()` is the repository materialization path; `HF_HUB_OFFLINE=1` makes cache completeness decisive; and safetensors header parsing is cheap structural metadata, not a full-byte authenticity proof.

## What remains blocked here

- This cloudtainer still does not contain a complete digest-authenticated TinyLlama snapshot.
- `transformers` is still not available here for real capture.
- No immutable public NPZ/provenance trace, accepted selector/evaluation receipts, handoff archive, or named-hardware timing exists.

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
