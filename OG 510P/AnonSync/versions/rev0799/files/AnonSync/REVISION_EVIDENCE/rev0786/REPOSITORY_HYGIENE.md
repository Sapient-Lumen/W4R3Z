# rev0786 repository hygiene

The published cube is a full source release, not a build cache. Packaging
excludes `.git`, CMake build trees, executables, object/static/shared libraries,
Python bytecode/cache directories, sockets, and symlinks. Validation logs,
audit reports, source deltas, and research notes remain because they are release
evidence rather than executable artifacts.

Rev0786 derives from the verified rev0785 archive named in `LINEAGE.json` and
from one local baseline commit created immediately after extraction. No
abandoned rev0784/rev0786 worktree, build product, or filename-only predecessor
is treated as authority.

Active source concentration remains a material cost: `src/sync_domain.cpp` has
24,528 lines, `src/sqlite_replay_ledger.cpp` has 4,466, and
`src/sync_peer_ingress_lifecycle.cpp` has 3,833. Historical evidence is kept
under revision-scoped directories; future decomposition should reduce active
translation-unit concentration without copying old source into competing
locations.
