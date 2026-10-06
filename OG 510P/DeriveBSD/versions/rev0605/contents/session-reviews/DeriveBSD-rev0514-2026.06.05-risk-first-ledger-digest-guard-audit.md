# DeriveBSD rev0514 risk-first audit: ledger digest guard and fresh release evidence

Cut: 2026-06-05r545
Linked revision target: DeriveBSD-rev0514

## Priority focus

This cut finishes the previously incomplete r545 work and adds one more release-evidence guard before packaging. The highest-risk issue remained evidence self-deception: resumable hygiene ledgers are necessary in this cloudtainer, but they must not become stale proof after checker code changes.

## Substantive change in this package

`tools/check_cube_hygiene_run_ledger.py` now verifies every release-critical ledger row's `tool_sha256` against the current checker file under `tools/`. The ledger writer already records checker digests and the resume path refuses stale rows; this package closes the checker-side gap so a committed/example ledger cannot carry a plausible but stale checker digest.

That is intentionally narrow and implementation-facing: it reduces the chance that a green ledger is just a cached row from older checker code.

## Preserved r545 implementation work

This package also carries the r545 worker-boundary fixes:

- `tools/freebsd/rm_post_detach_capsicum_worker.c` separates startup failure reports before stdio closure from post-stdio reports after stdio closure, with both paths using delegated fd 4 instead of inherited stderr.
- `tools/freebsd/derivebsd_capsicum_probe_shim.h` avoids sentinel-style varargs parsing for the Capsicum compile/execution probe.
- `tools/removable_media_capsicum_worker_bridge.py` and the backend/vertical-slice checks bind the fd-4 error channel and cloudtainer probe limits without claiming real FreeBSD Capsicum execution.
- `tools/hygiene.py` records `tool_sha256` and refuses to resume stale passed rows when profile, command shape, wrapper digest, or checker digest changes.

## Validation evidence

A fresh release-critical ledger was written after the final checker/doc changes, then copied into `spec/examples/cube.hygiene.run.ledger.json`.

Final included ledger:

`session-reviews/DeriveBSD-rev0514-2026.06.05-release-critical-hygiene-ledger.json`

Final status: 32 / 32 release-critical checks passed.

Direct checks after the final ledger/example copy included:

- `python3 -B tools/validate_spec_examples.py`
- `python3 -B tools/check_cube_hygiene_run_ledger.py`
- `python3 -B tools/check_generated_artifact_version_ids.py`
- `python3 -B tools/check_generated_docs.py`
- `python3 -B tools/check_no_python_bytecode_artifacts.py`
- `python3 -B tools/check_no_root_hygiene_log_dumps.py`
- `python3 -B tools/check_frontdoor_budget.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_source.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_bridge.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_backend_run.py`
- `python3 -B tools/check_removable_media_local_fallback_vertical_slice.py`

`check_frontdoor_budget.py` passes, with existing warnings for `docs/00-index.md` and `docs/99-llm-runbook.md` remaining above their original observed baselines. The budget was not raised.

## Remaining highest risk

The real implementation risk is still outside this Linux cloudtainer: compile the C worker on FreeBSD, bind the binary digest, run real `fstyp`, mount a disposable device/image read-only and untrusted, safe-capture the selected file, unmount before worker launch, and exec the worker with only fd 3 and fd 4 while preserving this receipt family.
