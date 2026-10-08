# Raw `fork()` inventory after rev0831

Rev0831 removes direct post-`fork()` application work from the focused reset and combined reset/receipt crash-frontier executables. It does **not** claim project-wide elimination.

The active C++ tree still contains **22 actual calls in 13 translation units**. Comments that merely discuss `fork()` are excluded.

| File | Calls | Classification | Direction |
|---|---:|---|---|
| `src/sqlite_replay_ledger.cpp` | 5 | `migrate-high` | Production-linked selftest tail performs full lock-holder and restore C++ directly in five raw-fork children; extract selftests and use the self-exec owner. |
| `tests/peer_ingress_schema_attestation_test.cpp` | 1 | `migrate-high` | Child opens SQLite and constructs live schema-attestation C++ after raw fork; encode the owner-close scenario as a versioned self-exec helper. |
| `tests/persistence/sqlite_persistence_process_authority_fork_test.cpp` | 2 | `retain-semantic` | The corpus intentionally proves inherited persistence capabilities fail stopped in a new process incarnation; exec would erase the inherited object under test. |
| `tests/process_incarnation_tests.cpp` | 4 | `retain-semantic` | The corpus directly exercises pthread_atfork/PID fallback and inherited-token behavior, including a fork-of-fork edge; raw fork is the subject of the test. |
| `tests/sqlite_connection_authority_test.cpp` | 1 | `retain-semantic` | The corpus intentionally carries an inherited connection/thread-affinity capability into a child and expects direct fail-stop. |
| `tests/sqlite_owner_generation_borrow_test.cpp` | 2 | `mixed` | Inherited owner/borrow fail-stop cases require raw fork; the isolated close-versus-borrow race can move to self-exec because it creates all SQLite state in the child. |
| `tests/sqlite_process_authority_fork_test.cpp` | 1 | `retain-semantic` | The corpus intentionally proves parent-process SQLite authority cannot be exercised by the fork child. |
| `tests/sqlite_runtime_payload_store_test.cpp` | 1 | `migrate-high` | Child performs full payload-store C++ and SQLite transaction work after raw fork; it should reopen from typed argv/file evidence after exec. |
| `tests/sqlite_source_first_move_test.cpp` | 1 | `retain-semantic` | The marker corpus intentionally exercises destructor/fail-stop behavior of objects inherited across fork; exec would remove that state. |
| `tests/sqlite_transaction_allocator_fault_test.cpp` | 1 | `migrate-medium` | The child immediately performs descriptor plumbing and exec; replace the custom fork/dup2/exec sequence with posix_spawn file actions and bounded ownership. |
| `tests/sync_atomic_file_publication_cutpoint_test.cpp` | 1 | `migrate-high` | Child performs full C++ atomic publication at selected cutpoints after raw fork; use the reusable self-exec process owner and exact cutpoint instruction. |
| `tests/sync_atomic_file_publication_prepared_test.cpp` | 1 | `retain-semantic` | The test intentionally attempts to publish a prepared plan inherited from the parent and proves process-incarnation denial; exec would erase the plan. |
| `tests/sync_atomic_file_publication_test.cpp` | 1 | `migrate-high` | Eight child contenders run full publication C++ after a raw fork; launch versioned self-exec contenders and replace inherited barrier descriptors with an explicit start protocol. |

## Priority order

1. Migrate the five production-linked selftest children in `src/sqlite_replay_ledger.cpp`; they combine the most architectural waste with direct post-fork C++.
2. Migrate payload-store and atomic-publication crash/concurrency children; each creates its own state after fork and therefore gains nothing from inherited C++ memory.
3. Replace the allocator-fault custom fork/dup2/exec shim with `posix_spawn` file actions.
4. Split mixed owner-generation tests so only the genuinely inherited-capability cases retain raw fork.

Raw fork remains justified where the invariant under test is specifically the denial or refresh of **inherited** process-incarnation authority. Those cases still need minimal child-side code and dedicated audits; “semantic” is not a blanket exemption from the async-signal-safety boundary.
