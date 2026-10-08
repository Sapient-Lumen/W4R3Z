# Rev0859 repository hygiene

- Active implementation projection: 303 files, 17,917,387 bytes.
- `src/sync_domain.cpp`: 15,108 lines.
- `src/sync_peer_ingestion.cpp`: 1,960 lines.
- Extracted streamed decoder: 287 implementation lines plus 93 header lines.
- Focused decoder test: 442 lines.
- Registered decoder audit: 415 lines.
- CMake registry: 2,924 lines.
- Generated Python bytecode and cache directories were removed before
  projection, manifest, and package verification.
- No build directory, object, static library, executable, VCS metadata, or
  symlink is included in the release tree.
- No bundled third-party file changed.

The extracted owner reduces semantic duplication, but the repository still has
high change amplification in the domain monolith, selftest units, CMake test
registration, and historical evidence corpus. Future revisions should prefer
small linked owners and generated checked inventories over additional lexical
rules.
