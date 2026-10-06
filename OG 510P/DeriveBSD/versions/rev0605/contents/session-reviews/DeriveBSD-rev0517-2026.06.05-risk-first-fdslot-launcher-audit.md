# DeriveBSD rev0517 risk-first audit: fd-slot launcher proof

## Focus

The riskiest unfinished lane remains removable-media local fallback, especially the first real FreeBSD host proof. This cut did not add another doctrine registry. It corrected the host-smoke worker launcher boundary so fixed delegated fd slots cannot leak back into the parent while evidence says they were restored.

## Main finding

The Python host-smoke launcher delegated fd 3, fd 4, and fd 5 by opening the preserved object, derivative output, and broker non-media canary, then saving/restoring target slots. If the newly opened files themselves occupied fd 3/4/5, the launcher could confuse newly delegated authority with pre-existing parent fd state. In that shape, a receipt could say `launcher_restored_parent_fd_slots = true` while the parent retained delegated worker fds after child exit.

## Changes

- Added `tools/removable_media_fd_slot_launcher.py` with the explicit policy `save-and-clear-target-fds-before-opening-delegated-files`.
- Refactored `tools/freebsd/run_removable_media_local_fallback_host_smoke.py` to save and clear fd 3/4/5 before opening delegated worker files, install only the intended fds for the child, then close/restore the parent slots after child exit.
- Moved `tools/removable_media_capsicum_worker_bridge.py` onto the same fd-slot policy so the cloudtainer execution probe and future host-smoke runner share the same launch-envelope rule.
- Extended `spec/removable.media.capsicum.worker.bridge.schema.json` and `spec/removable.media.local.freebsd.backend.run.receipt.schema.json` so bridge/backend evidence carries launcher fd-slot policy and restoration evidence.
- Strengthened `tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py` with a regression that clears fd 3/4/5, invokes `run_worker()` with a dummy fd-4-reporting child, and fails if delegated target slots remain open in the parent after child exit.
- Refreshed bridge/backend/host-smoke validation artifacts, generated docs, and the release-critical hygiene ledger for `2026-06-05r549`.

## Validation

The release-critical hygiene ledger at `session-reviews/DeriveBSD-rev0517-2026.06.05-release-critical-hygiene-ledger.json` completed `34 / 34` checks with result `passed`. It was copied into `spec/examples/cube.hygiene.run.ledger.json` and revalidated.

Important direct checks run after the final ledger copy included:

- `python3 -B tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_bridge.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_backend_run.py`
- `python3 -B tools/check_removable_media_local_fallback_vertical_slice.py`
- `python3 -B tools/check_cube_hygiene_run_ledger.py`
- `python3 -B tools/check_generated_artifact_version_ids.py`
- `python3 -B tools/check_generated_docs.py`
- `python3 -B tools/validate_spec_examples.py`
- `python3 -B tools/lint_spec_schemas.py`
- `python3 -B tools/check_consistency.py`
- `python3 -B tools/check_frontdoor_budget.py`
- `python3 -B tools/check_no_python_bytecode_artifacts.py`

`check_frontdoor_budget.py` passed but still warned that `docs/00-index.md` and `docs/99-llm-runbook.md` are above their original observed byte baselines.

## Remaining risk

The real remaining risk is still the FreeBSD host proof itself: compile the C worker on FreeBSD, bind the binary digest, create/attach a disposable image, perform real read-only/untrusted mount and real unmount/detach, run the worker with fd 3/fd 4/fd 5, and preserve the same receipt contract. The fd-slot fix makes that future proof less likely to be self-deceptive.

