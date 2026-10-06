# DeriveBSD rev0516 risk-first audit: fd-5 inheritance, input digest, host-smoke failure receipts, and atomic ledger writes

Date: 2026-06-05
Cut: 2026-06-05r548
Linked package target: DeriveBSD-rev0516

## Focus

This cut stayed on the riskiest unfinished lane: removable-media local fallback, specifically the boundary between cloudtainer fixture proof and the first real FreeBSD host proof.

The goal was to make the next FreeBSD host-smoke run harder to fake by accident. In particular, the worker proof now binds both inherited-fd behavior and the exact preserved input object, and host-smoke failures now stay receipt-shaped instead of escaping as tracebacks.

## Substantive changes

- Corrected the fd-5 canary proof. The Capsicum worker bridge execution probe now passes fd 5 into the child with `pass_fds=(3, 4, 5)`, and the C worker records `extra_fd_canary_observed_before_closefrom` before closing the delegated-set tail. This prevents a parent-only canary from masquerading as inherited-fd proof.
- Added worker input digest proof. The C worker computes `input_sha256` over delegated fd 3, the bridge execution probe verifies that digest against known fixture bytes, and the host-smoke runner requires the worker-reported digest to match the preserved CAS capture digest before a real host run can pass.
- Hardened host-smoke failure paths. The FreeBSD host-smoke runner now returns receipt-shaped JSON for host command, mount, capture, cleanup, and worker-launch failures. The checker-only mount-failure simulation proves cleanup evidence and no worker launch after a pre-worker host failure.
- Fixed release-evidence durability. `tools/hygiene.py` now writes ledgers through a unique same-directory temporary file, fsyncs the temp file before replace, and fsyncs the containing directory. `tools/check_cube_hygiene_run_ledger.py` now checks for this durable write shape.

## Audit/refactor result

The useful refactor was in evidence boundaries rather than registries:

- fd-5 proof moved from “a parent canary exists” to “the child actually inherited fd 5 and closed it before capability entry.”
- fd-count proof was supplemented with content proof: the worker must report the digest of the actual preserved object it processed.
- host-smoke failures now preserve structured receipt evidence, including no-worker-launch proof, so failure transcripts are useful during the first real FreeBSD host run.
- resumable hygiene evidence now has a safer atomic write path for chunked cloudtainer runs.

## Validation

A fresh release-critical hygiene ledger completed successfully:

- `session-reviews/DeriveBSD-rev0516-2026.06.05-release-critical-hygiene-ledger.json`
- Final status: 33 / 33 release-critical checks passed.

The completed ledger was copied into:

- `spec/examples/cube.hygiene.run.ledger.json`

Direct post-ledger checks passed, including:

- `python3 -B tools/check_cube_hygiene_run_ledger.py`
- `python3 -B tools/check_generated_artifact_version_ids.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_source.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_bridge.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_backend_run.py`
- `python3 -B tools/check_removable_media_local_fallback_vertical_slice.py`
- `python3 -B tools/check_generated_docs.py`
- `python3 -B tools/validate_spec_examples.py`
- `python3 -B tools/lint_spec_schemas.py`
- `python3 -B tools/check_consistency.py`
- `python3 -B tools/check_frontdoor_budget.py`
- `python3 -B tools/check_no_python_bytecode_artifacts.py`

`validate_spec_examples.py` validated 467 examples. `check_frontdoor_budget.py` passed with the existing warnings for `docs/00-index.md` and `docs/99-llm-runbook.md` byte growth; the budget was not raised.

## Remaining highest risk

This still is not the real FreeBSD host proof. The next substantive cut should run the host-smoke path on FreeBSD: compile the C worker, bind the binary digest, create/attach a disposable image, perform real read-only/untrusted mount and real unmount/detach, run the worker with fd 3/fd 4 plus the fd-5 non-media canary, and preserve the same receipt contract.
