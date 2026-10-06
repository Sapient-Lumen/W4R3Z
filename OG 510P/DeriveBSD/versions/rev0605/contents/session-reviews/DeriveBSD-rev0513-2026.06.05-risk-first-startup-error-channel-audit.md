# DeriveBSD rev0513 risk-first startup error-channel audit

## Scope

This cut continues the removable-media local fallback implementation lane, specifically the future FreeBSD/Capsicum worker boundary. The goal was to reduce self-deception in the post-detach worker proof rather than add another doctrine or registry surface.

## Main risk corrected

Earlier cuts moved post-stdio-close worker failures onto delegated fd 4, but the C worker still had early startup paths that used `err()` / `errx()` before stdio closure. That left an inherited stderr dependency for argv/path rejection and startup failure reporting, even though the surrounding receipt model was trying to prove an fd-only worker boundary.

rev0513 changes `tools/freebsd/rm_post_detach_capsicum_worker.c` so startup failures report through delegated fd 4 as structured JSON too. The worker no longer includes `<err.h>` and no longer calls `err()` / `errx()`. Path/device argv rejection now emits `path_arguments_rejected` through fd 4 with zero stdout/stderr output in the shim execution probe.

## Evidence added

`tools/removable_media_capsicum_worker_bridge.py` now runs a third cloudtainer shim execution probe in addition to the regular-input success probe and directory-fd failure probe:

- success: regular fd 3 input, fd 4 derivative output;
- failure: directory fd 3 reports `input_fd_not_regular` on fd 4;
- failure: path/argv rejection reports `path_arguments_rejected` on fd 4.

This remains explicitly a cloudtainer shim execution probe, not a real FreeBSD Capsicum execution claim.

## Receipt/schema/doc surfaces updated

Updated surfaces include:

- `tools/freebsd/rm_post_detach_capsicum_worker.c`
- `tools/check_removable_media_local_fallback_capsicum_worker_source.py`
- `tools/removable_media_capsicum_worker_bridge.py`
- `tools/check_removable_media_local_fallback_capsicum_worker_bridge.py`
- `tools/run_removable_media_local_freebsd_backend.py`
- `tools/check_removable_media_local_fallback_freebsd_backend_run.py`
- `tools/check_removable_media_local_fallback_vertical_slice.py`
- `spec/removable.media.capsicum.worker.bridge.schema.json`
- `spec/examples/removable.media.capsicum.worker.bridge.json`
- `validation/removable-media-capsicum-worker-bridge.receipt.json`
- `spec/removable.media.local.freebsd.backend.run.receipt.schema.json`
- `spec/examples/removable.media.local.freebsd.backend.run.receipt.json`
- `validation/removable-media-local-freebsd-backend-run.receipt.json`
- `docs/current/removable-media-capsicum-worker-bridge.md`
- `docs/current/removable-media-local-fallback-freebsd-backend-run.md`

The backend `worker_bridge` binding now carries `startup_failure_report_channel = delegated-output-fd-before-or-after-stdio-close`.

## Validation

A resumed release-critical hygiene ledger completed successfully:

`session-reviews/DeriveBSD-rev0513-2026.06.05-release-critical-hygiene-ledger.json`

Final status: 32 / 32 release-critical checks passed, with no failures or timeouts. The completed ledger was copied into `spec/examples/cube.hygiene.run.ledger.json`, and the ledger/id checks passed afterward.

Key direct checks completed during this cut included:

- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_source.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_build.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_bridge.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_backend_run.py`
- `python3 -B tools/check_removable_media_local_fallback_vertical_slice.py`
- `python3 -B tools/lint_spec_schemas.py`
- `python3 -B tools/validate_spec_examples.py`
- `python3 -B tools/check_generated_docs.py`
- `python3 -B tools/check_cube_hygiene_run_ledger.py`
- `python3 -B tools/check_generated_artifact_version_ids.py`

## Remaining highest risk

The next substantive risk remains the same: real FreeBSD host proof. The cube now has source, shim compile, shim execution, bridge receipts, and backend refusal gates. It still needs a real FreeBSD transcript that compiles the C worker, binds the binary digest, mounts a disposable image/device read-only and untrusted, performs safe capture, unmounts before worker launch, then execs the worker with only delegated fd 3 and fd 4.
