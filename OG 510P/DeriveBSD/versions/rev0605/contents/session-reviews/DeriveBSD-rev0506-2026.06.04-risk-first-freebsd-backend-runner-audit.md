# DeriveBSD rev0506 risk-first FreeBSD backend runner audit

Last updated: 2026-06-04r537

## Purpose

This cut keeps the removable-media local fallback moving toward a real host backend instead of adding another doctrine/register surface. The riskiest gap after r536 was that the cube had a FreeBSD backend plan and cloudtainer-safe capture evidence, but no executable backend runner artifact binding the plan to an actual sequence: admit, mount-shape, safe capture, detach, and launch the post-detach worker with only delegated descriptors.

## What changed

Added `tools/run_removable_media_local_freebsd_backend.py` as the first executable bridge from the r536 plan to a backend runner. In this cloudtainer, `--mode fixture` creates a private mount-shaped fixture tree from `fixtures/removable-media/local-fallback/exfat-card/`, admits the declared filesystem family, captures `invoice.pdf` through `tools/removable_media_safe_capture.py`, removes the mount-shaped tree before worker launch, and runs the derivative worker using only preopened input/output file descriptors. The canonical receipt is `spec/examples/removable.media.local.freebsd.backend.run.receipt.json`, and the validation copy is `validation/removable-media-local-freebsd-backend-run.receipt.json`.

Added `--mode apply-freebsd` to the same runner, but deliberately as a guarded real-host path. In this Linux cloudtainer it emits an explicit `freebsd-apply-refused` receipt with reason `non-freebsd-host`; it also refuses real mounts unless the host is FreeBSD, the process is root, and the filesystem family is one of the currently base-system-enabled apply families. exFAT remains helper-gated until a real FreeBSD host qualifies the helper and mount semantics.

Added `tools/removable_media_fd_worker.py` and refactored `tools/run_removable_media_local_fallback_prototype.py` plus the new backend runner to use the same fd-only worker launch helper. This removes one more duplicated implementation of the most security-relevant part of the lane: worker delivery after detach.

Added `spec/removable.media.local.freebsd.backend.run.receipt.schema.json`, four negative fixtures under `spec/examples/invalid/removable-media/freebsd-backend-run/`, `tools/check_removable_media_local_fallback_freebsd_backend_run.py`, and `docs/current/removable-media-local-fallback-freebsd-backend-run.md`.

Tightened `tools/check_removable_media_local_fallback_vertical_slice.py` so the removable-media lane now requires all of these layers at once: shared safe capture, fd-only prototype, canonical fixture-backed harness, FreeBSD backend plan, and executable FreeBSD-shaped backend runner receipt.

## Audit/refactor finding corrected during this cut

The first apply-path draft invoked `fstyp` twice: once to bind stdout/stderr digests into the receipt and once to parse stdout. That was wasteful and created an avoidable time-of-check/time-of-use seam. The runner now captures command output once with `_run_command_capture`, stores only digests/byte counts in the receipt, and parses the already-captured stdout bytes for the observed filesystem family.

The release-critical hygiene wrapper still exceeds the practical single-command patience of this cloudtainer, but rev0506 proved the resumable ledger path can complete through repeated resume/row refreshes. The completed release-critical ledger is included at `session-reviews/DeriveBSD-rev0506-2026.06.04-release-critical-hygiene-ledger.json` and copied into `spec/examples/cube.hygiene.run.ledger.json`.

## Online calibration used

- FreeBSD `fstyp(8)` is the right family probe anchor for this path, including base and removable-media-ish filesystems such as ISO-9660, exFAT, FAT, UFS, and NTFS.
- FreeBSD `mount(8)` remains the mount-option source of truth for the active tuple. The active generic tuple remains `ro,nosuid,noexec,nosymfollow,untrusted`; `nodev` is not emitted as a generic FreeBSD mount flag in this lane.
- FreeBSD `openat(2)` / `O_NOFOLLOW` supports the component-by-component no-follow capture shape; the code keeps this abstracted through the shared safe-capture helper in the cloudtainer.
- Capsicum/capability mode remains the right production worker-confinement direction: the cloudtainer runner proves fd-only delivery and no canary leak, while the real FreeBSD runner still needs actual `cap_enter` / Casper-style confinement.

## Validation summary

Passed direct checks after the final edits:

- `python3 tools/check_removable_media_safe_capture.py`
- `python3 tools/check_removable_media_local_fallback_prototype.py`
- `python3 tools/check_removable_media_local_fallback_harness_run.py`
- `python3 tools/check_removable_media_local_fallback_freebsd_backend_plan.py`
- `python3 tools/check_removable_media_local_fallback_freebsd_backend_run.py`
- `python3 tools/check_removable_media_local_fallback_vertical_slice.py`
- `python3 tools/check_removable_media_local_mount_hardening.py`
- `python3 tools/validate_spec_examples.py`
- `python3 tools/lint_spec_schemas.py`
- `python3 tools/check_schema_kind_matches_filename.py`
- `python3 tools/check_spec_example_coverage.py`
- `python3 tools/check_generated_docs.py`
- `python3 tools/check_generated_artifact_version_ids.py`
- `python3 tools/check_cube_hygiene_run_ledger.py`
- `python3 tools/check_cube_schema_audit_report.py`
- `python3 tools/check_cube_schema_refactor_backlog.py`
- `python3 tools/check_cube_hygiene_checkset_manifest.py`
- `python3 tools/check_hygiene_checkset_completeness.py`
- `python3 tools/check_consistency.py`
- `python3 tools/check_release_last_updated.py`
- `python3 tools/check_changelog_artifact_mentions.py`
- `python3 tools/check_validation_logs_clean.py`
- `python3 tools/check_frontdoor_budget.py`
- `python3 tools/check_readme_latest_cut.py`
- `python3 tools/check_version.py`
- `python3 tools/check_text_files_final_newline.py`
- `python3 tools/check_python_tool_executable_bits.py`

CLI smoke evidence:

- `python3 tools/run_removable_media_local_freebsd_backend.py --mode fixture` returned `passed`, digest `sha256:25f0e6a18c6e369d69592bde96f7cd9222edc3a8358e489268e6064e70ef08ec`, no unexpected worker fds, and no canary leak.
- `python3 tools/run_removable_media_local_freebsd_backend.py --mode apply-freebsd` returned exit code `2` in this cloudtainer with `result: refused`, `refusal_reason: non-freebsd-host`, no mount attempt, and no worker launch.

Completed release-critical ledger:

- `session-reviews/DeriveBSD-rev0506-2026.06.04-release-critical-hygiene-ledger.json`: 28 / 28 passed, `run_complete: true`.

## Remaining highest risk

The next cut should run the same backend contract on an actual FreeBSD host. The production lane still needs real `fstyp`, real read-only `mount`, real `umount` before worker launch, device-node closure proof, and closest-available Capsicum/Casper confinement while preserving the exact receipt contract introduced here.

The second remaining risk is front-door bloat. The front-door budget passes, but only because the hard line-count budget was trimmed; bytes still warn for `README.md`, `docs/00-index.md`, and `docs/99-llm-runbook.md`. The next non-removable-media cut should convert more front-door release history into generated/sharded history rather than hand-maintained bulk.
