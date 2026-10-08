# Raw `fork()` inventory

Actual calls: **20** across **13** translation units.
Production calls: **0**. Extracted replay-ledger corpus calls: **3**.

| Path | Line | Classification | Next action |
|---|---:|---|---|
| `tests/peer_ingress_schema_attestation_test.cpp` | 760 | migration-candidate | split inheritance-specific assertions from isolation-only work and migrate the latter to SelfExecTestProcess |
| `tests/persistence/sqlite_persistence_process_authority_fork_test.cpp` | 107 | process-incarnation-or-inherited-object-probe | retain only while raw inheritance is the explicit subject; continue bounded-wait review |
| `tests/persistence/sqlite_persistence_process_authority_fork_test.cpp` | 131 | process-incarnation-or-inherited-object-probe | retain only while raw inheritance is the explicit subject; continue bounded-wait review |
| `tests/process_incarnation_tests.cpp` | 178 | process-incarnation-or-inherited-object-probe | retain only while raw inheritance is the explicit subject; continue bounded-wait review |
| `tests/process_incarnation_tests.cpp` | 208 | process-incarnation-or-inherited-object-probe | retain only while raw inheritance is the explicit subject; continue bounded-wait review |
| `tests/process_incarnation_tests.cpp` | 213 | process-incarnation-or-inherited-object-probe | retain only while raw inheritance is the explicit subject; continue bounded-wait review |
| `tests/process_incarnation_tests.cpp` | 239 | process-incarnation-or-inherited-object-probe | retain only while raw inheritance is the explicit subject; continue bounded-wait review |
| `tests/sqlite_connection_authority_test.cpp` | 1435 | process-incarnation-or-inherited-object-probe | retain only while raw inheritance is the explicit subject; continue bounded-wait review |
| `tests/sqlite_owner_generation_borrow_test.cpp` | 712 | process-incarnation-or-inherited-object-probe | retain only while raw inheritance is the explicit subject; continue bounded-wait review |
| `tests/sqlite_owner_generation_borrow_test.cpp` | 858 | process-incarnation-or-inherited-object-probe | retain only while raw inheritance is the explicit subject; continue bounded-wait review |
| `tests/sqlite_process_authority_fork_test.cpp` | 115 | process-incarnation-or-inherited-object-probe | retain only while raw inheritance is the explicit subject; continue bounded-wait review |
| `tests/sqlite_replay_ledger_selftests.cpp` | 762 | required-inherited-capability-probe | retain while the tested fact is post-fork inherited lock/gate authority; child performs no SQLite open/use |
| `tests/sqlite_replay_ledger_selftests.cpp` | 786 | required-inherited-capability-probe | retain while the tested fact is post-fork inherited lock/gate authority; child performs no SQLite open/use |
| `tests/sqlite_replay_ledger_selftests.cpp` | 820 | required-inherited-capability-probe | retain while the tested fact is post-fork inherited lock/gate authority; child performs no SQLite open/use |
| `tests/sqlite_runtime_payload_store_test.cpp` | 227 | migration-candidate | split inheritance-specific assertions from isolation-only work and migrate the latter to SelfExecTestProcess |
| `tests/sqlite_source_first_move_test.cpp` | 73 | process-incarnation-or-inherited-object-probe | retain only while raw inheritance is the explicit subject; continue bounded-wait review |
| `tests/sqlite_transaction_allocator_fault_test.cpp` | 732 | migration-candidate | split inheritance-specific assertions from isolation-only work and migrate the latter to SelfExecTestProcess |
| `tests/sync_atomic_file_publication_cutpoint_test.cpp` | 649 | migration-candidate | split inheritance-specific assertions from isolation-only work and migrate the latter to SelfExecTestProcess |
| `tests/sync_atomic_file_publication_prepared_test.cpp` | 310 | migration-candidate | split inheritance-specific assertions from isolation-only work and migrate the latter to SelfExecTestProcess |
| `tests/sync_atomic_file_publication_test.cpp` | 254 | migration-candidate | split inheritance-specific assertions from isolation-only work and migrate the latter to SelfExecTestProcess |
