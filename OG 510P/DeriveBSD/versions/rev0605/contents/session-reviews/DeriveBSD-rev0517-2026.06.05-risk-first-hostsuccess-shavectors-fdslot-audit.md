# DeriveBSD rev0517 risk-first host-smoke success and digest-vector audit

## Scope

This session continued the removable-media local fallback lane, because it remains the highest-risk implementation path before real FreeBSD host proof.  The work stayed implementation-facing: host-smoke orchestration, fd-slot restoration, worker launch envelope, and C-worker digest execution coverage.

## Corrections made

The main audit finding was that the FreeBSD host-smoke checker had drifted into a self-contradictory state: it contained duplicate success-simulation/check functions, and the later duplicate shadowed the richer simulation.  That made the checker fail and made it possible for a weaker success-path proof to hide the intended safe-capture/worker-digest assertions.  The duplicate definitions were removed and the surviving simulation now checks the full happy path without claiming real FreeBSD execution.

A second implementation gap was the C worker `input_sha256` path.  The bridge already checked one short fd-3 input, but host-smoke depends on that digest as a core identity proof.  A one-string digest smoke test is not enough for an embedded SHA-256 implementation.  Added `tools/check_removable_media_local_fallback_capsicum_worker_sha256_vectors.py`, which compiles the same probe-shim worker and runs empty, padding-boundary, block-boundary, and multi-block fd-3 vectors through the worker, checking each reported `input_sha256` against Python `hashlib`.

## Substantive files touched

- `tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py`
- `tools/freebsd/run_removable_media_local_fallback_host_smoke.py`
- `tools/check_removable_media_local_fallback_capsicum_worker_sha256_vectors.py`
- `validation/removable-media-capsicum-worker-sha256-vectors.json`
- `validation/removable-media-local-freebsd-host-smoke.success-simulation.json`
- `tools/hygiene.py`
- `tools/check_cube_hygiene_checkset_manifest.py`
- `spec/examples/cube.hygiene.checkset.manifest.json`
- `spec/examples/cube.hygiene.run.ledger.json`
- current removable-media docs and generated catalog/context/index surfaces

## Validation evidence

A fresh release-critical hygiene ledger is included at:

`session-reviews/DeriveBSD-rev0517-2026.06.05-release-critical-hygiene-ledger.json`

Final status: 34 / 34 release-critical checks passed.

The completed ledger was copied to:

`spec/examples/cube.hygiene.run.ledger.json`

Direct checks after the final ledger copy included:

- `python3 -B tools/check_cube_hygiene_run_ledger.py`
- `python3 -B tools/check_generated_artifact_version_ids.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_sha256_vectors.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_bridge.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_backend_run.py`
- `python3 -B tools/check_removable_media_local_fallback_vertical_slice.py`
- `python3 -B tools/validate_spec_examples.py`
- `python3 -B tools/lint_spec_schemas.py`
- `python3 -B tools/check_generated_docs.py`
- `python3 -B tools/check_frontdoor_budget.py`
- `python3 -B tools/check_no_python_bytecode_artifacts.py`

## Remaining risk

This still does not replace the real FreeBSD host proof.  The next risk-first step remains running `tools/freebsd/run_removable_media_local_fallback_host_smoke.py` on FreeBSD with root and an explicit `--run-host-smoke`, then preserving the real transcript: compiled C worker binary digest, makefs image creation, mdconfig read-only attach, fstyp, hardened mount, safe capture, real umount/detach, and fd-3/fd-4/fd-5 worker launch evidence.
