# DeriveBSD rev0518 risk-first fd-slot cross-dup guard audit

Last updated: 2026-06-05r550

## Focus

This cut stayed on the removable-media local fallback path and the first FreeBSD host-smoke proof. The highest-risk issue corrected here was not another schema surface: it was a fixed-fd launcher bug that could make the parent fd restoration proof lie.

## Concrete bug fixed

`tools/removable_media_fd_slot_launcher.py` previously saved target fd slots with ordinary duplication while walking fd 3, fd 4, and fd 5. If a target slot was closed, a saved duplicate of an earlier slot could land in another target slot. A later save step could then mistake that backup for a real pre-existing parent fd. In the bad case, evidence could say parent fd slots were restored while the identities being restored were already confused.

The launcher policy is now:

`duplicate-target-fds-above-delegated-range-before-clearing-slots`

Saved copies are forced above the delegated range before any target slot is cleared. Restoration also preserves parent-slot inheritability as part of fd identity evidence.

## Implementation changes

Updated:

- `tools/removable_media_fd_slot_launcher.py`
- `tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py`
- `tools/check_removable_media_fd_slot_policy_consistency.py`
- `tools/removable_media_capsicum_worker_bridge.py` generated evidence
- `tools/run_removable_media_local_freebsd_backend.py` generated evidence
- bridge/backend schemas and examples carrying launcher policy evidence

The FreeBSD host-smoke checker now includes a cross-dup regression that opens distinct parent files into fd 3, fd 4, and fd 5 with mixed inheritability, runs save/clear/restore, and fails if identity or inheritability changes.

## Audit/refactor result

The useful refactor is narrow and authority-facing. Fixed-fd delegation now has one shared launcher helper and a policy consistency check that keeps code, schemas, examples, validation receipts, backend binding, and docs aligned on the same launcher semantics.

This reduces the risk that the future real FreeBSD host run proves only the happy case where parent fd 3/4/5 were initially closed.

## Validation

A fresh/resumed release-critical hygiene ledger is included at:

`session-reviews/DeriveBSD-rev0518-2026.06.05-release-critical-hygiene-ledger.json`

Final ledger status: 35 / 35 release-critical checks passed.

Key direct checks run after the final ledger copy included:

- `python3 -B tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py`
- `python3 -B tools/check_removable_media_fd_slot_policy_consistency.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_bridge.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_backend_run.py`
- `python3 -B tools/check_removable_media_local_fallback_vertical_slice.py`
- `python3 -B tools/check_cube_hygiene_run_ledger.py`
- `python3 -B tools/check_generated_artifact_version_ids.py`
- `python3 -B tools/validate_spec_examples.py`
- `python3 -B tools/lint_spec_schemas.py`
- `python3 -B tools/check_generated_docs.py`
- `python3 -B tools/check_consistency.py`
- `python3 -B tools/check_frontdoor_budget.py`
- `python3 -B tools/check_no_python_bytecode_artifacts.py`

`validate_spec_examples.py` validated 467 examples.

`check_frontdoor_budget.py` passed. It still warns that `docs/00-index.md` and `docs/99-llm-runbook.md` are above their original observed byte baselines; the line-count budget was preserved without raising it.

## Remaining highest risk

The next substantive step remains the real FreeBSD host proof: run host-smoke on FreeBSD, compile the C worker, bind the binary digest, create/attach a disposable image, perform real read-only/untrusted mount and real unmount/detach, run the worker with fd 3/fd 4/fd 5, and preserve the same receipt contract.
