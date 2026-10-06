# DeriveBSD rev0510 risk-first audit: Capsicum bridge and real-apply gate

## Scope

This cut closes the packaging gap left by the unfinished rev0510 work and keeps the focus on the removable-media local fallback lane. The risk being reduced is not a missing registry entry; it is the chance that cloudtainer fixture evidence drifts into a false production claim.

## Main correction

The FreeBSD-shaped backend runner now has a typed Capsicum worker bridge instead of an implicit future TODO hidden behind the real-apply refusal gate. The bridge binds the checked-in C worker source, source digest, cloudtainer syntax-probe boundary, production-only FreeBSD execution claim, delegated fd contract, and backend integration summary.

The real apply path remains refused with `capsicum-worker-required-for-real-apply` until a real FreeBSD host build/exec path exists. That refusal is intentional: the Python fd worker is fixture-only and must not become the accidental production worker.

## Files of interest

- `tools/removable_media_capsicum_worker_bridge.py`
- `tools/check_removable_media_local_fallback_capsicum_worker_bridge.py`
- `spec/removable.media.capsicum.worker.bridge.schema.json`
- `spec/examples/removable.media.capsicum.worker.bridge.json`
- `validation/removable-media-capsicum-worker-bridge.receipt.json`
- `docs/current/removable-media-capsicum-worker-bridge.md`
- `tools/run_removable_media_local_freebsd_backend.py`
- `tools/check_removable_media_local_fallback_freebsd_backend_run.py`
- `tools/check_removable_media_local_fallback_vertical_slice.py`

## Audit/refactor result

The previous backend code shape carried unreachable-looking host work behind a real-apply refusal gate. That was risky because it could rot silently or invite someone to wire the Python fixture worker into a real host path. This cut removes that dead host-operation branch from `build_apply_receipt()` and replaces it with a narrower, checked preflight/refusal function.

The backend receipt now binds `worker_bridge`, and fixture worker evidence explicitly records `python-fd-worker-cloudtainer-fixture-only`, `real_apply_python_fixture_worker_allowed = false`, and `real_apply_requires_capsicum_worker_bridge = true`.

## Final audit/refactor additions

A late audit found two concrete packaging/host-proof risks and corrected them before the linked cut. First, the C worker scaffold now validates that delegated fd 3 and fd 4 are regular files with `fstat` after `cap_enter()`; this keeps the future worker from accepting a pipe, device, or socket as if it were the preserved-CAS input/output contract. Second, compile-probe evidence no longer stores sandbox-absolute source/include paths: `tools/removable_media_capsicum_worker_bridge.py` emits repository-relative probe command arguments, and `tools/check_removable_media_local_fallback_capsicum_worker_build.py` reuses that same command generator while writing `validation/removable-media-capsicum-worker-build-probe.receipt.json`.

A separate archive-hygiene correction adds `tools/check_no_python_bytecode_artifacts.py` and runs hygiene children with `-B` plus `PYTHONDONTWRITEBYTECODE=1`, so linked revision zips should not carry interpreter-local `__pycache__`, `.pyc`, or `.pyo` artifacts.

## Evidence run

The release-critical hygiene ledger for this cut is stored at:

`session-reviews/DeriveBSD-rev0510-2026.06.04-release-critical-hygiene-ledger.json`

The linked package should be treated as a cloudtainer proof and contract package, not as evidence that a real FreeBSD mount/Capsicum worker has executed.

## Remaining risk

The highest remaining risk is still host proof. The next substantive step is to run the bridge on a FreeBSD host: compile the C worker against the real Capsicum header, mount a disposable device/image read-only and untrusted, capture via the safe-capture contract, unmount before worker launch, exec the C worker with only fd 3 and fd 4, and bind the binary digest and command results into the same receipt family.

The second risk remains front-door bloat. The budget guard passes, but the front-door files are still larger than their original observed baselines; future cuts should prefer sharding/generated surfaces over more hand-maintained front-door growth.
