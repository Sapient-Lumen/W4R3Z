# DeriveBSD rev0601 transaction-spine review

## Intent

This revision follows the rev0600 mission audit by spending work on the riskiest executable spine, not another registry family. The target was the dry-run runtime transaction path: content-addressed artifact publish, state journal ordering, current-pointer commit observation, and state-lock ownership.

## Priority changes made

- `tools/derive_runtime.py` now emits cube cut `2026-06-18r626`.
- Content-addressed artifacts are built in unique hidden staging directories and published by `publish_artifact_tree(...)`; rebuilding identical content reuses the existing CAS directory and refuses to delete/recreate it.
- Activation writes the precommit state journal before creating the generation receipt or changing `current-generation.json`.
- Activation and rollback use `commit_current_generation(...)`, which writes, reads back, compares exact state, and refuses journal cleanup on mismatch.
- State mutation locks keep the file descriptor open, take `flock`, record the original device/inode, and refuse to unlink if another owner replaces the lock path.
- `derive-runtime state-status` gives read-only recovery triage for clean state, applied pending journals, not-applied pending journals, divergent state, and malformed journals.

## Regression coverage added

`tools/check_runtime_golden_thread.py` now proves the four high-risk cases identified in rev0600:

1. Rebuilding the same artifact keeps the same CAS path, digest, and inode.
2. Fault-injected current-pointer non-write raises a commit-readback mismatch instead of producing a success receipt.
3. A replacement state lock is not deleted by the first owner during cleanup.
4. A malformed pending state journal is classified by `state-status` as quarantine-required without mutation.

Existing stale-journal, lock, duplicate-generation, symlink, tamper, activation, explanation, and rollback checks remain in the same golden thread.

## Audit/refactor performed

The refactor stayed inside the runtime and generated-evidence surfaces:

- Extracted explicit helpers: `unique_artifact_staging_root`, `publish_artifact_tree`, `commit_current_generation`, and `cmd_state_status`.
- Kept the schema cube from growing; no new schema family was added for this repair.
- Refreshed the generated schema audit, schema refactor backlog, hygiene checkset manifest, generated docs, runtime golden-thread evidence, FreeBSD proof-contract examples, and release-critical ledger so current docs bind to r626 evidence rather than stale r625 artifacts.

## Validation

- `python3 tools/check_runtime_golden_thread.py` passed.
- `tools/hygiene.py --profile release-critical --ledger-json spec/examples/cube.hygiene.run.ledger.json --resume-ledger` completed the release-critical profile.
- Canonical release-critical ledger result: 52 passed, 0 failed, 0 timed out, `run_complete=true`.
- `python3 -B tools/check_cube_hygiene_run_ledger.py` passed after the full ledger write.
- `python3 -B -S tools/check_no_python_bytecode_artifacts.py` passed after transient bytecode cleanup.

## Honest remaining boundary

This still does not implement real FreeBSD package/base resolution, `bectl` activation, host mutation, bhyve execution, or imported real-host proof. The important forward movement is that the local transaction spine is less capable of lying before the project crosses that real-host boundary.
