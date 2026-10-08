# rev0791 repository hygiene

The source patch is generated against a fresh extraction of the exact supplied
parent archive, not an intermediate work tree. It changes 7 active files:

- `CMakeLists.txt`
- `src/persistence/ingress_sender_replay_record.cpp`
- `src/persistence/ingress_sender_replay_record.hpp`
- `src/sqlite_replay_ledger.cpp`
- `tests/persistence/ingress_sender_replay_record_tests.cpp`
- `tests/sqlite_ingress_sender_replay_integrity_test.cpp`
- `tools/audit_ingress_sender_replay_integrity.py`

No build directories, object files, archives, executables, Python cache files,
VCS metadata, or symlinks are included in the package. Reproducer executables
were run externally and only their source, logs, and exit codes are retained.
Historical evidence files that are empty or oddly named remain untouched;
rewriting them would falsify lineage.
