# Rev0805 repository hygiene

- The release tree contains source, headers, tests, fuzz sources, tools,
  documentation, evidence, and the pinned SQLite source.
- Build directories, CMake outputs, object files, static/shared libraries,
  executables, Python bytecode/cache directories, VCS metadata, sanitizer
  profiles, and core dumps are excluded.
- `MANIFEST.sha256` is generated from the final exact file inventory and does
  not recursively list itself.
- `ACTIVE_IMPLEMENTATION_PROJECTION.json` binds CMake, source, headers, tests,
  tools, fuzz sources, and pinned third-party source bytes.
- The package verifier requires one `AnonSync/` ZIP root, safe unique paths, no
  symlinks, exact revision evidence, exact manifest inventory and hashes, active
  projection recomputation, source baselines, and CRC integrity.
- Evidence logs preserve deliberate limitations; incomplete full-core sanitizer
  work is labeled as an attempt rather than a pass.
- The parent archive filename, SHA-256, and 25/25 verifier result are preserved
  under `lineage/`.
