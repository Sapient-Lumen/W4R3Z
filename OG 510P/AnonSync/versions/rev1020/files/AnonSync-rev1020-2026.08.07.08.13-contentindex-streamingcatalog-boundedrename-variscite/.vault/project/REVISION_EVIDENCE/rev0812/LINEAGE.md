# Rev0812 lineage

## Exact parent

Archive:

`AnonSync-rev0811-2026.07.17.01.05-stickyowner-cascadepermit-repairlease-lineagerepair.zip`

SHA-256:

`8d8b873a832281e6c24e5999c44ebdb8624b616c6ad520c122326006f6760fdc`

The archive was verified with `tools/verify_release_package.py` pinned to
`rev0811`: 25/25 checks passed. Its extracted canonical `AnonSync/` directory
was separately verified: 21/21 checks passed.

Rev0812 was edited from that exact extracted source tree. The source comparison
covers the active implementation projection only (`.gitignore`,
`CMakeLists.txt`, `include/`, `src/`, `tests/`, `tools/`, `third_party/`, and
`fuzz/`). No build artifact was used as source. No third-party source changed.

## Exact active delta

- changed active files: 8;
- added lines: 1,849;
- removed lines: 82;
- added production files: `src/sync_checkpoint_owner_schema.hpp/.cpp`;
- added focused test: `tests/sync_checkpoint_owner_schema_test.cpp`;
- modified runtime: `src/sync_checkpoint_owner_fence.cpp`;
- modified build/audits/tests: `CMakeLists.txt`, the focused recipient test, and
  two architecture audit scripts.

The exact patch is
`SOURCE_DIFF_rev0811_to_rev0812.patch`. Per-file hashes and line counts are in
`CHANGESET.json`. The full active projection is in
`ACTIVE_IMPLEMENTATION_PROJECTION.json`.

## Parent verification evidence

- `lineage/parent_archive.sha256`
- `lineage/parent-zip-expected-rev0811.json`
- `lineage/parent-zip-expected-rev0811.log`
- `lineage/parent-directory-expected-rev0811.json`
- `lineage/parent-directory-expected-rev0811.log`
