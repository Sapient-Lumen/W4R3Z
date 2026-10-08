# Rev0778 repository hygiene

## Corrected

- removed `build-baseline/`: tracked generated Debug build products;
- removed `build-rev0778-baseline/`: tracked generated CMake/Make build tree;
- removed 488 tracked blobs totaling 286,095,753 bytes;
- added `.gitignore` for root build trees, Python cache, and core files;
- retained portable text/JSON validation evidence instead of binaries;
- package generation excludes `.git`, all build roots, caches, and crash output.

The complete deletion inventory is
`audit/REMOVED_TRACKED_BUILD_ARTIFACTS.tsv`. The JSON summary is
`audit/removed_tracked_build_artifacts.json`.

## Current source concentrations

| File | Lines | Assessment |
| --- | ---: | --- |
| `src/sync_domain.cpp` | 24,523 | Severe state-machine/persistence monolith |
| `src/reporting_selftests.cpp` | 4,498 | Test/reporting concentration |
| `src/sqlite_replay_ledger.cpp` | 4,340 | Large persistence owner |
| `src/sync_peer_ingress_lifecycle.cpp` | 3,794 | Lifecycle orchestration concentration |
| `include/anonsync_core.hpp` | 3,499 | Very broad public/internal surface |
| `src/sync_sqlite_connection_authority.cpp` | 1,005 | Cohesive but near next split threshold |
| `src/sync_sqlite_mutex_capability.cpp` | 171 | Narrow invariant-owned extraction |

The next splits should follow state ownership and transactional invariants. A
mechanical “500 lines per file” refactor would distribute ambiguity rather than
remove it.

## Remaining historical evidence debt

Older `audit/`, `evidence/`, and `REVISION_EVIDENCE/` trees contain repeated
logs and patches. They are much smaller than the removed build output, but they
still complicate search. A future compaction should preserve one immutable
manifest per revision, deduplicate identical blobs by digest, and move verbose
logs outside production source paths. That migration needs a lineage-aware tool;
manual deletion would destroy useful auditability.
