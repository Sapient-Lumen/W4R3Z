# Cube audit/refactor — rev0013

rev0013 adds a small audit lane because the cube is now large enough to grow stale surfaces.

## Refactor performed

The shipped rev0013 tree prunes transient `.pytest_cache` from the artifact.

## Audit added

`cubeaudit.py` and `scripts/evidence/run_cube_audit.py` check for:

- transient packaging surfaces such as `.pytest_cache` and `__pycache__`,
- duplicate ADR numeric prefixes,
- duplicate docs numeric prefixes,
- near-duplicate Python module names such as separator-only variants.

The audit is non-failing for now. Warnings are written to `artifacts/process/rev0013_cube_audit.json`.

## Known warnings are not secrets

The cube has duplicate ADR/doc numbering from fast prior revisions. This is acceptable for a baby cube if it is visible. A later cleanup can add an explicit supersession map or collapse duplicate historical surfaces.

## Hard guess

```text
Speculative systems need entropy accounting before they need polish.
```
