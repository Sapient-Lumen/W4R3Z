# Rev0811 repository hygiene

- Source and validation builds were kept under `/tmp/anonsync0811`; no build was
  performed under `/mnt/data`.
- The working source tree contained no symlinks, VCS metadata, Python cache,
  object files, static/shared libraries, executables, CMake cache, or build
  directories before staging.
- The final package is staged into a new `AnonSync/` root rather than preserving
  the parent archive's noncanonical long root.
- The active implementation projection binds `.gitignore`, `CMakeLists.txt`, and
  every file under `include/`, `src/`, `tests/`, `tools/`, `third_party/`, and
  `fuzz/`.
- `MANIFEST.sha256` is regenerated last and lists every package file except
  itself exactly once.
- Historical evidence and the rev0810 fallback sketch are retained because they
  are part of lineage, but neither is linked into production targets.
- No third-party source changed in rev0811.
- Final directory and ZIP verification reject unsafe paths, multiple roots,
  symlinks, generated artifacts, manifest drift, revision drift, projection
  drift, and ZIP CRC failure.
