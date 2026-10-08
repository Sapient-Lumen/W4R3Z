# rev0792 repository hygiene

The active source patch is generated against the exact supplied rev0791 archive
and changes seven active files:

- `CMakeLists.txt`
- `src/persistence/sqlite_replay_ledger_schema_contract.cpp`
- `src/persistence/sqlite_replay_ledger_schema_contract.hpp`
- `src/sqlite_replay_ledger.cpp`
- `tests/persistence/sqlite_replay_ledger_schema_contract_tests.cpp`
- `tests/sqlite_replay_ledger_schema_integrity_test.cpp`
- `tools/audit_sqlite_replay_ledger_schema_contract.py`

`README.md`, `REVISION_NOTES_rev0792.md`, `RELEASE_GATE.json`, and rev0792
verification evidence are handoff metadata rather than active implementation.

No build directory, object, archive, executable, database, sidecar, Python cache,
VCS metadata, or symlink is included in the release package. Reproducer binaries
remain external; only source, output, and exit status are retained. Historical
evidence is unchanged even where older files are empty or oddly named, because
rewriting it would falsify lineage.

The refactor removes the large inline schema DDL block from
`sqlite_replay_ledger.cpp`; production C++ count increases by one independently
owned translation unit while the ledger monolith shrinks by about 12.5 KiB.
