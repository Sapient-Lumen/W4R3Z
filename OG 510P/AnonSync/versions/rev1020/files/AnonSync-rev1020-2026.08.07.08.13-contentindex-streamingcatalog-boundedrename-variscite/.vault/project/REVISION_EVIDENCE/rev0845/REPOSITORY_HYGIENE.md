# AnonSync rev0845 repository hygiene

- Active implementation projection: 258 files / 17,365,128 bytes.
- Active source delta: 13 files / +1,418 / -255.
- Bundled third-party files changed: 0.
- `LocalJsonlReplayNamespace`: 1,223 lines in rev0844 to 1,125 lines now.
- Extracted directory authority: 456 production lines and 314 direct test lines.
- Local JSONL structural audit: 784 lines / 44 obligations.
- Registered CTest inventory: 141; registered source/architecture audits: 40.
- `REVISION_EVIDENCE` before final indexing: approximately 25.3 MiB.
- First-party `include/src/tests/tools/fuzz`: approximately 6.99 MiB.
- Package excludes `.git`, build trees, binaries, object files, Python caches,
  temporary logs, and cloudtainer work directories.

## Change amplifiers

The largest translation and build units remain:

- `src/sync_domain.cpp`: 15,287 lines;
- `src/sync_domain_selftests.cpp`: 9,348 lines;
- `src/sqlite_replay_ledger.cpp`: 4,527 lines;
- `src/reporting_selftests.cpp`: 4,992 lines; and
- `CMakeLists.txt`: 2,492 lines.

There are 41 `audit_*.py` tools. Two required repair in this revision because
they had captured accidental target adjacency or private-field representation.
This is direct evidence that lexical audits can tax correct refactoring. Retain
them where they pin a currently untyped boundary, but retire them as executable
models, typed owners, and target-graph assertions take over.

Historical evidence is substantially larger than the active first-party
implementation and is copied recursively into each handoff. Content-addressed
storage plus a compact lineage index would preserve auditability while reducing
hashing, manifest, verification, transfer, and review cost.

No bundled third-party source changed in rev0845. The revision deliberately
spends new code on a dependency-light typed owner and direct adversarial tests,
while reducing the composed namespace's internal responsibility.
