# Rev0814 evidence index

## Handoff

- `AUDIT.md` — corrected defect, typed savepoint owner, refactor, proof, and gaps.
- `LINEAGE.md` / `LINEAGE.json` — exact rev0812 parent and absent-rev0813 disclosure.
- `RESEARCH.md` — primary SQLite semantics and design consequences.
- `CHANGESET.json` / `SOURCE_DIFF_rev0812_to_rev0814.patch` — exact active source delta.
- `ACTIVE_IMPLEMENTATION_PROJECTION.json` — active implementation inventory and hashes.
- `repository_metrics.json`, `TOOLCHAIN.txt`, and `COMMANDS.tsv` — reproducibility metadata.
- `REPOSITORY_HYGIENE.md` and `OPERATIONAL_CORRECTION.md` — package and cloudtainer controls.

## Negative evidence

- `defect_reproduction/` — exact-parent 44/45 catch-and-commit failure and test-only patch.
- `validation/integration-audit-regression-before-fix.log` — 86/88 run that exposed stale audits.

## Final validation

- `validation/fresh-debug-configure.log`
- `validation/fresh-debug-all-targets-build.log`
- `validation/fresh-debug-ctest-088.log`
- `validation/focused-direct.log`
- `validation/focused-repeat-12.log`
- `validation/focused-asan-ubsan-run.log`
- `validation/VALIDATION_SUMMARY.json`

## Structural audits

- `audits/sqlite-transaction-stack-authority.json`
- `audits/sqlite-process-authority.json`
- `audits/sync-checkpoint-owner-fence.json`
