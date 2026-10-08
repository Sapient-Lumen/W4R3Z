# Exec wrapper portability audit — REV0138

Status: `pass_with_expected_environment_blockers`  
Promotion allowed: `false`

## Defect found

The stable aliases directly `exec`ed nested revision shell scripts. In this extracted zip those nested scripts were mode `0644`, so the operator-facing command failed with `Permission denied` before reaching the intended preflight blocker.

## Corrections

- Stable aliases retargeted to `REV0138` and use `exec bash`.
- Current run wrapper delegates to one-shot with `exec bash`.
- `artifacts/runtime/REV0138_public_trace_requirements.txt` exists for the bootstrap path.
- `tools/current_live_script_dependency_audit.py` now checks missing requirement files and non-portable direct shell exec.

## Remaining expected blockers

- `local_digest_verified_tinyllama_snapshot_not_available`
- `local_integrity_valid_tinyllama_snapshot_not_available`
- `transformers_not_importable`
