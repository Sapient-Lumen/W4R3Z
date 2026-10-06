# DeriveBSD rev0516 risk-first host-smoke failure evidence audit

Cut: 2026-06-05r548

## Focus

The highest-risk unfinished lane remains removable-media local fallback on a real FreeBSD host. The previous cut added a guarded host-smoke runner, but the audit found a brittle host-proof failure mode: real host command failures could still escape as Python exceptions unless every phase is converted into receipt-shaped evidence.

## Changes

- Hardened `tools/freebsd/run_removable_media_local_fallback_host_smoke.py` so host command, mount, safe-capture, cleanup, and worker-launch failures return structured receipts rather than tracebacks.
- Added checker-only mount-failure simulation in `tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py`.
- Added durable simulated failure evidence at `validation/removable-media-local-freebsd-host-smoke.failure-simulation.json`.
- Bound failure evidence to: failure stage, no worker launch after pre-worker host failure, mdconfig detach cleanup after attach, cleanup commands, and a no-real-FreeBSD-claim marker.
- Refreshed the Capsicum bridge/backend receipt schemas for the fd-5 observation-before-closefrom and worker `input_sha256` proof fields that were emitted by the bridge but not yet admitted by the schemas.
- Refreshed r548 bridge/backend/host-smoke/cube-generated evidence surfaces and completed a fresh release-critical hygiene ledger.

## Audit finding corrected

A host-smoke runner that only emits proof on the happy path is unsafe. The first real FreeBSD run is likely to fail somewhere mundane: compile flags, mdconfig behavior, mount option support, makefs image layout, safe-capture path, umount, or worker exec. That failure must still be evidence, or the next session will only have scrollback and guesswork.

This cut makes failure evidence explicit and replayed by a checker-only simulation without pretending that the Linux cloudtainer executed FreeBSD host work.

## Validation

Completed release-critical hygiene ledger:

`session-reviews/DeriveBSD-rev0516-2026.06.05-release-critical-hygiene-ledger.json`

Status: 33 / 33 checks passed.

Additional direct checks run after copying the completed ledger into `spec/examples/cube.hygiene.run.ledger.json`:

- `python3 -B tools/check_cube_hygiene_run_ledger.py`
- `python3 -B tools/check_generated_artifact_version_ids.py`
- `python3 -B tools/check_generated_docs.py`
- `python3 -B tools/validate_spec_examples.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_bridge.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_backend_run.py`
- `python3 -B tools/check_removable_media_local_fallback_vertical_slice.py`
- `python3 -B tools/check_frontdoor_budget.py`
- `python3 -B tools/check_no_python_bytecode_artifacts.py`
- `python3 -B tools/check_no_root_hygiene_log_dumps.py`

## Remaining risk

This is still not the real FreeBSD host transcript. The next high-value cut should run, or prepare more tightly for running, the host-smoke runner on FreeBSD and capture a real passed or failed host receipt with command-result evidence.
