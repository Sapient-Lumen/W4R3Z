# DeriveBSD rev0517 risk-first audit: worker launch envelope, fd-slot guard, and host-smoke success simulation

Date: 2026-06-05
Cut: 2026-06-05r549
Linked package target: DeriveBSD-rev0517

## Focus

This cut stayed on the removable-media local fallback lane because it remains the riskiest unfinished implementation path.  The concrete target was the last easy-to-miss authority channel before the first real FreeBSD host proof: the worker was becoming fd-disciplined, but the launch envelope still risked inheriting parent environment, cwd, and fixed fd-slot confusion.

## Substantive changes

- Hardened the Capsicum worker bridge probe and FreeBSD host-smoke runner so the worker launches with an empty environment and a private non-media cwd.  The bridge/backend/host-smoke evidence now records `worker_env_policy = empty-environment` and `worker_cwd_policy = private-empty-directory-not-media-not-repo` instead of relying on subprocess defaults.
- Added and bound the fd-slot launcher policy `save-and-clear-target-fds-before-opening-delegated-files`, so parent fd slots 3/4/5 are saved and cleared before delegated files are opened, then restored after the child exits.
- Extended the host-smoke checker with a success simulation that exercises the intended command order (`cc -> makefs -> mdconfig -> fstyp -> mount -> safe capture -> umount -> mdconfig -d -> worker`) without claiming real FreeBSD execution in this cloudtainer.
- Added Capsicum worker SHA-256 vector coverage beyond the short fixture string, including empty, padding-boundary, block-boundary, and multi-block fd-3 inputs.

## Audit/refactor result

The useful correction was to move launch authority out of implicit runtime defaults and into checkable evidence:

- fd-only now means more than pathless argv and delegated fd 3/fd 4; the worker also gets an empty environment and a private cwd that is not the media tree or repository.
- fd-slot restoration is now explicit, reducing the risk that a parent process with pre-existing fds 3/4/5 is silently damaged or that the child receives the wrong authority.
- The host-smoke lane now has both failure and success simulations, so it is less dependent on prose to describe the future FreeBSD run sequence.

## Validation

A fresh release-critical hygiene ledger completed successfully:

- `session-reviews/DeriveBSD-rev0517-2026.06.05-release-critical-hygiene-ledger.json`
- Final status: 34 / 34 release-critical checks passed.

The completed ledger was copied into:

- `spec/examples/cube.hygiene.run.ledger.json`

Direct post-ledger checks passed, including:

- `python3 -B tools/check_cube_hygiene_run_ledger.py`
- `python3 -B tools/check_generated_artifact_version_ids.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_source.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_build.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_bridge.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_backend_run.py`
- `python3 -B tools/check_removable_media_local_fallback_vertical_slice.py`
- `python3 -B tools/check_generated_docs.py`
- `python3 -B tools/validate_spec_examples.py`
- `python3 -B tools/lint_spec_schemas.py`
- `python3 -B tools/check_consistency.py`
- `python3 -B tools/check_frontdoor_budget.py`
- `python3 -B tools/check_no_python_bytecode_artifacts.py`

`validate_spec_examples.py` validated 467 examples.  `check_frontdoor_budget.py` passed with the existing warnings for `docs/00-index.md` and `docs/99-llm-runbook.md`; the budget was not raised.

## Remaining highest risk

This still is not the real FreeBSD host proof.  The next substantive cut should run the host-smoke path on FreeBSD, bind the compiled C worker binary digest, create/attach a disposable image, perform real read-only/untrusted mount and real unmount/detach, launch with empty environment and private cwd, run the worker with fd 3/fd 4 plus the fd-5 non-media canary, and preserve the same receipt contract.
