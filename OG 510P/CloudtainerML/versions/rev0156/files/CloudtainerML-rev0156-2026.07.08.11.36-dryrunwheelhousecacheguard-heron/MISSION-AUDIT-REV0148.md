# Mission audit — REV0148 downloadplangate-auk

## Heart of the mission

CloudtainerML is still a claim compiler: claim → hostile falsifier → digest-bound trace/provenance receipts → replayable selector gates → named-hardware timing → promote/kill/pivot. The heart is one real TinyLlama public trace that can be replayed and falsified, not more registry surface.

## What was riskiest this turn

The next completion risk was waste before evidence. The runner had runtime locks, local cache roots, import smoke, offline capture quarantine, and selected-snapshot handoff, but snapshot preparation could still begin a large materialization without first writing a planned file/commit/cache/disk receipt. On a capable machine, that is exactly the kind of late, expensive failure that prevents the first real trace from completing.

## Online grounding used

- Hugging Face Hub download docs support CLI and programmatic dry-run planning for `snapshot_download`, including file sizes, cache status, and whether bytes would be downloaded.
- Hugging Face Hub environment docs state that Hub env vars are read at import time and define `HF_HOME`, `HF_HUB_CACHE`, and `HF_XET_CACHE`.
- Hugging Face cache docs support cache-root and snapshot-path reasoning.
- Transformers attention docs reinforce that capture semantics remain backend-sensitive; this revision does not change the eager attention capture contract.

## What changed

- Added `tools/public_trace_snapshot_download_plan.py`.
- Added `tools/public_trace_snapshot_download_plan_gate_audit.py`.
- Wired the dry-run/byte-budget gate into `REV0148_FIRST_REAL_TRACE_ONE_COMMAND.sh` and `REV0148_PREPARE_TINYLLAMA_SNAPSHOT.sh` before `hf_snapshot_materializer.py --download`.
- Added `PUBLIC_TRACE_SKIP_DOWNLOAD_PLAN=1` as an explicit escape hatch for unusual environments; by default, `ALLOW_DOWNLOAD=1` now means plan first, materialize second.
- Rebuilt `REV0148_PUBLIC_TRACE_EXTERNAL_RUNNER.zip` so the compact runner carries the same gate.

## Validation status

Static audits pass for revision metadata coherence, run-manifest coherence, source lock, trace run packet, runtime requirements, cache-root contract, current-entrypoint dependency closure, and the new download-plan gate wiring. In this cloudtainer, live first-trace execution still stops at the intended missing-`transformers` blocker before any network/disk snapshot materialization. No public trace was claimed.

## What is still missing

A real public trace is still missing. This revision does not promote any scientific claim. It reduces the chance that the first capable-machine trace attempt wastes time or disk before proving that the snapshot download plan matches the locked TinyLlama source and local cache budget.

## Next best move

Run `BOOTSTRAP_RUNTIME=1 ALLOW_DOWNLOAD=1 bash RUN_FIRST_REAL_TRACE.sh` from `REV0148_PUBLIC_TRACE_EXTERNAL_RUNNER.zip` on a capable machine. Preserve `REV0148_PUBLIC_TRACE_SNAPSHOT_DOWNLOAD_PLAN.json` even if snapshot materialization fails; it is now the first receipt for whether the large download was safe to attempt.
