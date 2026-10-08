# rev0783 repository and handoff hygiene

The active worktree was reconstructed from a verified full-source archive and
kept separate from build directories. Build trees, compiler objects, binaries,
CMake caches, VCS metadata, Python caches, core dumps, and temporary SQLite
files are excluded from the release ZIP.

Historical textual evidence remains in the cube because it carries lineage and
security decisions. It is not compiled and is distinguished from current
rev0783 evidence. The package verifier requires one `AnonSync/` root, a complete
source/header/test tree, a successful required gate, safe member names, no
symlinks, no generated binaries, and an exact SHA-256 manifest file set.

The source-less rev0782 artifact exposed a serious handoff anti-pattern: a ZIP
can be internally well formed while omitting the implementation it purports to
revise. Rev0783 therefore makes source completeness a release condition rather
than relying on archive existence, filename revision, or CRC integrity.

Compilation cost remains wasteful. `src/sync_domain.cpp` is roughly 24,000
lines and dominates clean optimized builds. Decomposition should follow
invariant ownership—checkpoint repository, receipt evidence, work-order state
machine, operator projection—not arbitrary line-count splitting. The
SQLite-process refactor follows that rule by isolating process identity, owner
slots, mutex lifetime, and policy authority into independently testable units.
