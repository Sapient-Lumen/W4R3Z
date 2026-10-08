# Rev0943 lineage

Parent revision: **rev0942**.

The supplied rev0942 archive passed ZIP CRC validation. A fresh extraction was
compared path-for-path, byte-for-byte, type-for-type, and mode-for-mode against
the retained clean source basis; all 7,099 non-root entries matched. Rev0943 was
consolidated into one canonical source worktree after two unfinished branches
were found to contain complementary implementation and test changes. Final GCC
and Clang gates use only that canonical tree and isolated build directories.

Changed implementation/restart files relative to rev0942:

- `BOOTSTRAPROSE.md`
- `CMakeLists.txt`
- `README.md`
- `src/anonsync_folder.cpp`
- `src/anonsync_replica.cpp`
- `src/anonsync_sync.cpp`
- `src/sync_atomic_file_publication.cpp`
- `src/sync_atomic_file_publication.hpp`
- `src/sync_local_share_setup.cpp`
- `src/sync_posix_descriptor_snapshot.cpp`
- `src/sync_posix_descriptor_snapshot.hpp`
- `src/sync_replica_deployment_manifest.cpp`
- `src/sync_replica_deployment_manifest.hpp`
- `src/sync_replica_file_delivery_protocol.hpp`
- `src/sync_replica_file_payload_store.cpp`
- `src/sync_replica_file_payload_store.hpp`
- `src/sync_replica_folder_scan_owner.cpp`
- `src/sync_replica_folder_scan_owner.hpp`
- `src/sync_replica_peer_server_owner.cpp`
- `src/sync_replica_peer_service_configuration.cpp`
- `src/sync_replica_reconciliation_protocol.cpp`
- `src/sync_replica_reconciliation_protocol.hpp`
- `src/sync_replica_reconciliation_service.cpp`
- `src/sync_replica_sync_once.cpp`
- `tests/sync_atomic_file_publication_test.cpp`
- `tests/sync_bounded_regular_file_test.cpp`
- `tests/sync_replica_deployment_manifest_test.cpp`
- `tests/sync_replica_file_delivery_protocol_test.cpp`
- `tests/sync_replica_file_payload_store_test.cpp`
- `tests/sync_replica_folder_scan_owner_test.cpp`
- `tests/sync_replica_reconciliation_protocol_test.cpp`
- `tests/sync_replica_reconciliation_service_test.cpp`
- `tools/audit_authority_callback_boundaries.py`
- `tools/audit_sync_atomic_file_publication.py`
- `tools/audit_sync_bounded_regular_file.py`
- `tools/audit_sync_effect_root_authority.py`
- `tools/audit_sync_file_payload_store.py`
- `tools/test_anonsync_replica_reconciliation_process.py`
- `tools/test_anonsync_sync_process.py`
