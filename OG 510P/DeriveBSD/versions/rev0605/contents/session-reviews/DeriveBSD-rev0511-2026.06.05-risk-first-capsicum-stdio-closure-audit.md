# DeriveBSD rev0511 risk-first audit: Capsicum worker stdio closure

This cut continues the removable-media local fallback work because it is still the highest-risk unfinished implementation lane.  The goal was not to add another registry surface; it was to reduce a concrete authority leak that could survive the receipt story.

## Risk found

The r541 bridge correctly distinguished the cloudtainer Python fixture worker from the future FreeBSD Capsicum C worker, but the C worker still preserved fd 0/1/2 as ordinary stdio.  The surrounding prose often said the production worker had only fd 3 and fd 4 as data-plane authority.  That was not quite true: a bad real launcher could accidentally leave source-media authority on stdin/stdout/stderr while all receipts focused on fd 3 and fd 4.

This is the same class of problem as the earlier source-media fd canary issue: a proof can look closed-world while a parent/launcher descriptor quietly keeps authority alive.

## Changes made

- `tools/freebsd/rm_post_detach_capsicum_worker.c` now calls `close_standard_fds()` before `cap_enter()`.
- The worker report gained `stdio_fds_closed_before_cap_enter = true`.
- `tools/removable_media_capsicum_worker_bridge.py` now emits `source.stdio_policy = close-fd-0-1-2-before-cap-enter` and `launch_contract.worker_must_close_stdio_fds_before_cap_enter = true`.
- The backend run receipt's `worker_bridge` binding carries `production_stdio_policy = close-fd-0-1-2-before-cap-enter`.
- `tools/check_removable_media_local_fallback_capsicum_worker_source.py`, `tools/check_removable_media_local_fallback_capsicum_worker_bridge.py`, and `tools/check_removable_media_local_fallback_vertical_slice.py` now guard the stdio closure policy.
- `docs/current/removable-media-capsicum-worker-bridge.md` and `docs/current/removable-media-local-fallback-freebsd-backend-run.md` now correct the ordering claim: stdio closes before capability mode; delegated fd 3/fd 4 regular-file validation happens after capability mode entry in the current C worker.

## Audit/refactor result

The useful refactor is small: the production stdio policy is now generated once by the bridge and consumed by the backend binding, instead of living only as prose.  This prevents the FreeBSD host path from later growing a launcher that treats stdio as harmless ambient plumbing.

The front-door budget was not raised.  README and runbook wording were trimmed while adding the r542 note.  `docs/00-index.md` remained exactly at its line budget after pruning blank-line growth.

## Validation summary

Release-critical hygiene ledger:

- `session-reviews/DeriveBSD-rev0511-2026.06.05-release-critical-hygiene-ledger.json`
- final status: 32 / 32 checks passed
- copied into `spec/examples/cube.hygiene.run.ledger.json`

Direct checks run after the final edits included:

- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_build.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_source.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_bridge.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_backend_run.py`
- `python3 -B tools/check_removable_media_local_fallback_vertical_slice.py`
- `python3 -B tools/check_cube_hygiene_run_ledger.py`
- `python3 -B tools/check_cube_hygiene_checkset_manifest.py`
- `python3 -B tools/check_cube_schema_audit_report.py`
- `python3 -B tools/check_cube_schema_refactor_backlog.py`
- `python3 -B tools/check_generated_docs.py`
- `python3 -B tools/check_generated_artifact_version_ids.py`
- `python3 -B tools/check_frontdoor_budget.py`
- `python3 -B tools/check_version.py`
- `python3 -B tools/check_readme_latest_cut.py`
- `python3 -B tools/check_validation_logs_clean.py`
- `python3 -B tools/check_no_python_bytecode_artifacts.py`
- `python3 -B tools/validate_spec_examples.py`
- `python3 -B tools/lint_spec_schemas.py`

## Remaining risk

This is still not a real FreeBSD host proof.  The next substantive cut should compile the C worker on FreeBSD, bind the binary digest, launch it with fd 3 and fd 4 only after a real unmount, and record the first true host transcript for `fstyp`, read-only/untrusted mount, safe capture, `umount`, and Capsicum worker execution.
