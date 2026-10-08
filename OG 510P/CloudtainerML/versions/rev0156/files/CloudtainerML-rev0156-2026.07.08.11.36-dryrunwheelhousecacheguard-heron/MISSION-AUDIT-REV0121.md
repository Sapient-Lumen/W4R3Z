# Mission audit — REV0121 snapshot integrity phase guard

Status: `pass_with_blockers`  
Promotion allowed: `false`  
Package: `CloudtainerML-rev0121-2026.07.06.20.43-snapshotintegrityphaseguard-kite`

## What changed substantively

Rev0121 repairs a blocker that was easy to miss because the previous smoke tests passed: local-only snapshot preparation still stopped on `transformers_not_importable`, even though snapshot verification/materialization is the step meant to repair the model-source blocker before capture. The live path now separates two phases:

- `snapshot` phase: verify/materialize TinyLlama snapshot material without importing `transformers`.
- `capture` phase: fail fast unless `transformers`, `torch`, `safetensors`, a valid snapshot, and later named-hardware timing are available.

The revision also makes snapshot readiness harder to fake. The materializer/intake path now uses a shared integrity layer that checks required files, size minima, parseable config JSON, exact TinyLlama/Llama config fields, safetensors header structure, required tensor names, tensor offsets, and sparse-file materialization.

## Riskiest defect corrected

A directory with the seven expected filenames could previously be accepted as `complete_required_snapshot`. That was a severe evidence risk: it could allow later work to spend time debugging model-load failures after the archive had already claimed the snapshot blocker was repaired. `tools/snapshot_integrity_contract_audit.py` now creates a throwaway filename-only fake snapshot and proves it is rejected.

## What remains blocked here

- `transformers` is still not importable in this runtime.
- No complete integrity-valid TinyLlama snapshot is mounted in this capsule.
- No named CUDA timing device is available here.
- No immutable public trace/provenance NPZ or selector/evaluation receipt has been promoted.

## Next high-leverage work

Mount or materialize the exact TinyLlama snapshot and rerun `bash artifacts/capture-kit/PREPARE_CURRENT_PUBLIC_TRACE_SNAPSHOT.sh`. Once the snapshot integrity gate passes, install/repair the capture runtime and run `bash artifacts/capture-kit/RUN_CURRENT_PUBLIC_TRACE.sh` on named hardware.
