# Rev0946 lineage

Parent revision: **rev0945**.

The uploaded parent archive content has SHA-256
`afb7cc8f228c8291863cdf013e1ef6e17cd1d69427480052d57e5b655c19b16d`.
The upload service appended `(1)` to its filename, so the verifier correctly
rejected only the three filename/root-name checks on that renamed copy. An
otherwise byte-identical canonical filename passed all 41 wrapper-aware release
checks, including ZIP CRC, path/type policy, active projection, manifest, and
hidden release binding.

Rev0946 is that exact rev0945 source plus one capacity-composition correction,
focused C++/process regressions, and updated restart/evidence material.

Changed active implementation files relative to rev0945:

- `src/sync_replica_file_content_inventory.hpp`
- `src/sync_replica_file_payload_store.hpp`
- `src/sync_replica_file_payload_store.cpp`
- `src/sync_replica_folder_scan_owner.cpp`
- `src/sync_replica_folder_process.cpp`
- `src/sync_replica_peer_service.cpp`
- `tests/sync_replica_file_payload_store_test.cpp`
- `tests/sync_replica_folder_scan_owner_test.cpp`
- `tools/audit_sync_file_payload_store.py`
- `tools/test_anonsync_service_configuration_status.py`

Changed restart/history files include `BOOTSTRAPROSE.md`, `README.md`,
`REVISION_NOTES_rev0946.md`, `RELEASE_GATE.json`, and this rev0946 evidence
family.
