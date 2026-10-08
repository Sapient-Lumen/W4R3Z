# Rev0941 lineage

Parent revision: **rev0940**.

The supplied rev0940 ZIP did not have a readable central directory. Rev0941 was
therefore based on the retained extracted rev0940 source tree already present in
the cloudtainer, not on a newly trusted extraction of that archive. The parent
ZIP is not asserted as valid lineage evidence.

Active implementation files changed relative to that retained tree:

- `src/anonsync_replica.cpp`
- `src/anonsync_sync.cpp`
- `src/sync_replica_file_payload_store.cpp`
- `src/sync_replica_file_payload_store.hpp`
- `src/sync_replica_file_tls_server.hpp`
- `src/sync_replica_folder_process.cpp`
- `src/sync_replica_peer_server_owner.cpp`
- `src/sync_replica_reconciliation_protocol.cpp`
- `src/sync_replica_reconciliation_protocol.hpp`
- `src/sync_replica_reconciliation_service.cpp`
- `src/sync_replica_reconciliation_service.hpp`
- `src/sync_replica_reconciliation_tls_exchange.cpp`
- `src/sync_replica_reconciliation_tls_exchange.hpp`
- `src/sync_replica_sqlite_owner.cpp`
- `src/sync_replica_sqlite_owner.hpp`
- `src/sync_replica_sync_once.cpp`
- `tests/sync_replica_file_payload_store_test.cpp`
- `tests/sync_replica_reconciliation_protocol_test.cpp`
- `tests/sync_replica_reconciliation_service_test.cpp`
- `tests/sync_replica_sqlite_owner_test.cpp`
- `tests/sync_replica_tls_transport_test.cpp`
- `tools/audit_sync_file_payload_store.py`
- `tools/test_anonsync_replica_reconciliation_process.py`
