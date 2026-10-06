# DeriveBSD rev0507 risk-first CAS/failure-path audit

Date: 2026-06-04
Cut: 2026-06-04r538

## Priority worked

This cut stayed on the removable-media local fallback because it remains the riskiest unfinished implementation lane. The previous runner could prove the happy path, but two adapter details were still too easy to get wrong over time: digest-addressed preserved content could be treated like a mutable slot, and capture failures inside the backend bridge could degrade into process exceptions or scrollback instead of typed evidence.

## Substantive corrections

`tools/removable_media_safe_capture.py` now publishes preserved captures with a no-overwrite CAS policy. It stages copied bytes under `cas/.tmp`, computes the digest, links the temporary file into the digest-addressed object path without replacing an existing object, verifies an existing object when the digest path already exists, and fails closed if the pre-existing object does not match the digest. `tools/check_removable_media_safe_capture.py` now proves first publish, idempotent recapture, and corrupt-existing-object denial.

`tools/removable_media_fd_worker.py` now opens the derivative output slot create-exclusive without truncating an existing file. That keeps derivative output evidence from becoming a mutable scratch file and gives the backend runner a simple failure mode if stale or malicious output bytes already occupy the broker-owned slot.

`tools/run_removable_media_local_freebsd_backend.py` now keeps capture failures receipt-shaped. A missing selected member in fixture mode records `capture.error_reason`, removes the mount-shaped tree, leaves capture evidence absent, and proves the worker was not launched. The same shape is used for the real FreeBSD apply path after a mount succeeds but capture fails.

`tools/check_removable_media_local_fallback_freebsd_backend_run.py` and `tools/check_removable_media_local_fallback_vertical_slice.py` now require this failure-path/no-worker evidence in addition to the happy-path safe-capture, detach-before-worker, and fd-only worker delivery proof.

## Audit/refactor notes

The useful refactor in this cut is not a new registry. It is a narrowing of mutable boundaries: CAS object publication and derivative output creation now fail closed when a target already exists, and backend capture failure now has one structured path instead of an exception-shaped side channel.

The front-door budget still warns on README, index, and runbook byte growth. This cut did not solve that bloat; it deliberately prioritized backend safety over a front-door pruning pass.

## Validation summary

Key removable-media checks passed:

- `python3 tools/check_removable_media_safe_capture.py`
- `python3 tools/check_removable_media_local_fallback_prototype.py`
- `python3 tools/check_removable_media_local_fallback_harness_run.py`
- `python3 tools/check_removable_media_local_fallback_freebsd_backend_plan.py`
- `python3 tools/check_removable_media_local_fallback_freebsd_backend_run.py`
- `python3 tools/check_removable_media_local_fallback_vertical_slice.py`

Release-critical validation was also run directly in chunks and passed. A resumed ledger is included at `session-reviews/DeriveBSD-rev0507-2026.06.04-release-critical-hygiene-ledger.json` with 28/28 checks passed.

## Remaining highest risk

The next high-value cut is still the real FreeBSD host backend: real `fstyp`, read-only untrusted mount, no-follow safe capture, guaranteed unmount before worker launch, and host-level confinement. The current cloudtainer proof now gives that backend a stricter receipt contract, especially around no-overwrite CAS publication and no-worker failure evidence.
