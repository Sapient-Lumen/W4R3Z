# DeriveBSD rev0516 risk-first host-smoke failure receipts audit

Latest cut: 2026-06-05r548

## Focus

This cut continued the removable-media local fallback work because the first real FreeBSD host proof remains the riskiest unfinished lane. The target was not another registry surface; it was the FreeBSD host-smoke runner's behavior when host work fails.

## Main correction

`tools/freebsd/run_removable_media_local_fallback_host_smoke.py` no longer lets host command, mount, capture, cleanup, or worker-launch failures escape as Python tracebacks. The runner now emits failed `removable.media.local.freebsd.host.smoke.receipt` JSON with:

- `failure.stage` and a failure message;
- `receipt_shaped_instead_of_traceback = true`;
- host command evidence up to the failure;
- cleanup command evidence after attach or mount;
- explicit `worker_launched = false` for pre-worker failures;
- simulation markers when checker-only host command injection is used in the cloudtainer.

The checker now writes:

`validation/removable-media-local-freebsd-host-smoke.failure-simulation.json`

That fixture injects a mount failure after `mdconfig` attach and proves that cleanup evidence is recorded and the worker is not launched.

## Audit/refactor detail

The host-smoke worker launcher now saves and restores any pre-existing parent fd slots 3, 4, and 5 around the `pass_fds=(3, 4, 5)` worker launch. This prevents the smoke runner from proving a narrow child boundary while accidentally damaging the broker process's own descriptor state.

The runner also refuses a caller-provided `--work-dir` that already exists with `work-dir-must-not-already-exist`; it does not recursively delete caller paths.

## Preserved r548 worker-boundary evidence

This package also carries the r548 fd-5/input-digest bridge corrections:

- the bridge execution probe actually passes fd 5 into the child;
- the C worker records that the canary was observed before `closefrom`;
- the worker computes and reports `input_sha256` over fd 3;
- the host-smoke path requires the worker-observed digest to match the preserved CAS capture digest.

## Validation

Release-critical hygiene ledger:

`session-reviews/DeriveBSD-rev0516-2026.06.05-release-critical-hygiene-ledger.json`

Final status: 33 / 33 checks passed.

Additional direct checks after copying the completed ledger into `spec/examples/cube.hygiene.run.ledger.json` and regenerating generated docs:

- `python3 -B tools/check_cube_hygiene_run_ledger.py`
- `python3 -B tools/check_generated_artifact_version_ids.py`
- `python3 -B tools/validate_spec_examples.py`
- `python3 -B tools/check_generated_docs.py`
- `python3 -B tools/check_frontdoor_budget.py`
- `python3 -B tools/check_validation_logs_clean.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_bridge.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_backend_run.py`
- `python3 -B tools/check_removable_media_local_fallback_vertical_slice.py`

`check_frontdoor_budget.py` still warns that `docs/00-index.md` and `docs/99-llm-runbook.md` remain larger than their original observed byte baselines. I trimmed `docs/00-index.md` line count back under budget rather than raising the ratchet.

## Remaining risk

The next risk-first step is still the real FreeBSD host transcript: run the host-smoke path on FreeBSD, bind the compiled C worker binary digest, use a disposable image/device, perform real read-only/untrusted mount and real unmount/detach, and preserve the same receipt family while proving fd 3/fd 4 delivery and fd-5 closure.
