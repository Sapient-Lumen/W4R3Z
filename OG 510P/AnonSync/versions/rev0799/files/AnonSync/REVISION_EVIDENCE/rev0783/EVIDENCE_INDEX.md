# rev0783 evidence index

- `AUDIT.md`: mission, corrected severe failures, residual risks, and next sequence.
- `LINEAGE.md` / `LINEAGE.json`: fail-closed rejection of source-less rev0782 and exact rev0778 code parent.
- `SOURCE_DIFF_rev0778_to_rev0783.patch`: implementation/test/tool delta from the immutable parent commit.
- `research/REFERENCES.md`: primary SQLite and POSIX boundary references.
- `audit/`: deterministic source-audit reports and raw JSON output.
- `validation/VALIDATION_SUMMARY.json`: machine-readable required and optional outcomes.
- `validation/COMMANDS.tsv` / `EXIT_CODES.tsv`: command classification, outcomes, and evidence paths.
- `validation/gcc-debug-*`: fresh whole-cube build, 41-test suite, three repetitions, and direct checks.
- `validation/fork-authority-stress100.log`: 3,500 successful adversarial fork checks.
- `validation/gcc-release-*`, `gcc-asan-ubsan-*`, `clang-*`: independent focused build lanes.
- `validation/rev0782-release-package-rejection.json`: executable rejection of the filename-declared parent.
- `validation/COMPILER_DIAGNOSTICS.json`: build-log warning/error inventory.
- `validation/TOOLCHAIN.txt`: exact compiler/build/runtime environment.
