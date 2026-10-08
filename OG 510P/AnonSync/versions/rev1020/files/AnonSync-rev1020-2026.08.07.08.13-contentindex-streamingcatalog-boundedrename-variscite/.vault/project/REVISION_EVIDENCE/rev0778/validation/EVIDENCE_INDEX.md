# rev0778 validation evidence index

This directory is intentionally curated. Redundant incremental attempts and
repeated copies of identical audit JSON were omitted from the release archive.
The retained files preserve every distinct outcome needed to reconstruct the
release decision:

- `final-debug-full-build.log`: raw build interrupted by the explicitly imposed
  35-second observation ceiling.
- `final-debug-full-build-resume.log`: successful continuation of that exact
  build tree.
- `final-debug-full-ctest-clean.log`: fresh complete 40/40 Debug test run.
- `final-debug-full-ctest-repeat3-clean.log`: three complete repetitions,
  totaling 120 passing test executions.
- `final-direct-runtime-checks.log`: six focused executables and their exit
  codes, including 98 authority, 61 support, 38 runtime-policy, 58 schema,
  588 domain-model, and 49 lifecycle checks.
- `gcc-debug-authority-repeat100-current.log`: 100 authority runs, 9,800/9,800
  checks.
- GCC Release, GCC ASan/UBSan, and Clang focused configure/build/test logs.
- `final-audits-status.tsv` plus the canonical JSON reports in `../audit/`.
- toolchain, command, exit-code, warning, summary, and release-gate records.

The source diff, source checksums, lineage proof, audit narrative, research, and
repository-hygiene evidence live one directory above.
