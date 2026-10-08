# Rev0945 lineage

Parent revision: **rev0944**.

The retained parent archive is
`AnonSync-rev0944-2026.07.29.13.16-batchedadmission-warmverification-wrappertruth-rosebatch.zip`
with SHA-256
`60399cb6147ec167dc1b1af637e7266b7a0bd72de2399326f7912fb186dd0d50`.
Its ZIP CRC and the current wrapper-aware release verifier pass.

Rev0945 reconciles two unfinished descendants of that exact source. The branch
that spread internal segmentation through public configuration was rejected.
The retained implementation contains batch cache promotion, safe detached batch
ownership, payload-cutpoint no-op isolation, exact work segmentation, and the
focused tests/audit. A final audit then releases likely catalog no-ops before
hashing under unrelated exclusive mutation authority.

Changed active implementation files relative to rev0944:

- `CMakeLists.txt`
- `src/anonsync_folder.cpp`
- `src/anonsync_sync.cpp`
- `src/sync_replica_file_payload_store.cpp`
- `src/sync_replica_file_payload_store.hpp`
- `src/sync_replica_folder_scan_owner.cpp`
- `src/sync_replica_folder_scan_owner.hpp`
- `tests/sync_replica_file_payload_store_test.cpp`
- `tests/sync_replica_folder_scan_owner_test.cpp`
- `tools/audit_sync_file_payload_store.py`

Changed restart/history files:

- `BOOTSTRAPROSE.md`
- `README.md`
