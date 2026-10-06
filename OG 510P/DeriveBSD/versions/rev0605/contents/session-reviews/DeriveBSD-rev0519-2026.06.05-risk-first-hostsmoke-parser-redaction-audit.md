# DeriveBSD rev0519 session review — host-smoke parser/redaction hardening

## Focus

Risk-first work stayed on the removable-media local fallback lane, especially the first real FreeBSD host-smoke proof. The goal was to remove places where checker-only simulation or host command output could become misleading durable evidence before a real FreeBSD run exists.

## Substantive changes

- Tightened `tools/freebsd/run_removable_media_local_fallback_host_smoke.py` so `mdconfig` output is parsed only as numeric `N`, `mdN`, or `/dev/mdN` shapes. Traversal, suffix text, shell-shaped output, bare `md`, nonnumeric units, and non-normalized detach inputs are rejected before constructing `/dev/<unit>` or a detach argument.
- Added `md_unit_detach_number()` so the detach command receives a numeric-only unit derived from the normalized `mdN` shape rather than using a broad string prefix removal.
- Redacted private host-smoke work-root paths from command receipts with `$PRIVATE_WORK_ROOT`, and added `command_shape_sha256` plus `private_work_root_redacted` evidence to host command and cleanup command rows.
- Strengthened `tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py` with parser regression cases and command-redaction checks. The checker now fails if success/failure simulation receipts leak `/tmp/derivebsd-host-smoke...` paths or omit command-shape digests.
- Refreshed the Capsicum worker bridge and FreeBSD backend-run evidence to bind the r551 bridge/run ids.

## Audit/refactor result

The useful correction was narrow: host command output and host scratch paths are no longer treated as harmless strings in future host-proof evidence. `mdconfig` output is now shape-checked before it becomes device authority, and durable validation receipts no longer depend on randomized temporary work-root names.

This cut intentionally avoided adding another doctrine/registry layer.

## Validation

A fresh release-critical hygiene ledger is included at:

`session-reviews/DeriveBSD-rev0519-2026.06.05-release-critical-hygiene-ledger.json`

Final status: 35 / 35 release-critical checks passed.

The completed ledger was copied into:

`spec/examples/cube.hygiene.run.ledger.json`

Key direct checks after the final ledger copy:

- `python3 -B tools/check_removable_media_local_fallback_freebsd_host_smoke_runner.py`
- `python3 -B tools/check_removable_media_local_fallback_capsicum_worker_bridge.py`
- `python3 -B tools/check_removable_media_local_fallback_freebsd_backend_run.py`
- `python3 -B tools/check_removable_media_fd_slot_policy_consistency.py`
- `python3 -B tools/check_removable_media_local_fallback_vertical_slice.py`
- `python3 -B tools/check_cube_hygiene_run_ledger.py`
- `python3 -B tools/check_generated_artifact_version_ids.py`
- `python3 -B tools/validate_spec_examples.py`
- `python3 -B tools/check_generated_docs.py`
- `python3 -B tools/check_frontdoor_budget.py`
- `python3 -B tools/check_no_python_bytecode_artifacts.py`

`validate_spec_examples.py` validated 467 examples.

## Remaining highest risk

The next substantive step remains the real FreeBSD host proof: run the host-smoke path on FreeBSD, compile the C worker, bind the binary digest, create/attach a disposable image, mount it read-only/untrusted, safe-capture the selected file, perform real unmount/detach, and run the worker with fd 3/fd 4/fd 5 while preserving the same receipt contract.
