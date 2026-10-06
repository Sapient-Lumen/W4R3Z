# DeriveBSD rev0517 risk-first host-smoke success/fd-slot audit

Latest cut: 2026-06-05r549

## Focus

The riskiest unfinished lane remains removable-media local fallback, specifically the first real FreeBSD host proof. rev0516 had refusal evidence and a mount-failure simulation, but the successful host-smoke orchestration path was still not exercised end-to-end in the cloudtainer.

## Main changes

- Added `validation/removable-media-local-freebsd-host-smoke.success-simulation.json` through `tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py`.
- The success simulation drives the full host-smoke order with fake host commands and real safe-capture semantics: compile worker, makefs image, mdconfig attach, fstyp verify, mount, safe capture, umount, mdconfig detach, worker launch.
- The worker side of the simulation proves `input_sha256` equals the preserved CAS digest, fd-5 was observed before closefrom, extra fds are closed before capability entry, stdout/stderr byte counts are zero, and the run does not claim real FreeBSD execution.
- The vertical-slice check now requires the host-smoke refusal, failure simulation, and success simulation together.

## Audit/refactor correction

The success simulation exposed a concrete host-smoke seam: `run_host_smoke()` already passed a private `worker_cwd` argument to the default `run_worker()`, but `run_worker()` did not accept it. That would have made the future real FreeBSD success path fail late as a receipt-shaped worker-launch error rather than proving the host run.

`tools/freebsd/run_removable_media_local_fallback_host_smoke.py` now:

- accepts the private worker cwd in `run_worker()`;
- creates that cwd exclusively;
- launches the worker with `env={}`;
- runs the worker outside the repository and outside the simulated media tree;
- records `worker_env_policy`, `worker_env_keys_passed`, `worker_cwd_policy`, `worker_cwd_initially_empty`, `worker_cwd_is_private_empty_dir`, and `worker_cwd_contains_media_tree`.

This is implementation-facing boundary cleanup, not a new doctrine surface.

## Evidence refreshed

- `spec/examples/removable.media.capsicum.worker.bridge.json`
- `validation/removable-media-capsicum-worker-bridge.receipt.json`
- `spec/examples/removable.media.local.freebsd.backend.run.receipt.json`
- `validation/removable-media-local-freebsd-backend-run.receipt.json`
- `validation/removable-media-local-freebsd-host-smoke.refusal.json`
- `validation/removable-media-local-freebsd-host-smoke.failure-simulation.json`
- `validation/removable-media-local-freebsd-host-smoke.success-simulation.json`
- `spec/examples/cube.schema.audit.report.json`
- `spec/examples/cube.schema.refactor.backlog.json`
- `spec/examples/cube.hygiene.checkset.manifest.json`
- `spec/examples/cube.hygiene.run.ledger.json`

## Validation summary

The final release-critical hygiene ledger is at:

`session-reviews/DeriveBSD-rev0517-2026.06.05-release-critical-hygiene-ledger.json`

Final result: 34 / 34 release-critical checks passed.

Direct checks run after final ledger/example copy included:

- `python3 -B tools/check_cube_hygiene_run_ledger.py`
- `python3 -B tools/check_generated_artifact_version_ids.py`
- `python3 -B tools/validate_spec_examples.py`
- `python3 -B tools/check_generated_docs.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_bridge.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_backend_run.py`
- `python3 -B tools/check_removable_media_local_fallback_vertical_slice.py`
- `python3 -B tools/check_no_python_bytecode_artifacts.py`

## Remaining risk

This is still not the real FreeBSD host proof. The next real-risk cut should run the host-smoke path on FreeBSD and bind the compiled C worker binary digest, real makefs/mdconfig/fstyp/mount/umount command results, safe-capture digest, fd-5 canary observation, and worker report into the same receipt family.
