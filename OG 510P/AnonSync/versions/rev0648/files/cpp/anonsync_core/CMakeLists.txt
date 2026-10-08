cmake_minimum_required(VERSION 3.20)
project(anonsync_core LANGUAGES CXX)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
find_package(OpenSSL REQUIRED)
find_package(SQLite3 REQUIRED)
option(ANONSYNC_ENABLE_SANITIZERS "Build with AddressSanitizer and UndefinedBehaviorSanitizer when supported" OFF)
set(ANONSYNC_CORE_SOURCES
  src/json_codec_crypto.cpp
  src/contracts_policy_profiles.cpp
  src/normalizer_envelopes.cpp
  src/replay_ledger.cpp
  src/sqlite_replay_ledger.cpp
  src/jwt_policy_decision.cpp
  src/reporting_selftests.cpp
  src/runner.cpp)
add_library(anonsync_core_lib STATIC ${ANONSYNC_CORE_SOURCES})
target_include_directories(anonsync_core_lib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(anonsync_core_lib PUBLIC OpenSSL::Crypto SQLite::SQLite3)
target_compile_options(anonsync_core_lib PRIVATE -Wall -Wextra -Wpedantic)
add_executable(anonsync_core src/anonsync_core.cpp)
target_link_libraries(anonsync_core PRIVATE anonsync_core_lib)
target_compile_options(anonsync_core PRIVATE -Wall -Wextra -Wpedantic)
add_executable(anonsync_fuzz_json_codec fuzz/fuzz_json_codec.cpp)
target_link_libraries(anonsync_fuzz_json_codec PRIVATE anonsync_core_lib)
add_executable(anonsync_fuzz_jwt_codec fuzz/fuzz_jwt_codec.cpp)
target_link_libraries(anonsync_fuzz_jwt_codec PRIVATE anonsync_core_lib)
add_executable(anonsync_fuzz_route_event_ledger fuzz/fuzz_route_event_ledger.cpp)
target_link_libraries(anonsync_fuzz_route_event_ledger PRIVATE anonsync_core_lib)
if(ANONSYNC_ENABLE_SANITIZERS AND CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  foreach(tgt anonsync_core_lib anonsync_core anonsync_fuzz_json_codec anonsync_fuzz_jwt_codec anonsync_fuzz_route_event_ledger)
    target_compile_options(${tgt} PRIVATE -fsanitize=address,undefined -fno-omit-frame-pointer)
    target_link_options(${tgt} PRIVATE -fsanitize=address,undefined)
  endforeach()
endif()
include(CTest)
add_test(NAME anonsync_core_help COMMAND anonsync_core --help)
add_test(NAME anonsync_core_json_parser_boundary_selftest COMMAND anonsync_core --selftest-json-parser)
add_test(NAME anonsync_core_sqlite_wal_verified_claims_selftest COMMAND anonsync_core --selftest-ledger-sqlite-wal)
add_test(NAME anonsync_core_event_identity_replay_selftest COMMAND anonsync_core --selftest-ledger-event-identity-replay)
add_test(NAME anonsync_core_effect_idempotency_selftest COMMAND anonsync_core --selftest-ledger-effect-idempotency)
add_test(NAME anonsync_core_sqlite_effect_transition_selftest COMMAND anonsync_core --selftest-ledger-sqlite-effect-transition)
add_test(NAME anonsync_core_sqlite_effect_pending_recovery_selftest COMMAND anonsync_core --selftest-ledger-sqlite-effect-pending-recovery)
add_test(NAME anonsync_core_sqlite_effect_signed_transition_selftest COMMAND anonsync_core --selftest-ledger-sqlite-effect-signed-transition)
add_test(NAME anonsync_core_sqlite_effect_outbox_claim_selftest COMMAND anonsync_core --selftest-ledger-sqlite-effect-outbox-claim)
add_test(NAME anonsync_core_sqlite_effect_relay_selftest COMMAND anonsync_core --selftest-ledger-sqlite-effect-relay)
add_test(NAME anonsync_core_sqlite_effect_relay_configured_selftest COMMAND anonsync_core --selftest-ledger-sqlite-effect-relay-configured)
add_test(NAME anonsync_core_sqlite_effect_relay_handle_selftest COMMAND anonsync_core --selftest-ledger-sqlite-effect-relay-handle)
add_test(NAME anonsync_core_backend_capability_exact_version_selftest COMMAND anonsync_core --selftest-ledger-backend-capabilities)
add_test(NAME anonsync_core_jwt_codec_fuzz_selftest COMMAND anonsync_core --selftest-fuzz-jwt)
add_test(NAME anonsync_core_route_event_ledger_fuzz_selftest COMMAND anonsync_core --selftest-fuzz-route-event-ledger)
add_test(NAME anonsync_core_sqlite_snapshot_corpus_selftest COMMAND anonsync_core --selftest-ledger-sqlite-snapshot-corpus)
add_test(NAME anonsync_core_sqlite_restore_corpus_selftest COMMAND anonsync_core --selftest-ledger-sqlite-restore-corpus)
add_test(NAME anonsync_core_snapshot_manifest_verifier_selftest COMMAND anonsync_core --selftest-ledger-snapshot-manifest-verifier)
add_test(NAME anonsync_core_sqlite_restore_rollback_guard_selftest COMMAND anonsync_core --selftest-ledger-sqlite-restore-rollback-guard)
add_test(NAME anonsync_core_sqlite_restore_atomicity_selftest COMMAND anonsync_core --selftest-ledger-sqlite-restore-atomicity)
add_test(NAME anonsync_core_sqlite_restore_locking_selftest COMMAND anonsync_core --selftest-ledger-sqlite-restore-locking)
add_test(NAME anonsync_core_sqlite_restore_manifest_binding_selftest COMMAND anonsync_core --selftest-ledger-sqlite-restore-manifest-binding)
add_test(NAME anonsync_core_sqlite_restore_write_gate_selftest COMMAND anonsync_core --selftest-ledger-sqlite-restore-write-gate)
add_test(NAME anonsync_core_sqlite_restore_prefix_continuity_selftest COMMAND anonsync_core --selftest-ledger-sqlite-restore-prefix-continuity)
add_test(NAME anonsync_core_sqlite_readonly_snapshot_verifier_selftest COMMAND anonsync_core --selftest-ledger-sqlite-readonly-snapshot-verifier)
set(ANONSYNC_REPO_ROOT "${CMAKE_CURRENT_SOURCE_DIR}/../..")
if(EXISTS "${ANONSYNC_REPO_ROOT}/fixtures/rev0618/cpp-slim-gateway-context.json")
  add_test(NAME anonsync_core_rev0648_slim_sqlite_stream
    COMMAND anonsync_core
      --controls "${ANONSYNC_REPO_ROOT}/fixtures/rev0618/cpp-slim-gateway-context.json"
      --cases-jsonl "${ANONSYNC_REPO_ROOT}/fixtures/rev0618/cpp-slim-gateway-cases.jsonl"
      --contracts "${ANONSYNC_REPO_ROOT}/gateway/rev0618-cpp-slim-normalization-contract-table.json"
      --ledger "${CMAKE_BINARY_DIR}/rev0648-ctest-ledger.sqlite"
      --ledger-backend sqlite-wal
      --ledger-backend-capabilities "${ANONSYNC_REPO_ROOT}/gateway/rev0648-cpp-ledger-backend-capabilities.json"
      --ledger-reset
      --ledger-commit-mode batch
      --report "${CMAKE_BINARY_DIR}/rev0648-ctest-report.json")
endif()
