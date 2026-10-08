# Raw fork inventory — rev0833

- Parent: **20 calls** across **13** test translation units.
- Current: **16 calls** across **9** test translation units.
- Production (`src/` + `include/`): **0 calls**.
- Four application/SQLite crash or isolation campaigns now start in fresh self-exec images.
- Fifteen remaining calls are inheritance/lineage probes; one is a reviewed close/dup2/exec bridge pending capture-capable self-exec support.
- This inventory does **not** claim that every legacy inheritance probe has bounded wait ownership; those are explicit follow-up work.

## Fresh-image migrations

| Path | Parent calls | Current calls | Helper |
|---|---:|---:|---|
| `tests/sync_atomic_file_publication_test.cpp` | 1 | 0 | `--anonsync-atomic-publication-writer-helper-v1` |
| `tests/sync_atomic_file_publication_cutpoint_test.cpp` | 1 | 0 | `--anonsync-atomic-publication-crash-helper-v1` |
| `tests/sqlite_runtime_payload_store_test.cpp` | 1 | 0 | `--anonsync-payload-crash-helper-v1` |
| `tests/peer_ingress_schema_attestation_test.cpp` | 1 | 0 | `--anonsync-peer-schema-owner-close-helper-v1` |

## Remaining exact inventory

| Path:line | Class | Next action |
|---|---|---|
| `tests/persistence/sqlite_persistence_process_authority_fork_test.cpp:107` | inherited-process-capability-probe | retain only while inherited capability is the subject; migrate child-local success scenario separately and add bounded waits |
| `tests/persistence/sqlite_persistence_process_authority_fork_test.cpp:131` | inherited-process-capability-probe | retain only while inherited capability is the subject; migrate child-local success scenario separately and add bounded waits |
| `tests/process_incarnation_tests.cpp:178` | process-lineage-micro-oracle | retain raw inheritance but replace blocking pipe/wait ownership with bounded process supervision where compatible |
| `tests/process_incarnation_tests.cpp:208` | process-lineage-micro-oracle | retain raw inheritance but replace blocking pipe/wait ownership with bounded process supervision where compatible |
| `tests/process_incarnation_tests.cpp:213` | process-lineage-micro-oracle | retain raw inheritance but replace blocking pipe/wait ownership with bounded process supervision where compatible |
| `tests/process_incarnation_tests.cpp:239` | process-lineage-micro-oracle | retain raw inheritance but replace blocking pipe/wait ownership with bounded process supervision where compatible |
| `tests/sqlite_connection_authority_test.cpp:1435` | inherited-connection-affinity-probe | retain only the exact inherited-affinity fail-stop path; add bounded kill-and-reap supervision |
| `tests/sqlite_owner_generation_borrow_test.cpp:712` | inherited-owner-generation-probe | retain only inheritance-specific paths; audit thread/fork composition and bound every wait |
| `tests/sqlite_owner_generation_borrow_test.cpp:858` | inherited-owner-generation-probe | retain only inheritance-specific paths; audit thread/fork composition and bound every wait |
| `tests/sqlite_process_authority_fork_test.cpp:115` | inherited-sqlite-authority-probe | retain raw inheritance; reduce post-fork C++ setup and keep exact fail-stop semantics |
| `tests/sqlite_replay_ledger_selftests.cpp:762` | inherited-lock-capability-probe | three intentional inherited lock/gate probes already use bounded kill-and-reap ownership |
| `tests/sqlite_replay_ledger_selftests.cpp:786` | inherited-lock-capability-probe | three intentional inherited lock/gate probes already use bounded kill-and-reap ownership |
| `tests/sqlite_replay_ledger_selftests.cpp:820` | inherited-lock-capability-probe | three intentional inherited lock/gate probes already use bounded kill-and-reap ownership |
| `tests/sqlite_source_first_move_test.cpp:73` | inherited-source-first-probe | retain only if marker semantics require inheritance; add bounded supervision |
| `tests/sqlite_transaction_allocator_fault_test.cpp:732` | minimal-fork-exec-bridge | migrate to a capture-capable SelfExecTestProcess owner; current child is limited to close/dup2/exec/_Exit |
| `tests/sync_atomic_file_publication_prepared_test.cpp:353` | inherited-publication-capability-probe | retained intentionally; child invokes one capability and parent uses bounded monotonic kill-and-reap ownership |

The executable `tools/audit_raw_fork_boundaries.py` fails the CTest gate if the production inventory, remaining test allowlist/counts, four fresh-image migrations, prepared-publication fail-stop, or reviewed fork-exec child shape drifts.
