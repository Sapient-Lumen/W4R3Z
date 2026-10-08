# SQLite 3.53.3 provenance

AnonSync vendors the SQLite 3.53.3 amalgamation so every WAL-backed evidence
store uses a runtime that contains the WAL-reset corruption fix released in
SQLite 3.51.3 and later.

- Upstream project: https://sqlite.org/
- Upstream release: 3.53.3 (2026-06-26)
- Upstream source ID: `2026-06-26 20:14:12 d4c0e51e4aeb96955b99185ab9cde75c339e2c29c3f3f12428d364a10d782c62`
- Upstream amalgamation archive: `sqlite-amalgamation-3530300.zip`
- Upstream archive SHA3-256: `d45c688a8cb23f68611a894a756a12d7eb6ab6e9e2468ca70adbeab3808b5ab9`
- Upstream `sqlite3.c` SHA3-256: `28e484abdaa43630e34040ef6ed92be973a1ad54107803d8af5145b889c23ed7`
- Vendored `sqlite3.c` SHA-256: `87497ab605bedd0dbee27a209c1eeff8c89b229b13f921a7efdbb81a13f779fd`
- Vendored `sqlite3.h` SHA-256: `4ff81af4849acabc76fc8349abb926814395072617ca18e08800abf734ab7612`

The amalgamation was generated from the Debian sid `sqlite3` source package
3.53.3-1, whose canonical upstream source tree carries manifest UUID
`d4c0e51e4aeb96955b99185ab9cde75c339e2c29c3f3f12428d364a10d782c62`.
The generated `sqlite3.c` exactly matches SQLite's published SHA3-256 above.

SQLite states that its source is in the public domain. `LICENSE.md` is copied
from the corresponding upstream source tree.

## Build and runtime attestation

`cmake/AnonSyncBundledSqliteProfile.cmake` is the single reviewed dependency
profile. It declares a closed five-file inventory. A bundled build now fails
during CMake configuration if an entry is missing, undeclared, a directory, or
a symlink, or unless all five vendored files match that profile: `sqlite3.c`,
`sqlite3.h`, `sqlite3ext.h`, `LICENSE.md`, and this provenance record. The gate
checks both SHA-256 and SQLite's published SHA3-256 for `sqlite3.c`.

CMake generates a private C++ profile header from the same record. The runtime
WAL gate statically binds the included `sqlite3.h` version and source ID and
then rejects any linked SQLite runtime whose reported version or source ID is
not exact. `tools/verify_bundled_sqlite_profile.py` independently repeats the
file, header-macro, and amalgamation-macro checks without compiling the tree.
The same native CMake verifier also runs as a phony dependency before the
amalgamation target can build, so a retained file changed after configuration
is rejected instead of being compiled under stale configure-time evidence.
