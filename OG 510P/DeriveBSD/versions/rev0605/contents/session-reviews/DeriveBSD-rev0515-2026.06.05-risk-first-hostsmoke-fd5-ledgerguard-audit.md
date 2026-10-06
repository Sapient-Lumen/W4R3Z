# DeriveBSD rev0515 risk-first host-smoke/fd5/ledger guard audit

Latest cut: 2026-06-05r546

## Focus

This cut stayed on the removable-media local fallback lane because it remains the most important unfinished implementation boundary. The goal was to make the next real FreeBSD host proof concrete without claiming that the Linux cloudtainer had performed host work.

## Substantive changes

- Added the FreeBSD-only host-smoke runner at `tools/freebsd/run_removable_media_local_fallback_host_smoke.py` and its guardrail `tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py`.
- Added refusal evidence at `validation/removable-media-local-freebsd-host-smoke.refusal.json`; in this cloudtainer it refuses with `non-freebsd-host` and performs no host commands.
- Documented the host-smoke path in `docs/current/removable-media-freebsd-host-smoke.md`.
- Extended the Capsicum worker bridge and C worker to use fd 5 as a broker-owned non-media inherited-fd canary. The worker closes unexpected descriptors with `closefrom(FD_AFTER_DELEGATED_SET)` before capability entry and reports `extra_fds_closed_before_cap_enter` plus `extra_fd_scan_limit`.
- Updated the cloudtainer probe shim so `closefrom` actually closes descriptors during the shim execution probe instead of being only a source token.
- Tightened `tools/hygiene.py` and `tools/check_cube_hygiene_run_ledger.py` so resumable hygiene evidence refuses stale prior-release ledgers as well as stale checker digests.

## Audit/refactor finding

The most important audit finding was in evidence integrity, not another schema family: a resumable ledger must not merge passed rows merely because command names still match. It now requires current wrapper digest, current checker digest, current `generated_for_version`, and current `ledger_id` before reusing old passed rows.

## Validation

A fresh/resumed release-critical hygiene ledger completed at `session-reviews/DeriveBSD-rev0515-2026.06.05-release-critical-hygiene-ledger.json` with 33/33 checks passed. The completed ledger was copied to `spec/examples/cube.hygiene.run.ledger.json` and rechecked.

Key direct checks run after final ledger copy included `validate_spec_examples.py`, `lint_spec_schemas.py`, `check_generated_docs.py`, `check_generated_artifact_version_ids.py`, `check_cube_hygiene_run_ledger.py`, the removable-media host-smoke/bridge/backend/vertical-slice checks, version/release metadata checks, front-door budget, validation-log cleanliness, and no-bytecode/no-root-log package hygiene.

## Remaining highest risk

The next substantive step is still real FreeBSD host proof: compile the C worker on FreeBSD, create/attach a disposable image, mount it read-only and untrusted, safe-capture a selected file, perform real unmount/detach, and exec the C worker with only fd 3/fd 4 plus the fd-5 canary while preserving the same receipt contract.
