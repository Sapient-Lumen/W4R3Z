# AnonSync rev0905 research record

Primary sources reviewed on 2026-07-26:

- SQLite `sqlite3_create_filename()` and `sqlite3_free_filename()` contract: https://sqlite.org/c3ref/create_filename.html
- SQLite filename-family accessors: https://sqlite.org/c3ref/filename_database.html
- SQLite WAL design and read-only WAL conditions: https://sqlite.org/wal.html
- SQLite VFS and I/O method contracts: https://sqlite.org/c3ref/vfs.html
- SQLite 3.53.4 release notes: https://sqlite.org/releaselog/3_53_4.html
- SQLite current download and archive identities: https://sqlite.org/download.html
- SQLite compile-time source identity: https://sqlite.org/c3ref/c_source_id.html
- CMake `configure_file()` authority: https://cmake.org/cmake/help/latest/command/configure_file.html
- CMake file hashing: https://cmake.org/cmake/help/latest/command/file.html
- SLSA build provenance model and limits: https://slsa.dev/spec/v1.2/build-provenance
- SLSA threat model: https://slsa.dev/spec/v1.2/threats

Reasoned conclusions and speculation:

1. Observation is a security capability. A status command that can reconcile, checkpoint, create sidecars, or synchronize durability can manufacture evidence and should be designed separately from operational ownership.
2. VFS wrappers are representation adapters, not merely pathname filters. Passing text that looks identical is unsafe when the delegated API requires hidden lifetime/layout metadata.
3. Build configuration belongs in active source identity. Omitting CMake policy from the projection allowed executable dependency authority to drift while the reported source digest remained unchanged.
4. The next highest-leverage implementation is not another isolated store primitive. It is a bounded supervisor joining the existing admission, transport, chunking, conflict, effect, recovery, and reporting primitives into one continuously tested causal loop.
5. A later SQLite 3.53.4 update should be isolated from this repair so dependency deltas, VFS behavior, crash tests, sanitizers, and package provenance remain attributable.
