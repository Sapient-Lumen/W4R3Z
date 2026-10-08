# Rev0812 evidence index

## Handoff

- `AUDIT.md` — defect, refactor, proof surface, and remaining gaps.
- `LINEAGE.md` / `LINEAGE.json` — exact rev0811 parent and verification.
- `RESEARCH.md` — primary SQLite documentation and design implications.
- `REPOSITORY_HYGIENE.md` — source/package exclusions and inventory.
- `TOOLCHAIN.txt` — compiler, CMake, Ninja, SQLite, and host details.
- `CHANGESET.json` — exact per-active-file source delta.
- `SOURCE_DIFF_rev0811_to_rev0812.patch` — unified active-source patch.
- `ACTIVE_IMPLEMENTATION_PROJECTION.json` — exact active file hashes.
- `repository_metrics.json` — sizes, inventory, and source metrics.

## Behavioral validation

- `validation/all-targets-build.log`
- `validation/final-build-quiescence.log`
- `validation/ctest-inventory.txt`
- `validation/ctest-one-shot-087.log`
- `validation/focused-direct-and-repeat.log`
- `validation/owner-schema-strict-compile.log`
- `validation/owner-schema-focused-asan-ubsan.log`
- `validation/VALIDATION_SUMMARY.json`

The retained `validation/ctest-integration-regression-before-fix.log` is negative
evidence from the first integration attempt. It is not a final release gate.

## Structural audits

- `audits/sync-checkpoint-owner-fence-source-audit.json` and `.log`
- `audits/peer-ingress-schema-owner-generation.json`
- `audits/sqlite-scalar-extraction.json`
- `audits/active-persistence-boundaries.json`
- `audits/runtime-selftest-separation.json`
- `audits/sync-domain-selftest-separation.json`
- `audits/sync-checkpoint-scheduler-separation.json`
- `audits/selftest-registration.json`

## Defect reproduction and build graph

- `defect_reproduction/IF_NOT_EXISTS_SCHEMA_CONFUSION.md`
- `defect_reproduction/if_not_exists_schema_confusion.cpp`
- `defect_reproduction/if_not_exists_schema_confusion.log`
- `build_graph/owner-schema-target-linkage.txt`
