# Rev0804 repository hygiene

- The release tree contains source, tests, tools, evidence, documentation, and
  the pinned SQLite source only.
- Build directories, CMake outputs, object files, executables, sanitizer files,
  Python bytecode/cache directories, and VCS metadata are excluded.
- `MANIFEST.sha256` is generated from the final exact file inventory and does
  not recursively list itself.
- The active implementation projection is recomputed from CMake, source,
  headers, tests, tools, fuzz targets, and pinned third-party identity files.
- ZIP verification requires one `AnonSync/` root, safe unique member paths, no
  symlinks, exact manifest inventory and hashes, and successful CRC validation.
