# rev0786 evidence index

- `VALIDATION_SUMMARY.json`: machine-readable required/optional gate result.
- `COMMANDS.tsv`, `EXIT_CODES.tsv`: command ledger and outcomes.
- `gcc-debug-*`: final implementation projection build and full 42-test run.
- `owner-generation-repeat20.log`, `owner-generation-direct.log`: exact mode,
  lifetime, race, thread, and fork evidence; direct count is 258.
- `peer-ingress-lifecycle-repeat5.log`: repeated integration boundary evidence.
- `gcc-asan-ubsan-*`: focused five-test sanitizer lane.
- `clang-cxx20-werror-syntax.log`: independent strict compiler checks for all
  changed C++ translation units.
- `gcc-release-*`: optional optimized lane, including recorded resumptions.
- `COMPILER_DIAGNOSTICS.json`: project/third-party diagnostic classification.
- `ACTIVE_SOURCE_CHECKSUMS.json`: tested active implementation projection.
- `SOURCE_METRICS.json`: active source concentration audit.
- `../audit/`: six deterministic authority reports, stdout/stderr, and exit codes.
- `../SOURCE_DIFF_rev0785_to_rev0786.patch`: complete tracked implementation delta.
- `../research/REFERENCES.md`: first-party SQLite research and project inferences.
