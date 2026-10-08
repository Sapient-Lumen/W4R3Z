# Rev0818 evidence index

- `LINEAGE.*` and `lineage/`: exact sealed rev0817 parent identity and verification.
- `SOURCE_DIFF_rev0817_to_rev0818.patch`, `SOURCE_NUMSTAT.txt`, `SOURCE_SHORTSTAT.txt`, and `CHANGESET.json`: active-source delta.
- `defect_reproduction/`: byte-identical sealed-parent/current intermediate-symlink differential.
- `negative_runs/`: retained failed nested-exception run and its correction.
- `audits/`: 30-check structural publication audit.
- `validation/focused-*`: direct 20-, 28-, and 133-check focused campaigns plus 25 repetitions.
- `validation/full-debug-ctest-j8.log`: complete 96/96 project gate after final active-source changes.
- `validation/gcc-werror-*` and `clang-werror-*`: compiler-diverse warning-as-error lanes.
- `validation/clang-asan-*`: focused ASan/UBSan lane; leak detection disabled.
- `ACTIVE_IMPLEMENTATION_PROJECTION.json`: exact active-source file, byte, and digest inventory.
- `validation/VALIDATION_SUMMARY.json`: machine-readable claims and caveats.
