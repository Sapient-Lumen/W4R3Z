# DeriveBSD rev0520 risk-first fixture-copy host-smoke audit

Date: 2026-06-05
Revision: 2026-06-05r552
Linked package target: DeriveBSD-rev0520-2026.06.05.*-fixturecopy-hostsmokegate-sourceguard-*.zip

## Focus

This cut continued the removable-media local fallback lane, with attention on the first real FreeBSD host-smoke proof. The highest-risk remaining boundary is no longer only fd delegation or post-detach worker confinement; it is also the source tree that becomes the disposable mounted media image.

A host-smoke runner that accepts an arbitrary fixture root can accidentally turn caller-controlled local state into a trusted media image before the runner has admitted that tree. This is a self-deception risk: a later transcript could prove mount/detach/fd boundaries while hiding that the image source itself was uncontrolled.

## Substantive changes

`tools/freebsd/run_removable_media_local_fallback_host_smoke.py` now admits the fixture root before any host command. The admitted fixture root must resolve under `fixtures/removable-media/local-fallback`, avoid symlink components and symlink entries, avoid special-file entries, stay within fixed file-count and byte budgets, and contain a regular selected `invoice.pdf` member.

The runner also performs a source-stable fixture-copy check. It computes a deterministic manifest of the admitted source, copies the fixture tree without following symlink authority, recomputes the source manifest, computes the copied-tree manifest, and fails closed at `fixture-root-copy` if the source changed during copy or the copy diverged from the admitted manifest.

The host-smoke receipts now record fixture admission and copy evidence, including `fixture_root_admitted_before_host_commands`, `fixture_root_has_no_symlink_or_special_entries`, `fixture_source_stable_during_copy`, and `fixture_copy_matches_source_manifest`.

## Negative evidence added

`tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py` now writes and checks:

- `validation/removable-media-local-freebsd-host-smoke.fixture-admission-failure-simulation.json`
- `validation/removable-media-local-freebsd-host-smoke.fixture-copy-change-simulation.json`

The first proves that an outside fixture root fails at `fixture-root-admission` before any host command. The second simulates a source mutation during fixture copy and proves that the runner fails at `fixture-root-copy`, records cleanup/no-host-command invariants, and does not proceed to `cc`, `makefs`, `mdconfig`, `fstyp`, `mount`, capture, or worker launch.

## Audit/refactor result

The useful refactor is narrow and implementation-facing: fixture root admission and fixture copy verification are now a shared, explicit step in the host-smoke runner rather than an implicit `copytree` side effect. Durable receipts no longer prove only the worker/device side of the lane; they also bind the source tree used to construct the disposable media image.

## Validation

The release-critical hygiene ledger completed successfully at:

`session-reviews/DeriveBSD-rev0520-2026.06.05-release-critical-hygiene-ledger.json`

Final status: 35 / 35 release-critical checks passed.

Additional direct checks after the final ledger copy included:

- `python3 -B tools/validate_spec_examples.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py`
- `python3 -B tools/check_removable_media_local_fallback_vertical_slice.py`
- `python3 -B tools/check_cube_hygiene_run_ledger.py`
- `python3 -B tools/check_generated_artifact_version_ids.py`
- `python3 -B tools/check_generated_docs.py`
- `python3 -B tools/check_frontdoor_budget.py`
- `python3 -B tools/check_validation_logs_clean.py`
- `python3 -B tools/check_no_python_bytecode_artifacts.py`

`validate_spec_examples.py` validated 467 examples.

## Remaining highest risk

The remaining highest-risk step is still real FreeBSD host proof: run the host-smoke path on FreeBSD, compile the C worker, bind the binary digest, create/attach a disposable image from an admitted fixture root, perform real read-only/untrusted mount and real unmount/detach, run the worker with fd 3/fd 4/fd 5, and preserve the same receipt contract.
