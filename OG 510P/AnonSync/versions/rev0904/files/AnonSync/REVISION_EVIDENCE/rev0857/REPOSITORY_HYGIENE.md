# Repository hygiene

- Active implementation projection: **295 files**,
  **17808174 bytes**, SHA-256 `0d3012a2f8584f0d7788d66cf3d366aea6ec3fe1dd1062a1f4a082e004ae3732`.
- Active source delta: **10 files**, **1,326 insertions**, **152 deletions**;
  bundled third-party changes: **0**.
- Generated Python bytecode, VCS metadata, build trees, object files,
  executables, sanitizer outputs, and temporary replay trees are excluded from
  the release package.
- A generated `tools/__pycache__` directory was detected after audits, removed,
  and the active projection was recomputed before manifest generation.
- Build products are outside the source tree. The release archive has one
  `AnonSync/` root and no symlinks.
- The failed first sanitizer link is retained under `operational/` because it
  exposed a real compile/link inventory gap; it is not counted as a passing
  validation result.
- The active patch explicitly represents all new files, applies cleanly to the
  independently verified rev0856 parent, and matches all ten final active paths
  byte-for-byte.
