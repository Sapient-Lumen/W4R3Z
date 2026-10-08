# rev0785 repository hygiene

The release archive is a full source cube, not a build cache. Packaging excludes
`.git`, CMake build trees, object/static/shared libraries, executables, Python
bytecode/cache directories, sockets, and symlinks. Validation logs and audit
JSON are retained because they are evidence, not executable build products.

Historical evidence remains, but no phantom rev0784 implementation or notes are
included. Rev0785 derives from the verified full-source rev0783 archive and
records the rejected incomplete direction in its own audit rather than treating
a filename or abandoned worktree as authority.

The largest active implementation files remain `src/sync_domain.cpp` (24,528
lines) and `src/sqlite_replay_ledger.cpp` (4,466 lines). This concentration is a
review and build-scalability debt. Future extraction should preserve one
invariant owner per module and avoid copying historical evidence into active
source paths.
