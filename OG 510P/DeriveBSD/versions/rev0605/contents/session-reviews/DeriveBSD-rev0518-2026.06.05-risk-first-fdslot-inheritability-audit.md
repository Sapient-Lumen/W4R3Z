# DeriveBSD rev0518 risk-first audit: fd-slot inheritability and host-smoke launcher truth

Last updated: 2026-06-05r550

## Focus

The risk focus stayed on the removable-media local fallback lane, specifically the worker-launch boundary used by the FreeBSD host-smoke path and the Capsicum bridge probes.

The concrete problem: the fixed-fd launcher had been tightened to save and restore parent fd slots 3/4/5, but the evidence still needed to cover a quieter authority leak class: restoring a parent fd's file identity while changing its inheritable flag. That can make a later subprocess inherit authority the parent previously kept close-on-exec.

## Changes made

- Hardened `tools/removable_media_fd_slot_launcher.py` so fd identity evidence includes `inheritable` and restore explicitly resets the original inheritability with `os.set_inheritable(fd, original_inheritable)`.
- Kept the stronger out-of-band save policy `duplicate-target-fds-above-delegated-range-before-clearing-slots`, which avoids saving fd 3 into fd 4 before fd 4 has been inspected.
- Extended the FreeBSD host-smoke checker so the cross-dup regression proves distinct open parent fd 3/4/5 slots preserve both identity and inheritability across save/clear/restore.
- Refactored `tools/check_removable_media_local_fallback_capsicum_worker_sha256_vectors.py` to use the shared fd-slot launcher instead of a local save/restore helper, so digest-vector probes do not carry a second weaker fd-delegation implementation.
- Added/kept `tools/check_removable_media_fd_slot_policy_consistency.py` in release-critical hygiene so policy strings in schemas, examples, validations, and docs cannot drift from `tools/removable_media_fd_slot_launcher.py`.
- Regenerated the Capsicum bridge, backend-run, host-smoke, SHA-vector, cube audit/refactor/checkset, and hygiene-ledger evidence surfaces for `2026-06-05r550`.

## Validation summary

The completed release-critical ledger is:

`session-reviews/DeriveBSD-rev0518-2026.06.05-release-critical-hygiene-ledger.json`

It records `35 / 35` release-critical checks passed. The completed ledger was copied into:

`spec/examples/cube.hygiene.run.ledger.json`

Direct checks also passed after the final ledger copy, including:

- `python3 -B tools/check_cube_hygiene_run_ledger.py`
- `python3 -B tools/check_generated_artifact_version_ids.py`
- `python3 -B tools/validate_spec_examples.py`
- `python3 -B tools/check_cube_hygiene_checkset_manifest.py`
- `python3 -B tools/check_cube_schema_audit_report.py`
- `python3 -B tools/check_cube_schema_refactor_backlog.py`
- `python3 -B tools/check_removable_media_fd_slot_policy_consistency.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_bridge.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_sha256_vectors.py`
- `python3 -B tools/check_removable_media_local_fallback_vertical_slice.py`

## Remaining risk

This is still cloudtainer proof plus FreeBSD-shaped host-smoke preparation, not a completed FreeBSD host run. The next real-risk step remains: run the host-smoke path on an actual FreeBSD host, compile the C worker, attach and mount a disposable image, safe-capture, unmount/detach, run the worker with fd 3/fd 4/fd 5, and bind the real transcript into the same receipt family.
