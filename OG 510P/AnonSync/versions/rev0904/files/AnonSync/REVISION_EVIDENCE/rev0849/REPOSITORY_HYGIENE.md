# AnonSync rev0849 repository hygiene

The release projection contains source and handoff evidence only. Build trees,
compiler outputs, VCS metadata, editor state, Python bytecode, CTest scratch
state, and symbolic links are not release inputs.

## Final checks

- active implementation projection: 269 files, with path, byte count, and
  SHA-256 bound in `ACTIVE_IMPLEMENTATION_PROJECTION.json`;
- source patch: 23 changed active files, 1,268 insertions, 413 deletions;
- third-party source changes: zero;
- generated `__pycache__`, `.pyc`, and `.pyo`: removed and rechecked;
- source patch replay: 269/269 exact active-file matches;
- final GCC dependency closure: no compilation or link work;
- package contains one canonical `AnonSync/` root and no symlinks;
- `MANIFEST.sha256` is an exact nonrecursive inventory of every packaged file;
- final directory and ZIP are independently verified by the packaged verifier;
- ZIP CRC is verified after construction.

## Refactor cost observation

The new typed verification-budget boundary necessarily includes the large
SQLite handle-slot interface, causing broad incremental recompilation. This is a
build-cost smell, not a reason to weaken lifetime ownership. The next refactor
should reduce header fan-out through a smaller stable borrow interface or a
private implementation and should be accepted only with measured dependency
improvement and unchanged process/generation tests.
