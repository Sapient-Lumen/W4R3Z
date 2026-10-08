# Rev0815 evidence index

## Handoff and interpretation

- `AUDIT.md` — allocation-window finding, corrected close plan, executable model,
  structural gates, validation, and remaining boundaries.
- `LINEAGE.md` / `LINEAGE.json` — exact verified rev0814 parent.
- `RESEARCH.md` — official SQLite semantics, allocator, VFS, testing, and release
  evidence with design consequences.
- `REPOSITORY_HYGIENE.md`, `TOOLCHAIN.txt`, and `COMMANDS.tsv` — package and
  reproduction controls.

## Exact active-source delta

- `CHANGESET.json`
- `SOURCE_DIFF_rev0814_to_rev0815.patch`
- `SOURCE_NUMSTAT.txt`
- `SOURCE_SHORTSTAT.txt`
- `ACTIVE_IMPLEMENTATION_PROJECTION.json`
- `repository_metrics.json`

## Parent evidence

- `lineage/parent_archive.sha256`
- `lineage/parent-zip-expected-rev0814.json`
- `lineage/parent-zip-expected-rev0814.log`
- `lineage/parent-directory-expected-rev0814.json`
- `lineage/parent-directory-expected-rev0814.log`
- `defect_reproduction/parent-allocation-window-reproduction.json`
- `defect_reproduction/README.md`

## Structural audits

- `audits/sqlite-transaction-exception-composition.json` — 43/43.
- `audits/sqlite-transaction-stack-authority.json` — 86/86.

## Behavioral validation

- `validation/debug-configure.log`
- `validation/debug-all-targets-build.log`
- `validation/final-no-work-build.log`
- `validation/debug-ctest-090.log` — 90/90.
- `validation/focused-build.log`
- `validation/focused-ctest.log`
- `validation/focused-audit-ctest.log`
- `validation/composition-stress-500.log`
- `validation/composition-stress-500.status`
- `validation/focused-asan-ubsan-configure.log`
- `validation/focused-asan-ubsan-build.log`
- `validation/focused-asan-ubsan-ctest.log`
- `validation/focused-asan-ubsan-repeat-10.log`
- `validation/VALIDATION_SUMMARY.json`
