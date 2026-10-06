# DeriveBSD rev0516 risk-first fd-5 inheritance proof audit

This cut packages the r548 host-smoke failure-shaping work and corrects the highest-risk proof gap found while reviewing the removable-media FreeBSD/Capsicum bridge.

## Main finding

The bridge execution probe created a broker-owned fd-5 canary in the parent process, but the probe subprocess only passed fd 3 and fd 4. That made the canary proof weaker than the receipt claimed: the worker could report that fd 5 was closed simply because Python never delivered fd 5 to the child.

## Change

`tools/removable_media_capsicum_worker_bridge.py` now launches probe subprocesses with `pass_fds=(3, 4, 5)` and records `pass_fds = [3, 4, 5]` plus `extra_fd_canary_passed_to_child = true` in each probe case.

`tools/freebsd/rm_post_detach_capsicum_worker.c` now observes fd 5 before `closefrom(FD_AFTER_DELEGATED_SET)`, stores that state, and reports `extra_fd_canary_observed_before_closefrom`. Successful and post-stdio failure probes must report both `extra_fd_canary_observed_before_closefrom = true` and `extra_fds_closed_before_cap_enter = true`.

`tools/check_removable_media_local_fallback_capsicum_worker_bridge.py`, `tools/check_removable_media_local_fallback_capsicum_worker_source.py`, and `tools/check_removable_media_local_fallback_vertical_slice.py` now reject a proof that creates a parent fd-5 canary without proving child inheritance and worker observation before closefrom.

## Evidence refreshed

Refreshed:

- `spec/examples/removable.media.capsicum.worker.bridge.json`
- `validation/removable-media-capsicum-worker-bridge.receipt.json`
- `spec/examples/removable.media.local.freebsd.backend.run.receipt.json`
- `validation/removable-media-local-freebsd-backend-run.receipt.json`
- `validation/removable-media-local-freebsd-host-smoke.refusal.json`
- `validation/removable-media-local-freebsd-host-smoke.failure-simulation.json`
- `spec/examples/cube.schema.audit.report.json`
- `spec/examples/cube.schema.refactor.backlog.json`
- `spec/examples/cube.hygiene.checkset.manifest.json`
- `spec/examples/cube.hygiene.run.ledger.json`

## Audit/refactor note

This is a small but important anti-theatre correction. The project had a good invariant name but insufficient execution evidence. The change makes the check prove the thing the receipt says: fd 5 existed in the child before the worker closed fd 5 and above.

## Validation

The included release-critical ledger is:

`session-reviews/DeriveBSD-rev0516-2026.06.05-release-critical-hygiene-ledger.json`

Final status: `33 / 33`, `run_complete = true`, `result = passed`.

Key direct checks passed after the ledger copy:

- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_source.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_build.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_bridge.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_backend_run.py`
- `python3 -B tools/check_removable_media_local_fallback_vertical_slice.py`
- `python3 -B tools/check_cube_hygiene_run_ledger.py`
- `python3 -B tools/check_generated_artifact_version_ids.py`
- `python3 -B tools/check_generated_docs.py`
- `python3 -B tools/validate_spec_examples.py`
- `python3 -B tools/check_no_python_bytecode_artifacts.py`

## Remaining risk

The project still needs the real FreeBSD host proof: run the host-smoke runner as root on FreeBSD against a disposable image, bind the compiled C worker binary digest, perform real mount/umount/mdconfig attach-detach, and preserve the same receipt contract.
