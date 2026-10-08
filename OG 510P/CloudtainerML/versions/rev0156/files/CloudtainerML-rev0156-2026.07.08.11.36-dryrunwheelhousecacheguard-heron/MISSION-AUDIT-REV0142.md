# Mission audit — REV0142

Status: `non_promotional_forward_progress`  
Promotion allowed: `false`  
Current first-trace alias: `artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh`  
Current capture alias: `artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh`  
Primary artifact: `artifacts/external-runner/REV0142_PUBLIC_TRACE_EXTERNAL_RUNNER.zip`

## Heart of the mission

CloudtainerML is still a claim compiler: the useful unit is not a registry entry but a claim that survives hostile falsification with digest-bound provenance, replayable receipts, and named-hardware timing. The immediate mission remains one real public TinyLlama trace that can be inspected, replayed, handed off, and used to promote/kill a selector claim.

## Riskiest unfinished work

The first real digest-bound TinyLlama trace still has not run in this cloudtainer. The highest-risk work is the boring execution path: model materialization, exact local binding, and first receipts on a capable machine. REV0142 therefore reduces a concrete waste mode in that path instead of expanding doctrine.

## What went wrong or wasteful

The live path can require several tools to verify the same 2.2GB `model.safetensors` digest. The full hash is essential; doing it repeatedly in adjacent gates is not. That can make a first real run feel stalled or flaky even after the snapshot is present.

A second operational hazard is slow large-file materialization. Hugging Face Hub exposes timeout controls, and the TinyLlama weight is Xet-backed and about 2.2GB. Keeping default short timeouts during the download phase is a completion risk, not a scientific safeguard.

## What changed in REV0142

- Added a stat-bound digest receipt cache in `tools/hf_snapshot_integrity.py`.
- Added `tools/snapshot_digest_receipt_cache_audit.py` with a mutation fixture: first hash computes, second unchanged hash reuses the receipt, changed file invalidates the receipt.
- Wired the digest-cache audit into the active first-real-trace, snapshot-prepare, capture, and one-shot wrappers.
- Added default `HF_HUB_DOWNLOAD_TIMEOUT=300` and `HF_HUB_ETAG_TIMEOUT=60` during snapshot materialization/bootstrap, while keeping capture local-only.
- Moved live wrappers, prompts, requirements, run packet, and source lock forward to REV0142.
- Rebuilt the compact external runner as `REV0142_PUBLIC_TRACE_EXTERNAL_RUNNER.zip`.
- Pruned stale derived REV0140/REV0141 external-runner packet copies from the hot package and recorded the action in `PRUNED-ARTIFACTS.jsonl`; prior revision archives retain history.

## Safety boundary

A stat-bound receipt is a performance guard, not a new trust primitive. The first full SHA-256 remains mandatory. Receipt reuse is allowed only when resolved path, size, mtime, ctime, device, and inode are unchanged; operators can force full rehashes with `PUBLIC_TRACE_DISABLE_DIGEST_RECEIPT_CACHE=1`.

## Decision

Run the same first-real-trace command on a capable machine:

```bash
BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/RUN_CURRENT_FIRST_REAL_TRACE.sh
```

If it fails, fix the first concrete blocker returned by that runner before adding more registries or doctrine.
