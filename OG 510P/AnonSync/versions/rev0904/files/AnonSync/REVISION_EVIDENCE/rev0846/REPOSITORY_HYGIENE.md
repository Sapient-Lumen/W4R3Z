# AnonSync rev0846 repository hygiene

- Active implementation projection: 262 files / 17,415,088 bytes.
- Active source delta: 24 files / +1,395 / -216.
- Bundled third-party files changed: 0.
- First-party active projection, excluding bundled third party: 257 files /
  7,165,674 bytes, including `.gitignore` and `CMakeLists.txt`.
- Generic thread-incarnation leaf: 200 production lines and 221 direct test
  lines.
- Dedicated thread-incarnation structural audit: 401 lines / 31 obligations.
- Registered CTest inventory: 143; registered source/architecture audits: 41.
- Audit tools: 42 files / 18,307 lines.
- `REVISION_EVIDENCE` before final indexing: approximately 25.7 MB.
- Package excludes `.git`, build trees, binaries, object files, Python caches,
  temporary logs, and cloudtainer work directories.

## Refactor value

The thread allocator and lifetime proof moved out of the SQLite-specific leaf
and now has no SQLite or filesystem dependency. SQLite preserves its public
adapter names while filesystem owners depend directly on the generic type.
Opaque typing forced stale integer assumptions to fail at compile time.

The inherited-process audits now compare independently discovered wrapper users
against one exact 11-target CMake inventory. This closes an actual completeness
blind spot rather than merely adjusting expected counts.

## Change amplifiers

The largest translation and build units remain:

- `src/sync_domain.cpp`: 15,287 lines;
- `src/sync_domain_selftests.cpp`: 9,348 lines;
- `src/sqlite_replay_ledger.cpp`: 4,527 lines;
- `src/reporting_selftests.cpp`: 4,992 lines;
- `CMakeLists.txt`: 2,527 lines; and
- `src/persistence/local_jsonl_replay_namespace.cpp`: 1,146 lines.

The new thread primitive is 200 production lines, while its dedicated test and
audit total 622 lines. Sensitive boundary code deserves disproportionate proof,
but the ratio is also a warning: lexical and build-spelling obligations can
outgrow the implementation they protect. Prefer executable semantics and typed
dependency structure over duplicated source phrases.

The previous fork audits were green while omitting real consumers because their
universe was hand selected. Any audit claiming a complete inventory should
discover candidates independently and prove exact set equality, or derive the
set from authoritative generated metadata.

Historical evidence remains substantially larger than the active first-party
implementation and is copied recursively into each handoff. A content-addressed
store plus compact lineage manifests would preserve auditability while reducing
hashing, verification, transfer, and review cost.
