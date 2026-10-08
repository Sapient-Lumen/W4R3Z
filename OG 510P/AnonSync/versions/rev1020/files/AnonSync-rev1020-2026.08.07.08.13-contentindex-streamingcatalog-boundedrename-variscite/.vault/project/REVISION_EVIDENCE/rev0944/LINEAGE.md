# Rev0944 lineage

Parent revision: **rev0943**.

The supplied rev0943 archive passed ZIP CRC verification and has SHA-256
`8a5908bef2cb409fd369d05ee76ca2088d5ac49a32abd5c983367c435b9badf9`.
Rev0944 starts from its direct canonical source extraction. Two unfinished
rev0944 branches were compared and merged: one implemented exact warm
verification, and one implemented mutation batching plus wrapper-aware release
verification. All publication claims are rerun against one combined source tree
and isolated GCC/Clang build directories.

Changed active implementation files relative to rev0943:

- `src/sync_replica_file_payload_store.cpp`
- `src/sync_replica_file_payload_store.hpp`
- `src/sync_replica_folder_scan_owner.cpp`
- `src/sync_replica_folder_scan_owner.hpp`
- `tests/sync_replica_file_payload_store_test.cpp`
- `tests/sync_replica_folder_scan_owner_test.cpp`
- `tools/audit_sync_file_payload_store.py`
- `tools/test_release_package_path_policy.py`
- `tools/verify_release_package.py`

Changed restart/documentation files:

- `BOOTSTRAPROSE.md`
- `README.md`
