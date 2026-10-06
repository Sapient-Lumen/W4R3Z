# DeriveBSD rev0504 risk-first executable fallback audit

This cut deliberately spent the session budget on the riskiest gap left after r533/r534: the removable-media local fallback had many receipts, schemas, and post-detach guardrails, but too little executable proof that bytes can move through the lane without preserving ambient media authority.

## Priority changes

- Added `tools/removable_media_local_fallback_harness.py` and `tools/check_removable_media_local_fallback_harness_run.py` as a canonical fixture-backed harness. It uses checked-in fixture bytes at `fixtures/removable-media/local-fallback/exfat-card/invoice.pdf`, verifies that those bytes match the existing content-import plan/receipt, writes a digest-addressed preserved capture, writes a metadata-only derivative summary, and emits `removable.media.local.fallback.harness.run` evidence.
- Added `spec/removable.media.local.fallback.harness.run.schema.json`, `spec/examples/removable.media.local.fallback.harness.run.json`, `spec/examples/invalid/removable-media/local-fallback-harness/ambient-ingest-visible.json`, and expected evidence under `validation/removable-media-local-fallback-harness/expected/`.
- Added `tools/run_removable_media_local_fallback_prototype.py`, `tools/check_removable_media_local_fallback_prototype.py`, and `validation/removable-media-local-fallback-prototype-run.receipt.json`. This no-root cloudtainer prototype captures a regular file into a digest-addressed CAS object, deletes the simulated source media tree before the worker starts, and feeds the worker by preopened file descriptors only.
- Tightened `tools/check_removable_media_local_fallback_vertical_slice.py` so the vertical slice cannot pass on schema/prose coherence alone. It now requires both the fixture-backed harness and the raw fd-only prototype evidence.
- Extended `tools/hygiene.py` ledger mode with `checks_total`, `checks_completed`, `run_complete`, `failure_class`, `terminated_by_signal`, `signal_name`, and `--resume-ledger`. Partial interrupted ledgers now remain failed/incomplete until the selected profile finishes; negative return codes are visibly signal termination rather than ordinary assertion failure.

## Audit/refactor performed

The audit target was the removable-media first lane and the hygiene evidence path. The main design correction was changing the lane from “many modeled receipts that agree” to “modeled receipts plus a replayable byte-moving harness.” The implementation also removed a waste pattern in interrupted hygiene runs: a release-critical run no longer restarts from zero after terminal/cloudtainer interruption, and it no longer risks presenting a partial all-green prefix as a complete release run.

The harness path gate was hardened during review. It rejects path traversal, absolute paths, directory subjects, unknown filesystem-family claims, and symlink components in any selected path ancestor, not only a symlink leaf.

## Remaining limitations

This is still not the production FreeBSD backend. The cloudtainer cannot exercise real device attach, kernel mount flags, devfs rules, jails, Capsicum/Casper, pf, or hardware detach events. The value of this cut is that the cube now has a concrete executable spine for byte capture, preservation, detach-before-worker ordering, and post-detach fd-only delivery. The next implementation risk is to replace the simulated fixture/media roots with a FreeBSD-specific mount/jail/Capsicum adapter while keeping the same receipt/evidence expectations.

## Validation evidence

The release-critical hygiene ledger completed after resume:

- `session-reviews/DeriveBSD-rev0504-2026.06.04-release-critical-hygiene-ledger.json`: 28 / 28 checks passed, `run_complete: true`.
- `session-reviews/DeriveBSD-rev0504-2026.06.04-schema-cube-audit-hygiene-ledger.json`: 3 / 3 checks passed, `run_complete: true`.

Additional direct checks run during the cut included:

- `python3 tools/check_removable_media_local_fallback_harness_run.py`
- `python3 tools/check_removable_media_local_fallback_prototype.py`
- `python3 tools/check_removable_media_local_fallback_vertical_slice.py`
- `python3 tools/check_cube_hygiene_run_ledger.py`
- `python3 tools/check_generated_artifact_version_ids.py`
- `python3 tools/check_generated_docs.py`
- `python3 tools/validate_spec_examples.py`
- `python3 tools/lint_spec_schemas.py`
- `python3 tools/check_consistency.py`

## Recommended next cut

Move the harness toward a FreeBSD adapter without changing the evidence contract: mount read-only with hardened flags, capture one selected regular file with no-follow/openat-style discipline, detach/unmount before worker launch, launch under the constrained post-detach envelope, and replay the same negative corpus against real filesystem subjects.
