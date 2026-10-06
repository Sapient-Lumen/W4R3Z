# DeriveBSD rev0513 risk-first audit: startup fd-4 reports and stale resume guard

Cut: 2026-06-05r545
Linked revision target: DeriveBSD-rev0513

## Priority focus

This cut continued the removable-media local fallback lane, but the highest-risk finding during packaging was in validation evidence rather than the media worker itself: resumable hygiene evidence could keep an old green row after a checker changed. That made the release ledger vulnerable to stale proof, especially in this cloudtainer where long runs are accumulated in chunks.

## Substantive changes

- Hardened the FreeBSD Capsicum worker startup/error boundary in `tools/freebsd/rm_post_detach_capsicum_worker.c`.
  - Startup/path-argument rejection is reported through delegated fd 4 before stdio closure.
  - Post-stdio failures remain reported through delegated fd 4 after stdio closure.
  - The worker no longer relies on `err()`/`errx()` stderr paths for expected validation failures.
- Hardened the cloudtainer Capsicum probe shim in `tools/freebsd/derivebsd_capsicum_probe_shim.h`.
  - The shim no longer uses a sentinel-style varargs parser for `cap_rights_init()`.
  - The bridge execution probe remains a syntax/contract probe only, not a Linux claim about FreeBSD Capsicum execution.
- Hardened resumable hygiene evidence in `tools/hygiene.py`.
  - Each row records `tool_sha256`.
  - The ledger also records `hygiene_wrapper_sha256`, so resume cannot silently reuse rows from a stale wrapper implementation.
  - Resume refuses to reuse a passed row if the selected profile, command shape, checker digest, or wrapper digest no longer matches.
  - `spec/cube.hygiene.run.ledger.schema.json` and `tools/check_cube_hygiene_run_ledger.py` validate the new binding.
  - During final validation, `tools/check_cube_hygiene_run_ledger.py` itself exposed a missing `json` import in its resume-regression test; that checker drift was fixed and re-run.
- Trimmed front-door bulk in `README.md` rather than raising the front-door byte budget.

## Audit result

The key correction is that validation evidence is now less self-deceptive. A partial release-critical ledger can still be resumed, but a changed checker source invalidates the old row. That directly addresses the failure mode found while packaging this cut.

The remaining limitation is that row reuse is still keyed to checker identity and command shape, not a full dependency graph for every file read by a checker. For this cut, final ledger/example replacement was followed by direct `check_cube_hygiene_run_ledger.py`, `check_generated_artifact_version_ids.py`, and generated-doc checks.

## Final validation

A completed release-critical ledger is included at:

`session-reviews/DeriveBSD-rev0513-2026.06.05-release-critical-hygiene-ledger.json`

Final ledger status: 32 / 32 release-critical checks passed.

Important direct checks after final ledger/example copy:

- `python3 -B tools/check_cube_hygiene_run_ledger.py`
- `python3 -B tools/check_generated_artifact_version_ids.py`
- `python3 -B tools/check_generated_docs.py`
- `python3 -B tools/check_no_python_bytecode_artifacts.py`
- `python3 -B tools/check_no_root_hygiene_log_dumps.py`
- `python3 -B tools/check_frontdoor_budget.py`
- `python3 -B tools/check_readme_latest_cut.py`
- `python3 -B tools/check_version.py`
- `python3 -B tools/check_changelog_artifact_mentions.py`
- `python3 -B tools/validate_spec_examples.py`

## Next highest risk

The real implementation boundary is still the FreeBSD host proof: compile the C worker on FreeBSD, bind the binary digest, mount a disposable device/image read-only and untrusted, safe-capture the selected file, unmount before worker launch, and exec the worker with only fd 3 and fd 4 while preserving the same receipt family.
