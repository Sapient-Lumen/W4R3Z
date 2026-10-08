# rev0796 repository hygiene

- No VCS directory, build tree, executable, object, archive, Python cache, core
  dump, or sanitizer profile is included.
- Historical evidence remains byte-preserved; rev0796 evidence is additive.
- The release manifest excludes itself and binds every other packaged file.
- The active implementation projection is independently recomputed by the
  package verifier and includes CMake, source, headers, tests, tools, bundled
  third-party source, and fuzz sources.
- The ZIP has one `AnonSync/` root, unique safe paths, no symlink members, and
  passes archive CRC verification.
