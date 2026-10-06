# DeriveBSD rev0516 risk-first worker-input digest / host-smoke audit

Last updated: 2026-06-05r548

## Focus

This cut stayed on the removable-media local fallback lane. The highest-value risk was not another registry surface; it was an implementation-proof gap in the future FreeBSD/Capsicum host smoke path.

The host-smoke plan and docs already said the worker-observed input digest should match the preserved safe-capture CAS object, but the checked-in C worker only reported the number of bytes read from fd 3. That proved descriptor shape and byte count, not that the worker processed the intended preserved object.

## Main correction

`tools/freebsd/rm_post_detach_capsicum_worker.c` now computes SHA-256 over delegated fd 3 and emits:

`input_sha256`

in the worker success report.

The implementation is deliberately local to the worker source for the current smoke scaffold so the cloudtainer compile/execution probe can catch drift without adding a new external dependency.

## Evidence tightened

Updated bridge and host-smoke evidence now requires the digest binding end to end:

- `tools/removable_media_capsicum_worker_bridge.py` runs the cloudtainer shim execution probe with known fd-3 bytes and verifies the emitted `input_sha256`.
- `tools/freebsd/run_removable_media_local_fallback_host_smoke.py` requires `worker_input_sha256_matches_capture_digest` before a real FreeBSD host smoke can pass.
- `tools/check_removable_media_local_fallback_capsicum_worker_source.py` requires the C worker to update/finalize the SHA-256 context and emit `input_sha256`.
- `tools/check_removable_media_local_fallback_capsicum_worker_bridge.py`, `tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py`, and `tools/check_removable_media_local_fallback_vertical_slice.py` all bind the new field.

## Audit/refactor note

This removes a subtle self-deception path: fd-only delivery plus byte count could look like strong proof while still failing to bind the worker to the preserved CAS capture. The new proof is still a cloudtainer shim plus FreeBSD-shaped host-smoke contract, not a real FreeBSD run. The real host smoke must still compile and execute the worker on FreeBSD.

## Validation

A fresh release-critical hygiene ledger was completed for r548:

`session-reviews/DeriveBSD-rev0516-2026.06.05-release-critical-hygiene-ledger.json`

Final status: `33 / 33 release-critical checks passed`.

Targeted checks passed, including:

- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_source.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_build.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_bridge.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_backend_run.py`
- `python3 -B tools/check_removable_media_local_fallback_vertical_slice.py`
- `python3 -B tools/validate_spec_examples.py`
- `python3 -B tools/check_generated_docs.py`
- `python3 -B tools/check_cube_hygiene_run_ledger.py`
- `python3 -B tools/check_generated_artifact_version_ids.py`

`validate_spec_examples.py` validated 467 examples.

## Remaining risk

The next substantive step remains the real FreeBSD host proof: run the host-smoke path on FreeBSD, bind the compiled C worker binary digest, create and mount a disposable image read-only/untrusted, safe-capture the selected file, unmount/detach, then exec the C worker with fd 3/fd 4 and the fd-5 non-media canary while preserving this receipt family.
