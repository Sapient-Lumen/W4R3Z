# Raw `fork()` inventory — rev0834

Production calls: **0**. Test-only calls: **15 across 8 translation units**.
Every remaining call is an exact allowlisted inherited-state or process-lineage probe. The reviewed fork-exec bridge count is **0**.

| Path | Line | Classification | Next action |
|---|---:|---|---|
| `tests/persistence/sqlite_persistence_process_authority_fork_test.cpp` | 107 | inherited-process-capability-probe | retain only while inherited capability is the subject; migrate child-local success scenarios separately and add bounded waits |
| `tests/persistence/sqlite_persistence_process_authority_fork_test.cpp` | 131 | inherited-process-capability-probe | retain only while inherited capability is the subject; migrate child-local success scenarios separately and add bounded waits |
| `tests/process_incarnation_tests.cpp` | 178 | process-lineage-micro-oracle | retain raw inheritance but replace blocking pipe/wait ownership with bounded process supervision where compatible |
| `tests/process_incarnation_tests.cpp` | 208 | process-lineage-micro-oracle | retain raw inheritance but replace blocking pipe/wait ownership with bounded process supervision where compatible |
| `tests/process_incarnation_tests.cpp` | 213 | process-lineage-micro-oracle | retain raw inheritance but replace blocking pipe/wait ownership with bounded process supervision where compatible |
| `tests/process_incarnation_tests.cpp` | 239 | process-lineage-micro-oracle | retain raw inheritance but replace blocking pipe/wait ownership with bounded process supervision where compatible |
| `tests/sqlite_connection_authority_test.cpp` | 1435 | inherited-connection-affinity-probe | retain only the exact inherited-affinity fail-stop path; add bounded kill-and-reap supervision |
| `tests/sqlite_owner_generation_borrow_test.cpp` | 712 | inherited-owner-generation-probe | retain only inheritance-specific paths; audit thread/fork composition and bound every wait |
| `tests/sqlite_owner_generation_borrow_test.cpp` | 858 | inherited-owner-generation-probe | retain only inheritance-specific paths; audit thread/fork composition and bound every wait |
| `tests/sqlite_process_authority_fork_test.cpp` | 115 | inherited-sqlite-authority-probe | retain raw inheritance; reduce post-fork C++ setup and keep exact fail-stop semantics |
| `tests/sqlite_replay_ledger_selftests.cpp` | 762 | inherited-lock-capability-probe | three intentional inherited lock/gate probes already use bounded kill-and-reap ownership |
| `tests/sqlite_replay_ledger_selftests.cpp` | 786 | inherited-lock-capability-probe | three intentional inherited lock/gate probes already use bounded kill-and-reap ownership |
| `tests/sqlite_replay_ledger_selftests.cpp` | 820 | inherited-lock-capability-probe | three intentional inherited lock/gate probes already use bounded kill-and-reap ownership |
| `tests/sqlite_source_first_move_test.cpp` | 73 | inherited-source-first-probe | retain only if marker semantics require inheritance; add bounded supervision |
| `tests/sync_atomic_file_publication_prepared_test.cpp` | 353 | inherited-publication-capability-probe | retained intentionally; child invokes one capability and parent uses bounded monotonic kill-and-reap ownership |

## Fresh-image campaigns

- `tests/sync_atomic_file_publication_test.cpp` — `--anonsync-atomic-publication-writer-helper-v1` (rev0833)
- `tests/sync_atomic_file_publication_cutpoint_test.cpp` — `--anonsync-atomic-publication-crash-helper-v1` (rev0833)
- `tests/sqlite_runtime_payload_store_test.cpp` — `--anonsync-payload-crash-helper-v1` (rev0833)
- `tests/peer_ingress_schema_attestation_test.cpp` — `--anonsync-peer-schema-owner-close-helper-v1` (rev0833)
- `tests/sqlite_transaction_allocator_fault_test.cpp` — `--anonsync-sqlite-transaction-allocator-fault-worker-v1` (rev0834)

## Claim boundary

The inventory does not claim uniform bounded supervision for the 15 retained inheritance probes. Raw inheritance may be required by the fact under test; blocking parent-side ownership is still a migration target.
