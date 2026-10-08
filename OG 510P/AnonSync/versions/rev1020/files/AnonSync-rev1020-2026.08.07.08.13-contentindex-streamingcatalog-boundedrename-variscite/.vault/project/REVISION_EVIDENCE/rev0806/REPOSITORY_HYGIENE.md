# Rev0806 repository hygiene

- The release tree contains source, headers, tests, fuzz sources, tools,
  documentation, revision evidence, and the pinned SQLite source.
- VCS metadata, build directories, CMake outputs, executables, object/static/
  shared libraries, sanitizer profiles, compiler time-trace build products,
  Python bytecode/cache directories, core dumps, and temporary work files are
  excluded from the sealed tree.
- Raw compiler trace JSON is preserved under revision evidence only; generated
  object files and build directories are not packaged.
- `src/sync_domain_test_access.hpp` is intentionally private to the source tree.
  No corresponding header exists under `include/`, and the boundary audit
  requires exactly two include users.
- `MANIFEST.sha256` is generated from the final exact file inventory and does
  not recursively list itself.
- `ACTIVE_IMPLEMENTATION_PROJECTION.json` binds CMake, source, headers, tests,
  tools, fuzz sources, and pinned third-party source bytes.
- The release verifier requires safe unique ZIP paths, one `AnonSync/` root, no
  symlinks, canonical revision evidence, exact manifest inventory and hashes,
  active-projection recomputation, minimum source baselines, and CRC integrity.
- Incomplete from-scratch and sanitizer attempts remain labeled as attempts;
  their logs are not converted into green claims.
- The exact parent archive filename, digest, and 25/25 verifier output are
  preserved under `lineage/`.
