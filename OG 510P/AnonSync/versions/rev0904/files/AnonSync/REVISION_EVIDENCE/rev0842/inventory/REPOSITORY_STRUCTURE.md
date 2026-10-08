# AnonSync rev0842 repository structure

Package working-tree bytes before the evidence index and final manifest: **46922650**.

## Areas

- `src/`: 120 files, 4453150 bytes.
- `include/`: 5 files, 198113 bytes.
- `tests/`: 66 files, 1300358 bytes.
- `tools/`: 43 files, 797773 bytes.
- `audit/`: 34 files, 4608986 bytes.
- `fuzz/`: 5 files, 17201 bytes.
- `third_party/`: 5 files, 10249414 bytes.
- `REVISION_EVIDENCE/`: 2843 files, 24394269 bytes.

## Largest active first-party files

- `src/sync_domain.cpp`: 1122163 bytes, 15287 lines.
- `src/sync_domain_selftests.cpp`: 805483 bytes, 9348 lines.
- `src/reporting_selftests.cpp`: 288345 bytes, 4773 lines.
- `src/sqlite_replay_ledger.cpp`: 266224 bytes, 4527 lines.
- `src/sync_peer_ingress_lifecycle.cpp`: 231599 bytes, 3831 lines.
- `src/runner.cpp`: 211346 bytes, 2543 lines.
- `include/anonsync_core.hpp`: 171116 bytes, 3506 lines.
- `src/sync_peer_ingestion.cpp`: 125996 bytes, 1901 lines.
- `CMakeLists.txt`: 120595 bytes, 2361 lines.
- `src/sync_operator_cli.cpp`: 112465 bytes, 1444 lines.
- `src/sync_sqlite_connection_authority.cpp`: 71860 bytes, 1762 lines.
- `tests/sqlite_connection_authority_test.cpp`: 69490 bytes, 1664 lines.

The 15,287-line domain owner and 9,348-line selftest owner remain the dominant compile and review amplifiers. Rev0842 extracts four dependency-light publication/material leaves but does not claim that the monolith problem is solved.

The current evidence area remains larger than the first-party source area. A content-addressed checkpoint strategy is still recommended.
