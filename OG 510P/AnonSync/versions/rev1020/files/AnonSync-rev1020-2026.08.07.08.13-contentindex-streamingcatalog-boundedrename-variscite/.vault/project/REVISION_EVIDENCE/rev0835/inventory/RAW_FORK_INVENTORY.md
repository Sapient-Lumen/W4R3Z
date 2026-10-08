# Raw fork and process-boundary inventory — rev0835

- Production raw forks: **0**
- Test raw forks: **1 in 1 translation unit**
- Shared-owner inherited spawn sites: **13 across 7 consumers**
- Pinned fresh-image campaigns: **7**

## The one raw fork

| Path | Calls | Classification |
|---|---:|---|
| `tests/inherited_test_process.cpp` | 1 | shared test-only owner for exact inherited-state probes |

## Inherited-state consumers

| Path | Spawn sites |
|---|---:|
| `tests/persistence/sqlite_persistence_process_authority_fork_test.cpp` | 2 |
| `tests/process_incarnation_tests.cpp` | 4 |
| `tests/sqlite_owner_generation_borrow_test.cpp` | 1 |
| `tests/sqlite_process_authority_fork_test.cpp` | 1 |
| `tests/sqlite_replay_ledger_selftests.cpp` | 3 |
| `tests/sqlite_source_first_move_test.cpp` | 1 |
| `tests/sync_atomic_file_publication_prepared_test.cpp` | 1 |

## Fresh-image campaigns

- `tests/sync_atomic_file_publication_test.cpp`
- `tests/sync_atomic_file_publication_cutpoint_test.cpp`
- `tests/sqlite_runtime_payload_store_test.cpp`
- `tests/peer_ingress_schema_attestation_test.cpp`
- `tests/sqlite_transaction_allocator_fault_test.cpp`
- `tests/sqlite_connection_authority_test.cpp`
- `tests/sqlite_owner_generation_borrow_test.cpp`

The audit fails if any production call appears, a second raw test call appears, a consumer regains local process choreography, or a fresh-state campaign regresses to raw inheritance.
