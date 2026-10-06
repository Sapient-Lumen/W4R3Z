# DeriveBSD rev0505 session review: risk-first safe capture and FreeBSD backend bridge

Date: 2026-06-04
Cut: 2026-06-04r536

## Priority chosen

The riskiest unfinished removable-media gap was not another registry entry. It was the executable gap between the modeled local fallback and the host-side mechanics that will decide whether hostile removable media can turn into ambient path, symlink, mount, or worker authority.

This cut therefore focused on two concrete hazards:

1. selected-member capture must not rely on path strings, final-component-only symlink checks, or a live mount path after detach;
2. the FreeBSD backend must not inherit a Linux-shaped mount-flag tuple, especially `nodev` as if it were a generic FreeBSD `mount -o` option.

## Substantive changes

- Added shared safe-capture implementation and guard:
  - `tools/removable_media_safe_capture.py`
  - `tools/check_removable_media_safe_capture.py`
  - `validation/removable-media-safe-capture.receipt.json`

  The helper performs a dirfd/openat-style root-pinned walk, rejects traversal, absolute paths, directory subjects, symlink leaves, symlink ancestors, and non-regular subjects, and writes deterministic evidence for the green and red cases.

- Refactored the executable removable-media lane onto that shared helper:
  - `tools/run_removable_media_local_fallback_prototype.py`
  - `tools/removable_media_local_fallback_harness.py`
  - `spec/removable.media.local.fallback.harness.run.schema.json`
  - `spec/examples/removable.media.local.fallback.harness.run.json`
  - `validation/removable-media-local-fallback-harness/expected/`
  - `validation/removable-media-local-fallback-prototype-run.receipt.json`

  The prototype and canonical harness now record `capture.path_capture` evidence before the vertical slice can pass.

- Added and tightened the FreeBSD backend plan bridge:
  - `tools/removable_media_local_freebsd_backend_plan.py`
  - `tools/check_removable_media_local_fallback_freebsd_backend_plan.py`
  - `spec/removable.media.local.freebsd.backend.plan.schema.json`
  - `spec/examples/removable.media.local.freebsd.backend.plan.json`
  - `spec/examples/invalid/removable-media/freebsd-backend-plan/`
  - `docs/current/removable-media-local-fallback-freebsd-backend-plan.md`

  The bridge remains a dry-run host plan in this cloudtainer. It makes the real FreeBSD order explicit: `fstyp`, private read-only mount, safe capture, preserved-CAS commit, `umount`, then fd-only post-detach worker launch.

- Corrected the active FreeBSD mount-hardening tuple:
  - active emitted tuple is now `ro,nosuid,noexec,nosymfollow,untrusted`;
  - `nodev` remains only as an audit finding about the older Linux-shaped overclaim;
  - device-node denial is expressed through devfs/no-raw-device posture, regular-file-only capture, no device/mount path in argv/env, empty worker devfs surface, and preopened fd delivery.

- Tightened the vertical-slice guard:
  - `tools/check_removable_media_local_fallback_vertical_slice.py` now requires the safe-capture receipt, prototype receipt, canonical harness run, and FreeBSD backend plan together.

- Refreshed generated surfaces:
  - `cube.schema.audit.report`
  - `cube.schema.refactor.backlog`
  - `cube.hygiene.checkset.manifest`
  - `cube.hygiene.run.ledger`
  - generated context pack, doc catalog, artifact index, risk register index, and product profile matrix.

## Audit/refactor notes

The capture path is now shared rather than hand-coded separately in the prototype and harness. This removes a concrete drift risk: one path could have rejected symlink leaves while another forgot symlink ancestors or source-stability checks.

The FreeBSD mount audit found and corrected an implementation-shaped mismatch: the project had been carrying a `ro,nodev,nosuid,noexec,nosymfollow` tuple as if it were a generic FreeBSD mount flag floor. The backend plan now models what is actually emitted separately from the security property being achieved.

The front-door budget caught bloat after the new current surfaces were added. I trimmed the README r536 entry rather than raising the budget.

## Validation run directly in this cloudtainer

Focused removable-media checks passed:

- `python3 tools/check_removable_media_safe_capture.py`
- `python3 tools/check_removable_media_local_fallback_freebsd_backend_plan.py`
- `python3 tools/check_removable_media_local_mount_hardening.py`
- `python3 tools/check_removable_media_local_fallback_harness_run.py`
- `python3 tools/check_removable_media_local_fallback_prototype.py`
- `python3 tools/check_removable_media_local_fallback_vertical_slice.py`

Schema/generated/release checks passed:

- `python3 tools/validate_spec_examples.py`
- `python3 tools/lint_spec_schemas.py`
- `python3 tools/check_schema_kind_matches_filename.py`
- `python3 tools/check_generated_docs.py`
- `python3 tools/check_generated_artifact_version_ids.py`
- `python3 tools/check_cube_schema_audit_report.py`
- `python3 tools/check_cube_schema_refactor_backlog.py`
- `python3 tools/check_cube_hygiene_checkset_manifest.py`
- `python3 tools/check_cube_hygiene_run_ledger.py`
- `python3 tools/check_frontdoor_budget.py`
- `python3 tools/check_version.py`
- `python3 tools/check_readme_latest_cut.py`
- `python3 tools/check_release_last_updated.py`
- `python3 tools/check_changelog_index_release_coverage.py`
- `python3 tools/check_hygiene_checkset_completeness.py`
- `python3 tools/check_validation_logs_clean.py`
- `python3 tools/check_spec_example_coverage.py`

I did not mark a full release-critical hygiene wrapper run as complete in this note. In this cloudtainer, long multi-check wrapper invocations were interrupted or killed inconsistently even when the same child checks passed directly. That reinforces the value of the ledger work from rev0503/rev0504, but for this cut I relied on direct check execution plus focused guardrails.

## Remaining risk

The backend plan is still not a real FreeBSD host mount. The next production-grade cut should run the same contract on a FreeBSD machine with at least `msdosfs` and `cd9660` media first, then qualify exFAT only after helper/FUSE semantics and post-mount option verification are proven.
