# AnonSync rev0850 repository hygiene

The release projection contains source and handoff evidence only. Build trees,
compiler outputs, VCS metadata, editor state, Python bytecode, CTest scratch
state, symbolic links, and the temporary source checkpoint are excluded.

## Final checks

- active implementation projection: 273 files / 17,567,989 bytes, with path,
  byte count, and SHA-256 bound in `ACTIVE_IMPLEMENTATION_PROJECTION.json`;
- source patch: 14 changed active files, 1,106 insertions, 352 deletions;
- bundled third-party source changes: zero;
- generated `__pycache__`, `.pyc`, and `.pyo`: removed before projection;
- source patch replay: 273/273 exact active-file matches;
- final GCC normal and Ninja dry-run dependency closure: no work;
- package root: one canonical `AnonSync/` directory and no symlinks;
- `MANIFEST.sha256`: exact nonrecursive inventory of every packaged file;
- directory and ZIP: independently verified with the packaged rev0850 verifier;
- ZIP CRC: verified after construction.

## Refactor cost observation

The focused owner adds 231 production header/source lines and isolates all raw
production authorizer setters, but broad integration still relinks many targets
because the connection-authority support library sits high in the dependency
graph. The audit cleanup removes a 319-line duplicated proof surface, which is a
useful direction: future rigor should reduce parallel sources of truth rather
than add another lexical checker for each callback.
