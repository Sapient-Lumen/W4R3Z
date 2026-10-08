# MISSION-AUDIT-REV0120 — snapshot prepare phase fix

Revision: `rev0120`  
Package: `CloudtainerML-rev0120-2026.07.06.20.12-snapshotpreparephasefix-tern`  
Status: `pass_with_blockers`  
Promotion allowed: `false`

## Heart of the mission

CloudtainerML is valuable as a claim compiler, not a registry. It should turn architectural claims into executable falsifiers, source locks, trace receipts, selector/evaluation gates, and named-hardware timing boundaries.

## Risk chosen this turn

The riskiest unfinished path remains the public TinyLlama trace lane. Rev0119 correctly stopped the live path quickly, but it also exposed a priority bug: snapshot preparation could be blocked by capture-runtime prerequisites and stale top-level wrapper references before the archive even tried to repair the independent model-source blocker.

## Concrete change

- Split snapshot preparation from capture runtime readiness.
- In download mode, `public_trace_fast_prereq_gate.py` now hard-blocks only true snapshot-preparation blockers such as missing `huggingface_hub`, broken shell closure, insufficient disk, or stale current aliases; missing `transformers` is recorded as a deferred capture blocker.
- `REV0120_PREPARE_TINYLLAMA_SNAPSHOT.sh` runs source/packet/static checks and then `hf_snapshot_dry_run_audit.py` + `hf_snapshot_materializer.py` before collecting nonfatal dependency/env receipts.
- Added `tools/snapshot_prepare_phase_order_audit.py` and smoke coverage so dependency/env probes cannot drift back before the snapshot materializer.
- Repaired top-level stale entrypoint references so `current_entrypoint_consistency_audit.py` passes again.

## What changed philosophically

A blocker should be repaired in the phase where it belongs. Missing model material and missing `transformers` are both real blockers, but they are independent. The cube should not use one blocker as an excuse to skip the other repair path.


## Local validation receipts

- `python3 tools/public_trace_fast_prereq_gate.py --local-only --strict` returns `blocked_here_fast_prereq` with `complete_tinyllama_snapshot_not_available` and `transformers_not_importable`.
- `ALLOW_DOWNLOAD=1 python3 tools/public_trace_fast_prereq_gate.py --download --strict` returns `pass`, deferring `transformers_not_importable` until after snapshot materialization.
- `bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh` exits in about 1.84 seconds here with the same two explicit blockers, confirming the anti-waste front gate still protects strict capture.
- Metadata coherence, current live-script dependency closure, current entrypoint consistency, source lock, trace run packet, snapshot phase-order, and readiness fail-fast contract audits pass.

## Online source check

- Hugging Face Transformers documents that offline use requires downloaded/cached model files ahead of time and points to `snapshot_download` for preparing repositories.
- Hugging Face Hub documents `snapshot_download` support for `revision`, `local_files_only`, `allow_patterns`, and `dry_run`, plus `IncompleteSnapshotError` when a requested local-only snapshot is incomplete.
- PyTorch documents CUDA events as device synchronization/timing markers, which keeps named-hardware timing separate from this CPU-only prerequisite phase.

## What is still missing

- Complete runtime stack with `transformers` importable.
- Complete reviewed TinyLlama snapshot at `fe8a4ea1ffedaf415f4da2f062534de366a451e6`.
- Real public trace NPZ/provenance pair.
- Selector/evaluation receipts over that real trace.
- Named-hardware CUDA timing receipts.

## Next command

```bash
ALLOW_DOWNLOAD=1 bash artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh
```

Expected in this capsule if network/package policy remains constrained: exact snapshot/download or dependency blockers, not more doctrine.
