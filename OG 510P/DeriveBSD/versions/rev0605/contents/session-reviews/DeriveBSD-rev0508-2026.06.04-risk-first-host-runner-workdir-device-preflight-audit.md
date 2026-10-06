# DeriveBSD rev0508 risk-first host-runner workdir/device-preflight audit

This cut continues the removable-media local-fallback backend work and intentionally avoids adding a new registry/doctrine surface.

## Main risk targeted

The highest-risk unfinished lane is still the real FreeBSD removable-media backend. The r537/r538 runner made the path executable, but it still carried two fixture-shaped hazards that should not reach a rooted host runner:

1. `--work-dir` was treated as something the tool could recursively delete before use.
2. the apply path had insufficiently explicit device-node admission before `fstyp`/`mount`.

Both are dangerous in a host runner. A user-supplied work directory is not scratch unless the tool creates an owned child beneath it. A device path is not safe merely because it is a string under `/dev`; the apply path needs clean path-shape validation everywhere, and real host validation must lstat the exact node and reject symlinks or non-character-device nodes before probing or mounting.

## Implementation changes

Changed `tools/run_removable_media_local_freebsd_backend.py`:

- removed destructive CLI cleanup of user-supplied `--work-dir`;
- added `WORK_ROOT_POLICY = private-temp-or-create-exclusive-child-under-user-base-no-rmtree`;
- added `_prepare_user_work_root()` so a user work base survives and an exclusive private child is created instead;
- added `_shape_validation_error()` and tightened the apply path so invalid `/dev` path shape becomes a structured refusal before host work;
- changed `_validate_device_node_for_apply()` to use `os.lstat()` and reject symlink and non-character-device nodes before real `fstyp`/`mount`;
- added command-result evidence slots for the future real FreeBSD `mount` and `umount` path;
- kept fixture-mode `mount.command_result` and `detach.umount_result` null so cloudtainer fixture runs cannot impersonate host command evidence.

Changed `tools/removable_media_local_freebsd_backend_plan.py`:

- replaced the broad `/dev/[A-Za-z0-9._/-]+` check with component-wise validation;
- rejected empty components, `.`, `..`, and unsafe component characters without normalizing the path into something else.

Changed `spec/removable.media.local.freebsd.backend.run.receipt.schema.json`:

- added a `workspace` block with the no-rmtree runtime work-root policy;
- added `preflight.device_node_validation_method` and `preflight.device_node_error_detail`;
- added `mount.command_result` and `detach.umount_result` slots.

Changed `tools/check_removable_media_local_fallback_freebsd_backend_run.py`:

- exercises the non-FreeBSD apply refusal through the real `build_apply_receipt()` path rather than only the raw refusal builder;
- proves invalid device-node shape is a structured refusal with no mount and no worker launch;
- directly checks accepted/rejected device-node path shapes;
- directly checks lstat behavior on `/dev/null`, and on `/dev/fd` when present as a symlink;
- runs the CLI with a user work base and proves a sentinel file survives;
- checks the source no longer contains the old `shutil.rmtree(work_dir)` cleanup pattern.

Changed `tools/check_removable_media_local_fallback_vertical_slice.py` so the vertical slice now requires:

- no-rmtree work-root policy;
- explicit device-node validation scope;
- null fixture-mode mount/umount command evidence;
- all prior no-overwrite CAS, detach-before-worker, and fd-only worker proofs.

## Continuation hardening before packaging

Before shipping the linked rev0508 zip, this worktree received two additional implementation-facing risk reducers:

- Added `tools/freebsd/rm_post_detach_capsicum_worker.c`, a FreeBSD-only post-detach fd worker scaffold. It accepts no path/device argv, keeps input on fd 3 and output on fd 4, closes fds above the delegated set, limits the delegated fd rights with Capsicum, enters `cap_enter()`, and writes only through the output fd. `tools/check_removable_media_local_fallback_capsicum_worker_source.py` statically guards that source until a real FreeBSD host can compile and run it.
- Removed the stale root `hygiene_r*.log` / `check_run.log` / `checks_tail.log` dumps and added `tools/check_no_root_hygiene_log_dumps.py` to keep future linked zips from carrying obsolete scrollback now that durable evidence lives under `session-reviews/*.json` and validation artifacts.

The vertical-slice checker now also requires the Capsicum-shaped fd-worker source tokens in addition to the backend runner receipt.

## Refreshed artifacts

Refreshed for `2026-06-04r539`:

- `spec/examples/removable.media.local.freebsd.backend.run.receipt.json`
- `validation/removable-media-local-freebsd-backend-run.receipt.json`
- `spec/examples/cube.schema.audit.report.json`
- `spec/examples/cube.schema.refactor.backlog.json`
- `spec/examples/cube.hygiene.checkset.manifest.json`
- `spec/examples/cube.hygiene.run.ledger.json`
- generated docs: `docs/412-product-profile-matrix.md`, `docs/414-doc-catalog.md`, `docs/415-risk-register-index.md`, `docs/418-artifact-index.md`, `docs/420-context-pack.md`, plus generated JSON companions where applicable.

## Validation evidence

A completed release-critical hygiene ledger is included at:

`session-reviews/DeriveBSD-rev0508-2026.06.04-release-critical-hygiene-ledger.json`

Final ledger result: 29 / 29 release-critical checks passed.

Important direct checks also passed:

- `python3 tools/check_removable_media_local_fallback_freebsd_backend_run.py`
- `python3 tools/check_removable_media_local_fallback_vertical_slice.py`
- `python3 tools/check_removable_media_local_fallback_capsicum_worker_source.py`
- `python3 tools/check_no_root_hygiene_log_dumps.py`
- `python3 tools/check_removable_media_safe_capture.py`
- `python3 tools/check_removable_media_local_fallback_freebsd_backend_plan.py`
- `python3 tools/lint_spec_schemas.py`
- `python3 tools/validate_spec_examples.py`
- `python3 tools/check_schema_kind_matches_filename.py`
- `python3 tools/check_spec_example_coverage.py`
- `python3 tools/check_consistency.py`
- `python3 tools/check_generated_docs.py`
- `python3 tools/check_generated_artifact_version_ids.py`
- `python3 tools/check_cube_hygiene_run_ledger.py`
- `python3 tools/check_cube_hygiene_checkset_manifest.py`
- `python3 tools/check_cube_schema_audit_report.py`
- `python3 tools/check_cube_schema_refactor_backlog.py`
- `python3 tools/check_frontdoor_budget.py`
- `python3 tools/check_version.py`
- `python3 tools/check_readme_latest_cut.py`
- `python3 tools/check_release_last_updated.py`
- `python3 tools/check_changelog_artifact_mentions.py`
- `python3 tools/check_validation_logs_clean.py`
- `python3 tools/check_text_files_final_newline.py`

`tools/check_frontdoor_budget.py` passes but still warns that the front-door files are larger than the original observed baseline. README stayed under the existing hard budget after trimming the r539 front-door entry.

## Remaining risk

This is still not a production FreeBSD host run. The next truly substantive step is to run the same receipt contract on a FreeBSD host with a disposable block device/image: real `fstyp`, real read-only/untrusted mount, safe capture, real `umount`, and post-detach fd-only worker launch. The next cloudtainer cut can prepare that by adding a host-run transcript fixture format and a replay checker, but it should not pretend that a Linux cloudtainer has qualified FreeBSD mount semantics.

The second risk remains front-door growth. This cut kept README under budget by trimming, but `docs/00-index.md` and `docs/99-llm-runbook.md` still warn on growth. A future cut should start extracting old release-note sediment from the hand-maintained front door.
