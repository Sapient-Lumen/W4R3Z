# DeriveBSD rev0509 risk-first audit: detach fd proof, worker preflight, apply gate

Date: 2026-06-04
Base linked package: DeriveBSD-rev0508-2026.06.04.12.28-capsicumworker-logpurge-workdirguard-ashmarten.zip
Current cut: 2026-06-04r540

## Priority focus

This cut keeps the focus on the removable-media local fallback path, because it is the most implementation-critical lane and the easiest place for a receipt-heavy cube to become self-deceptive.

The risky proof bug was the parent-held source-media fd canary.  It showed that the child did not inherit a source-media fd, but the parent still held source-media authority while the receipts claimed detach before worker launch.  The proof is now split correctly:

- source-media fds are closed before detach and before worker launch;
- fd-leak detection uses a broker-owned non-media canary;
- receipts record `source_media_fd_closed_before_detach`, `source_media_fd_closed_before_worker`, and `leak_canary_fd_source = broker-nonmedia-canary-not-source-media`.

## Implementation changes

- `tools/removable_media_fd_worker.py` now preflights preserved CAS input before delegation.  It rejects missing, symlink, non-regular, and digest-mismatched input before opening the worker fds.
- `tools/run_removable_media_local_fallback_prototype.py` no longer recursively deletes a user-supplied `--work-dir`; it creates an exclusive private child and preserves caller-owned siblings/sentinels.
- `tools/run_removable_media_local_freebsd_backend.py` records the corrected source-fd closure proof and refuses real CLI apply before `fstyp`/`mount` with `capsicum-worker-required-for-real-apply` until the Capsicum worker bridge is wired.
- `tools/freebsd/rm_post_detach_capsicum_worker.c` gained a syntax-only cloudtainer probe gate while keeping the production FreeBSD `<sys/capsicum.h>` path.
- `tools/check_removable_media_local_fallback_capsicum_worker_build.py` was added and wired into hygiene so ordinary C syntax/signature drift is caught before a FreeBSD host lane exists.

## Audit/refactor corrections

The audit/refactor work stayed narrow and implementation-facing:

- removed the remaining destructive prototype work-dir cleanup pattern;
- replaced the misleading source-media fd canary with a non-media broker canary;
- made preserved-input prelaunch checks common fd-worker evidence rather than ad hoc backend prose;
- kept the front-door budget by trimming README/index sediment instead of raising the budget.

## Validation evidence

Release-critical hygiene ledger:

`session-reviews/DeriveBSD-rev0509-2026.06.04-release-critical-hygiene-ledger.json`

Final status: 30 / 30 release-critical checks passed.

Additional direct checks run after the final edits included:

- `python3 tools/check_removable_media_local_fallback_capsicum_worker_source.py`
- `python3 tools/check_removable_media_local_fallback_capsicum_worker_build.py`
- `python3 tools/check_removable_media_local_fallback_prototype.py`
- `python3 tools/check_removable_media_local_fallback_freebsd_backend_run.py`
- `python3 tools/check_removable_media_local_fallback_vertical_slice.py`
- `python3 tools/validate_spec_examples.py`
- `python3 tools/lint_spec_schemas.py`
- `python3 tools/check_generated_docs.py`
- `python3 tools/check_generated_artifact_version_ids.py`
- `python3 tools/check_cube_hygiene_run_ledger.py`
- `python3 tools/check_frontdoor_budget.py`

## Remaining highest risk

The next highest-risk cut is still the real FreeBSD host lane: compile the C worker on FreeBSD, mount a disposable image or device read-only/untrusted, perform no-follow safe capture, unmount before worker launch, and run the Capsicum fd-only worker while preserving the same receipt contract.
