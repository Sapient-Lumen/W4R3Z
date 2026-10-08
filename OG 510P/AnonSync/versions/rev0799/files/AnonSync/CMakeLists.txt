cmake_minimum_required(VERSION 3.20)
project(anonsync_core LANGUAGES C CXX)
set(CMAKE_C_STANDARD 99)
set(CMAKE_C_STANDARD_REQUIRED ON)
set(CMAKE_C_EXTENSIONS OFF)
set(CMAKE_CXX_STANDARD 20)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
find_package(OpenSSL REQUIRED)
find_package(Threads REQUIRED)
option(ANONSYNC_USE_BUNDLED_SQLITE
  "Build against the reviewed SQLite amalgamation pinned under third_party" ON)
option(ANONSYNC_ENABLE_SANITIZERS "Build with AddressSanitizer and UndefinedBehaviorSanitizer when supported" OFF)
option(ANONSYNC_SANITIZE_BUNDLED_SQLITE
  "Also instrument the pinned SQLite amalgamation (slow; intended for dedicated upstream-boundary jobs)" OFF)
option(ANONSYNC_ENABLE_LIBFUZZER
  "Build the Clang libFuzzer projection-decoder target" OFF)
option(ANONSYNC_LIBFUZZER_WITH_ASAN
  "Add AddressSanitizer to the libFuzzer target (toolchain/runtime dependent)" OFF)

if(ANONSYNC_USE_BUNDLED_SQLITE)
  set(ANONSYNC_BUNDLED_SQLITE_DIR
    ${CMAKE_CURRENT_SOURCE_DIR}/third_party/sqlite-3.53.3)
  file(SHA256 ${ANONSYNC_BUNDLED_SQLITE_DIR}/sqlite3.c
    ANONSYNC_BUNDLED_SQLITE_C_SHA256)
  file(SHA256 ${ANONSYNC_BUNDLED_SQLITE_DIR}/sqlite3.h
    ANONSYNC_BUNDLED_SQLITE_H_SHA256)
  if(NOT ANONSYNC_BUNDLED_SQLITE_C_SHA256 STREQUAL
      "87497ab605bedd0dbee27a209c1eeff8c89b229b13f921a7efdbb81a13f779fd")
    message(FATAL_ERROR
      "Bundled SQLite 3.53.3 sqlite3.c hash mismatch: "
      "${ANONSYNC_BUNDLED_SQLITE_C_SHA256}")
  endif()
  if(NOT ANONSYNC_BUNDLED_SQLITE_H_SHA256 STREQUAL
      "4ff81af4849acabc76fc8349abb926814395072617ca18e08800abf734ab7612")
    message(FATAL_ERROR
      "Bundled SQLite 3.53.3 sqlite3.h hash mismatch: "
      "${ANONSYNC_BUNDLED_SQLITE_H_SHA256}")
  endif()
  message(STATUS
    "Verified bundled SQLite 3.53.3 amalgamation hashes")
  add_library(anonsync_sqlite3 STATIC
    ${ANONSYNC_BUNDLED_SQLITE_DIR}/sqlite3.c)
  target_include_directories(anonsync_sqlite3 PUBLIC
    ${ANONSYNC_BUNDLED_SQLITE_DIR})
  target_compile_definitions(anonsync_sqlite3 PRIVATE
    SQLITE_THREADSAFE=1
    SQLITE_DQS=0
    SQLITE_DEFAULT_FOREIGN_KEYS=1
    SQLITE_DEFAULT_MEMSTATUS=0
    SQLITE_DEFAULT_SYNCHRONOUS=2
    SQLITE_DEFAULT_WAL_SYNCHRONOUS=2
    SQLITE_ENABLE_API_ARMOR
    SQLITE_OMIT_LOAD_EXTENSION
    SQLITE_OMIT_SHARED_CACHE
    SQLITE_SECURE_DELETE=1
    SQLITE_TRUSTED_SCHEMA=0)
  target_link_libraries(anonsync_sqlite3 PUBLIC Threads::Threads ${CMAKE_DL_LIBS})
  set_target_properties(anonsync_sqlite3 PROPERTIES POSITION_INDEPENDENT_CODE ON)
  set(ANONSYNC_SQLITE_TARGET anonsync_sqlite3)
else()
  find_package(SQLite3 REQUIRED)
  set(ANONSYNC_SYSTEM_SQLITE_WAL_RESET_SAFE OFF)
  if(SQLite3_VERSION VERSION_GREATER_EQUAL "3.51.3")
    set(ANONSYNC_SYSTEM_SQLITE_WAL_RESET_SAFE ON)
  elseif(SQLite3_VERSION VERSION_GREATER_EQUAL "3.50.7" AND
         SQLite3_VERSION VERSION_LESS "3.51.0")
    set(ANONSYNC_SYSTEM_SQLITE_WAL_RESET_SAFE ON)
  elseif(SQLite3_VERSION VERSION_GREATER_EQUAL "3.44.6" AND
         SQLite3_VERSION VERSION_LESS "3.45.0")
    set(ANONSYNC_SYSTEM_SQLITE_WAL_RESET_SAFE ON)
  endif()
  if(NOT ANONSYNC_SYSTEM_SQLITE_WAL_RESET_SAFE)
    message(FATAL_ERROR
      "System SQLite ${SQLite3_VERSION} is not known to contain the official "
      "WAL-reset corruption fix. AnonSync refuses an implicit journal-policy "
      "downgrade: use the bundled SQLite profile (default), SQLite 3.51.3+, "
      "SQLite 3.50.7 on the 3.50 branch, or SQLite 3.44.6 on the 3.44 branch.")
  endif()
  set(ANONSYNC_SQLITE_TARGET SQLite::SQLite3)
endif()

# Exact SQLite scalar extraction is a small invariant-owned boundary shared by
# runtime policy, generic support, runner metadata, and replay-ledger recovery.
# It is the only general-purpose location permitted to call sqlite3_column_*
# directly; callers receive byte-exact TEXT/BLOB and exact storage classes.
set(ANONSYNC_SQLITE_EXACT_VALUE_SOURCE
  src/persistence/sqlite_exact_value.cpp)
add_library(anonsync_sqlite_exact_value STATIC
  ${ANONSYNC_SQLITE_EXACT_VALUE_SOURCE})
target_include_directories(anonsync_sqlite_exact_value PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_exact_value PUBLIC
  ${ANONSYNC_SQLITE_TARGET})
target_compile_options(anonsync_sqlite_exact_value PRIVATE
  -Wall -Wextra -Wpedantic)

# Sender-replay evidence is promoted to a durable reservation only after one
# small semantic owner validates every field and its exact prepared-entry
# binding. Keeping this pure C++ boundary outside the replay-ledger monolith
# makes malformed, overflow-edge, and aliasing proofs independently cheap.
set(ANONSYNC_INGRESS_SENDER_REPLAY_RECORD_SOURCE
  src/persistence/ingress_sender_replay_record.cpp)
add_library(anonsync_ingress_sender_replay_record STATIC
  ${ANONSYNC_INGRESS_SENDER_REPLAY_RECORD_SOURCE})
target_include_directories(anonsync_ingress_sender_replay_record PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_compile_options(anonsync_ingress_sender_replay_record PRIVATE
  -Wall -Wextra -Wpedantic)

# Schema shape is durable authority, not merely a list of expected columns.
# One pure owner supplies the exact version-10 CREATE SQL for new ledgers and
# verifies the exact normalized sqlite_schema.sql text before an existing or
# restored database is promoted. This prevents IF NOT EXISTS from laundering a
# weakened schema into writable authority.
set(ANONSYNC_SQLITE_REPLAY_LEDGER_SCHEMA_CONTRACT_SOURCE
  src/persistence/sqlite_replay_ledger_schema_contract.cpp)
add_library(anonsync_sqlite_replay_ledger_schema_contract STATIC
  ${ANONSYNC_SQLITE_REPLAY_LEDGER_SCHEMA_CONTRACT_SOURCE})
target_include_directories(anonsync_sqlite_replay_ledger_schema_contract PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_compile_options(anonsync_sqlite_replay_ledger_schema_contract PRIVATE
  -Wall -Wextra -Wpedantic)

# SQLite pathname identity and no-symlink family traversal are shared security
# infrastructure, not an implementation detail of the core monolith.  Keeping
# this owner separately linkable lets snapshot sealing and focused adversarial
# tests use the exact production path checks without compiling sync_domain.cpp.
set(ANONSYNC_SQLITE_PATH_SECURITY_SOURCE
  src/sqlite_path_security.cpp)
add_library(anonsync_sqlite_path_security STATIC
  ${ANONSYNC_SQLITE_PATH_SECURITY_SOURCE})
target_include_directories(anonsync_sqlite_path_security PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sqlite_path_security PUBLIC
  ${ANONSYNC_SQLITE_TARGET})
target_compile_options(anonsync_sqlite_path_security PRIVATE
  -Wall -Wextra -Wpedantic)

# Raw SQLite header fields become authority only after one pure boundary proves
# canonical file geometry: valid current page-count evidence and an exact
# page_count * page_size == descriptor_bytes relationship.  Keeping this logic
# separate makes trailing-byte and stale-header proofs independent of OpenSSL,
# the filesystem, and the core monolith.
set(ANONSYNC_SQLITE_SNAPSHOT_GEOMETRY_SOURCE
  src/persistence/sqlite_snapshot_geometry.cpp)
add_library(anonsync_sqlite_snapshot_geometry STATIC
  ${ANONSYNC_SQLITE_SNAPSHOT_GEOMETRY_SOURCE})
target_include_directories(anonsync_sqlite_snapshot_geometry PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_compile_options(anonsync_sqlite_snapshot_geometry PRIVATE
  -Wall -Wextra -Wpedantic)


# A sealed byte/page extent does not bound SQLite execution or C++ projection.
# This independently linked lifetime owner installs the sole progress handler
# on a hostile-snapshot connection and enforces monotone work, row, decoded-byte,
# retained-byte, and wall-clock ceilings without depending on the core monolith.
set(ANONSYNC_SQLITE_VERIFICATION_BUDGET_SOURCE
  src/persistence/sqlite_verification_budget.cpp)
add_library(anonsync_sqlite_verification_budget STATIC
  ${ANONSYNC_SQLITE_VERIFICATION_BUDGET_SOURCE})
target_include_directories(anonsync_sqlite_verification_budget PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_verification_budget PUBLIC
  ${ANONSYNC_SQLITE_TARGET})
target_compile_options(anonsync_sqlite_verification_budget PRIVATE
  -Wall -Wextra -Wpedantic)

# An untrusted snapshot pathname is copied once into a private, byte-hashed,
# sidecar-free staging object and opened only via SQLite immutable mode.  The
# digest verifier, logical verifier, continuity guard, and restore backup all
# consume that same process-local seal rather than independently reopening a
# mutable pathname. Geometry is proven before staging and re-proven on the
# private copy and retained descriptor.
set(ANONSYNC_SQLITE_SNAPSHOT_SEAL_SOURCE
  src/persistence/sqlite_snapshot_seal.cpp)
add_library(anonsync_sqlite_snapshot_seal STATIC
  ${ANONSYNC_SQLITE_SNAPSHOT_SEAL_SOURCE})
target_include_directories(anonsync_sqlite_snapshot_seal PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_snapshot_seal PUBLIC
  anonsync_sqlite_snapshot_geometry
  anonsync_sqlite_path_security
  OpenSSL::Crypto
  ${ANONSYNC_SQLITE_TARGET})
target_compile_options(anonsync_sqlite_snapshot_seal PRIVATE
  -Wall -Wextra -Wpedantic)

add_library(anonsync_sqlite_runtime STATIC src/sync_sqlite_runtime.cpp)
target_include_directories(anonsync_sqlite_runtime PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sqlite_runtime PUBLIC
  anonsync_sqlite_exact_value
  ${ANONSYNC_SQLITE_TARGET})
target_compile_options(anonsync_sqlite_runtime PRIVATE -Wall -Wextra -Wpedantic)
if(ANONSYNC_USE_BUNDLED_SQLITE)
  target_compile_definitions(anonsync_sqlite_runtime PRIVATE ANONSYNC_BUNDLED_SQLITE=1)
endif()

# The peer-ingress durable-connection verifier is an invariant-owned boundary,
# not an implementation detail of the monolithic domain archive.  Keep it as a
# separately linkable library so its focused proof never has to compile the
# 24k-line sync domain or unrelated transports, ledgers, codecs, and reports.
set(ANONSYNC_PEER_INGRESS_CONNECTION_PROFILE_SOURCE
  src/persistence/peer_ingress_connection_profile.cpp)
add_library(anonsync_peer_ingress_connection_profile STATIC
  ${ANONSYNC_PEER_INGRESS_CONNECTION_PROFILE_SOURCE})
target_include_directories(anonsync_peer_ingress_connection_profile PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_peer_ingress_connection_profile PUBLIC
  ${ANONSYNC_SQLITE_TARGET})
target_compile_options(anonsync_peer_ingress_connection_profile PRIVATE
  -Wall -Wextra -Wpedantic)

# Canonical projection comparison is a pure evidence boundary.  The focused
# proof should compile only this implementation, not the whole application.
set(ANONSYNC_CANONICAL_PROJECTION_VERIFIER_SOURCE
  src/persistence/canonical_projection_verifier.cpp)
add_library(anonsync_canonical_projection_verifier STATIC
  ${ANONSYNC_CANONICAL_PROJECTION_VERIFIER_SOURCE})
target_include_directories(anonsync_canonical_projection_verifier PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_compile_options(anonsync_canonical_projection_verifier PRIVATE
  -Wall -Wextra -Wpedantic)

# SQLite projection decoding owns column-map and field semantics while routing
# all scalar conversion through the exact-value boundary. Keeping this slice
# independently linkable makes malformed-row testing cheap and exact without
# creating a second raw sqlite3_column_* authority.
set(ANONSYNC_SQLITE_PROJECTION_DECODER_SOURCE
  src/persistence/sqlite_projection_decoder.cpp)
add_library(anonsync_sqlite_projection_decoder STATIC
  ${ANONSYNC_SQLITE_PROJECTION_DECODER_SOURCE})
target_include_directories(anonsync_sqlite_projection_decoder PUBLIC
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_projection_decoder PUBLIC
  anonsync_canonical_projection_verifier
  anonsync_sqlite_exact_value)
target_compile_options(anonsync_sqlite_projection_decoder PRIVATE
  -Wall -Wextra -Wpedantic)

# One independently testable ownership and statement boundary is shared by
# the checkpoint and peer-ingress domains. Keeping it outside either large
# translation unit prevents another private helper copy from becoming an
# accidental source of divergent transaction semantics.
add_library(anonsync_sqlite_support STATIC
  src/sync_sqlite_support.cpp
  src/sync_sqlite_process_incarnation.cpp
  src/sync_sqlite_handle_slot.cpp
  src/sync_sqlite_mutex_capability.cpp
  src/sync_sqlite_transaction.cpp
  src/sync_sqlite_connection_authority.cpp)
target_include_directories(anonsync_sqlite_support PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sqlite_support PUBLIC
  anonsync_sqlite_runtime
  anonsync_sqlite_exact_value)
target_compile_options(anonsync_sqlite_support PRIVATE -Wall -Wextra -Wpedantic)

set(ANONSYNC_CORE_SOURCES
  src/sync_domain.cpp
  src/sync_peer_ingress_projection.cpp
  src/sync_peer_ingress_lifecycle.cpp
  src/sync_peer_ingress_schema.cpp
  src/sync_peer_ingress_wire.cpp
  src/sync_peer_wire_codec.cpp
  src/sync_peer_ingress_payload_store.cpp
  src/sync_peer_ingress_retention.cpp
  src/sync_peer_ingress_claim.cpp
  src/sync_peer_ingress_reconciliation.cpp
  src/sync_sqlite_schema_identity.cpp
  src/sync_operator_cli.cpp
  src/sync_peer_ingestion.cpp
  src/sync_peer_local_transport.cpp
  src/json_codec_crypto.cpp
  src/contracts_policy_profiles.cpp
  src/normalizer_envelopes.cpp
  src/replay_ledger.cpp
  src/sqlite_replay_ledger.cpp
  src/jwt_policy_decision.cpp
  src/reporting_selftests.cpp
  src/runner.cpp)
foreach(ANONSYNC_INVARIANT_OWNED_SOURCE
    "${ANONSYNC_PEER_INGRESS_CONNECTION_PROFILE_SOURCE}"
    "${ANONSYNC_SQLITE_EXACT_VALUE_SOURCE}"
    "${ANONSYNC_INGRESS_SENDER_REPLAY_RECORD_SOURCE}"
    "${ANONSYNC_SQLITE_REPLAY_LEDGER_SCHEMA_CONTRACT_SOURCE}"
    "${ANONSYNC_SQLITE_PATH_SECURITY_SOURCE}"
    "${ANONSYNC_SQLITE_SNAPSHOT_GEOMETRY_SOURCE}"
    "${ANONSYNC_SQLITE_VERIFICATION_BUDGET_SOURCE}"
    "${ANONSYNC_SQLITE_SNAPSHOT_SEAL_SOURCE}"
    "${ANONSYNC_CANONICAL_PROJECTION_VERIFIER_SOURCE}"
    "${ANONSYNC_SQLITE_PROJECTION_DECODER_SOURCE}")
  list(FIND ANONSYNC_CORE_SOURCES "${ANONSYNC_INVARIANT_OWNED_SOURCE}"
    ANONSYNC_INVARIANT_SOURCE_IN_CORE_INDEX)
  if(NOT ANONSYNC_INVARIANT_SOURCE_IN_CORE_INDEX EQUAL -1)
    message(FATAL_ERROR
      "invariant-owned persistence boundary must remain outside anonsync_core_lib: ${ANONSYNC_INVARIANT_OWNED_SOURCE}")
  endif()
endforeach()
add_library(anonsync_core_lib STATIC ${ANONSYNC_CORE_SOURCES})
target_include_directories(anonsync_core_lib PUBLIC ${CMAKE_CURRENT_SOURCE_DIR}/include)
target_link_libraries(anonsync_core_lib
  PUBLIC OpenSSL::Crypto anonsync_sqlite_support
  PRIVATE
    anonsync_peer_ingress_connection_profile
    anonsync_sqlite_exact_value
    anonsync_ingress_sender_replay_record
    anonsync_sqlite_replay_ledger_schema_contract
    anonsync_sqlite_path_security
    anonsync_sqlite_snapshot_geometry
    anonsync_sqlite_verification_budget
    anonsync_sqlite_snapshot_seal
    anonsync_canonical_projection_verifier
    anonsync_sqlite_projection_decoder)
if(ANONSYNC_USE_BUNDLED_SQLITE)
  target_compile_definitions(anonsync_core_lib PRIVATE ANONSYNC_BUNDLED_SQLITE=1)
endif()
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

# The three legacy fuzz-named binaries above are deterministic corpus
# selftests. This is the first actual coverage-guided fuzz target: it exercises
# SQLite row state, storage classes, malformed/aliased column maps, embedded
# bytes, and the value-free decoder error surface. Compile the three small
# boundary implementations directly so the fuzz lane instruments
# them without forcing sanitizer runtimes into every normal consumer of their
# static libraries.
if(ANONSYNC_ENABLE_LIBFUZZER)
  if(NOT CMAKE_CXX_COMPILER_ID MATCHES "Clang")
    message(FATAL_ERROR
      "ANONSYNC_ENABLE_LIBFUZZER requires a matching Clang/libFuzzer toolchain")
  endif()
  add_executable(anonsync_fuzz_sqlite_projection_decoder
    fuzz/fuzz_sqlite_projection_decoder.cpp
    ${ANONSYNC_SQLITE_EXACT_VALUE_SOURCE}
    ${ANONSYNC_CANONICAL_PROJECTION_VERIFIER_SOURCE}
    ${ANONSYNC_SQLITE_PROJECTION_DECODER_SOURCE})
  target_include_directories(anonsync_fuzz_sqlite_projection_decoder PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
  target_link_libraries(anonsync_fuzz_sqlite_projection_decoder PRIVATE
    ${ANONSYNC_SQLITE_TARGET})
  set(ANONSYNC_LIBFUZZER_SANITIZERS "fuzzer,undefined")
  if(ANONSYNC_LIBFUZZER_WITH_ASAN)
    set(ANONSYNC_LIBFUZZER_SANITIZERS "fuzzer,address,undefined")
  endif()
  target_compile_options(anonsync_fuzz_sqlite_projection_decoder PRIVATE
    -Wall -Wextra -Wpedantic -Werror
    -fsanitize=${ANONSYNC_LIBFUZZER_SANITIZERS}
    -fno-omit-frame-pointer -D_GLIBCXX_ASSERTIONS)
  target_link_options(anonsync_fuzz_sqlite_projection_decoder PRIVATE
    -fsanitize=${ANONSYNC_LIBFUZZER_SANITIZERS})

  # A second real fuzz boundary explores the 100-byte SQLite header, stale
  # page-count evidence, exact file extents, and caller-tightenable hard caps.
  # Compile the pure owner directly so coverage is not diluted by the core.
  add_executable(anonsync_fuzz_sqlite_snapshot_geometry
    fuzz/fuzz_sqlite_snapshot_geometry.cpp
    ${ANONSYNC_SQLITE_SNAPSHOT_GEOMETRY_SOURCE})
  target_include_directories(anonsync_fuzz_sqlite_snapshot_geometry PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
  target_compile_options(anonsync_fuzz_sqlite_snapshot_geometry PRIVATE
    -Wall -Wextra -Wpedantic -Werror
    -fsanitize=${ANONSYNC_LIBFUZZER_SANITIZERS}
    -fno-omit-frame-pointer -D_GLIBCXX_ASSERTIONS)
  target_link_options(anonsync_fuzz_sqlite_snapshot_geometry PRIVATE
    -fsanitize=${ANONSYNC_LIBFUZZER_SANITIZERS})
endif()
add_executable(anonsync_sqlite_exact_value_test
  tests/persistence/sqlite_exact_value_tests.cpp)
target_include_directories(anonsync_sqlite_exact_value_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_exact_value_test PRIVATE
  anonsync_sqlite_exact_value)
target_compile_options(anonsync_sqlite_exact_value_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_ingress_sender_replay_record_test
  tests/persistence/ingress_sender_replay_record_tests.cpp)
target_include_directories(anonsync_ingress_sender_replay_record_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_ingress_sender_replay_record_test PRIVATE
  anonsync_ingress_sender_replay_record)
target_compile_options(anonsync_ingress_sender_replay_record_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_replay_ledger_schema_contract_test
  tests/persistence/sqlite_replay_ledger_schema_contract_tests.cpp)
target_include_directories(anonsync_sqlite_replay_ledger_schema_contract_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_replay_ledger_schema_contract_test PRIVATE
  anonsync_sqlite_replay_ledger_schema_contract)
target_compile_options(anonsync_sqlite_replay_ledger_schema_contract_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_replay_ledger_schema_integrity_test
  tests/sqlite_replay_ledger_schema_integrity_test.cpp)
target_link_libraries(anonsync_sqlite_replay_ledger_schema_integrity_test PRIVATE
  anonsync_core_lib
  anonsync_sqlite_snapshot_seal)
target_include_directories(anonsync_sqlite_replay_ledger_schema_integrity_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_compile_options(anonsync_sqlite_replay_ledger_schema_integrity_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_snapshot_seal_test
  tests/persistence/sqlite_snapshot_seal_tests.cpp)
target_include_directories(anonsync_sqlite_snapshot_seal_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_snapshot_seal_test PRIVATE
  anonsync_sqlite_snapshot_seal)
target_compile_options(anonsync_sqlite_snapshot_seal_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_snapshot_geometry_test
  tests/persistence/sqlite_snapshot_geometry_tests.cpp)
target_include_directories(anonsync_sqlite_snapshot_geometry_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_snapshot_geometry_test PRIVATE
  anonsync_sqlite_snapshot_geometry)
target_compile_options(anonsync_sqlite_snapshot_geometry_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_verification_budget_test
  tests/persistence/sqlite_verification_budget_tests.cpp)
target_include_directories(anonsync_sqlite_verification_budget_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_verification_budget_test PRIVATE
  anonsync_sqlite_verification_budget)
target_compile_options(anonsync_sqlite_verification_budget_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_snapshot_geometry_binding_test
  tests/persistence/sqlite_snapshot_geometry_binding_test.cpp)
target_include_directories(anonsync_sqlite_snapshot_geometry_binding_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_snapshot_geometry_binding_test PRIVATE
  anonsync_sqlite_snapshot_seal)
target_compile_options(anonsync_sqlite_snapshot_geometry_binding_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_snapshot_sidecar_binding_test
  tests/sqlite_snapshot_sidecar_binding_test.cpp)
target_link_libraries(anonsync_sqlite_snapshot_sidecar_binding_test PRIVATE
  anonsync_core_lib)
target_compile_options(anonsync_sqlite_snapshot_sidecar_binding_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_ingress_sender_replay_integrity_test
  tests/sqlite_ingress_sender_replay_integrity_test.cpp)
target_link_libraries(anonsync_sqlite_ingress_sender_replay_integrity_test PRIVATE
  anonsync_core_lib)
target_compile_options(anonsync_sqlite_ingress_sender_replay_integrity_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_runtime_policy_test tests/sqlite_runtime_policy_test.cpp)
target_link_libraries(anonsync_sqlite_runtime_policy_test PRIVATE anonsync_sqlite_runtime)
target_compile_options(anonsync_sqlite_runtime_policy_test PRIVATE -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_support_test tests/sqlite_support_test.cpp)
target_link_libraries(anonsync_sqlite_support_test PRIVATE anonsync_sqlite_support)
target_compile_options(anonsync_sqlite_support_test PRIVATE -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_connection_authority_test
  tests/sqlite_connection_authority_test.cpp)
target_include_directories(anonsync_sqlite_connection_authority_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sqlite_connection_authority_test PRIVATE
  anonsync_sqlite_support)
target_compile_options(anonsync_sqlite_connection_authority_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_process_authority_fork_test
  tests/sqlite_process_authority_fork_test.cpp)
target_include_directories(anonsync_sqlite_process_authority_fork_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sqlite_process_authority_fork_test PRIVATE
  anonsync_sqlite_support)
target_compile_options(anonsync_sqlite_process_authority_fork_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_owner_generation_borrow_test
  tests/sqlite_owner_generation_borrow_test.cpp)
target_include_directories(anonsync_sqlite_owner_generation_borrow_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sqlite_owner_generation_borrow_test PRIVATE
  anonsync_sqlite_support)
target_compile_options(anonsync_sqlite_owner_generation_borrow_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sync_peer_ingress_wire_test
  tests/sync_peer_ingress_wire_test.cpp)
target_include_directories(anonsync_sync_peer_ingress_wire_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_sync_peer_ingress_wire_test PRIVATE anonsync_core_lib)
target_compile_options(anonsync_sync_peer_ingress_wire_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_peer_ingress_wire_adversarial_test
  tests/sync_peer_ingress_wire_adversarial_test.cpp)
target_include_directories(anonsync_peer_ingress_wire_adversarial_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/tests)
target_link_libraries(anonsync_peer_ingress_wire_adversarial_test PRIVATE
  anonsync_core_lib)
target_compile_options(anonsync_peer_ingress_wire_adversarial_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sync_peer_wire_compatibility_test
  tests/sync_peer_wire_compatibility_test.cpp)
target_include_directories(anonsync_sync_peer_wire_compatibility_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/tests)
target_link_libraries(anonsync_sync_peer_wire_compatibility_test PRIVATE
  anonsync_core_lib)
target_compile_options(anonsync_sync_peer_wire_compatibility_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_runtime_payload_store_test
  tests/sqlite_runtime_payload_store_test.cpp)
target_include_directories(anonsync_sqlite_runtime_payload_store_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/tests)
target_link_libraries(anonsync_sqlite_runtime_payload_store_test PRIVATE
  anonsync_core_lib)
target_compile_options(anonsync_sqlite_runtime_payload_store_test PRIVATE
  -Wall -Wextra -Wpedantic)
if(ANONSYNC_USE_BUNDLED_SQLITE)
  target_compile_definitions(anonsync_sqlite_runtime_payload_store_test PRIVATE
    ANONSYNC_BUNDLED_SQLITE=1)
endif()
add_executable(anonsync_canonical_projection_verifier_test
  tests/persistence/canonical_projection_verifier_tests.cpp)
target_include_directories(anonsync_canonical_projection_verifier_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_canonical_projection_verifier_test PRIVATE
  anonsync_canonical_projection_verifier)
target_compile_options(anonsync_canonical_projection_verifier_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_sqlite_projection_decoder_test
  tests/persistence/sqlite_projection_decoder_tests.cpp)
target_include_directories(anonsync_sqlite_projection_decoder_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/src/persistence)
target_link_libraries(anonsync_sqlite_projection_decoder_test PRIVATE
  anonsync_sqlite_projection_decoder)
target_compile_options(anonsync_sqlite_projection_decoder_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_peer_ingress_projection_integrity_test
  tests/peer_ingress_projection_integrity_test.cpp)
target_include_directories(anonsync_peer_ingress_projection_integrity_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/tests)
target_link_libraries(anonsync_peer_ingress_projection_integrity_test PRIVATE
  anonsync_core_lib)
target_compile_options(anonsync_peer_ingress_projection_integrity_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_peer_ingress_retention_integrity_test
  tests/peer_ingress_retention_integrity_test.cpp)
target_include_directories(anonsync_peer_ingress_retention_integrity_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src
  ${CMAKE_CURRENT_SOURCE_DIR}/tests)
target_link_libraries(anonsync_peer_ingress_retention_integrity_test PRIVATE
  anonsync_core_lib)
target_compile_options(anonsync_peer_ingress_retention_integrity_test PRIVATE
  -Wall -Wextra -Wpedantic)
add_executable(anonsync_peer_ingress_schema_attestation_test
  tests/peer_ingress_schema_attestation_test.cpp)
target_include_directories(anonsync_peer_ingress_schema_attestation_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_peer_ingress_schema_attestation_test PRIVATE
  anonsync_core_lib)
target_compile_options(anonsync_peer_ingress_schema_attestation_test PRIVATE
  -Wall -Wextra -Wpedantic)
# rev0789: independently compiled and executable proof for the durable,
# exact-VFS peer-ingress connection publication boundary.  Linking this test
# back through anonsync_core_lib would silently restore the 26-translation-unit
# dependency fan-out that this boundary exists to eliminate.
add_executable(anonsync_peer_ingress_connection_profile_test
  tests/persistence/peer_ingress_connection_profile_test.cpp)
target_include_directories(anonsync_peer_ingress_connection_profile_test PRIVATE
  ${CMAKE_CURRENT_SOURCE_DIR}/src)
target_link_libraries(anonsync_peer_ingress_connection_profile_test PRIVATE
  anonsync_peer_ingress_connection_profile)
target_compile_options(anonsync_peer_ingress_connection_profile_test PRIVATE
  -Wall -Wextra -Wpedantic)
get_target_property(ANONSYNC_PROFILE_TEST_LINK_LIBRARIES
  anonsync_peer_ingress_connection_profile_test LINK_LIBRARIES)
list(FIND ANONSYNC_PROFILE_TEST_LINK_LIBRARIES anonsync_core_lib
  ANONSYNC_PROFILE_TEST_CORE_LINK_INDEX)
if(NOT ANONSYNC_PROFILE_TEST_CORE_LINK_INDEX EQUAL -1)
  message(FATAL_ERROR
    "focused connection-profile proof must not link anonsync_core_lib")
endif()
get_target_property(ANONSYNC_PROFILE_LIBRARY_LINK_LIBRARIES
  anonsync_peer_ingress_connection_profile LINK_LIBRARIES)
list(FIND ANONSYNC_PROFILE_LIBRARY_LINK_LIBRARIES anonsync_core_lib
  ANONSYNC_PROFILE_LIBRARY_CORE_LINK_INDEX)
if(NOT ANONSYNC_PROFILE_LIBRARY_CORE_LINK_INDEX EQUAL -1)
  message(FATAL_ERROR
    "connection-profile library must not depend on anonsync_core_lib")
endif()

foreach(ANONSYNC_FOCUSED_BOUNDARY_TARGET
    anonsync_sqlite_exact_value
    anonsync_sqlite_exact_value_test
    anonsync_ingress_sender_replay_record
    anonsync_ingress_sender_replay_record_test
    anonsync_sqlite_replay_ledger_schema_contract
    anonsync_sqlite_replay_ledger_schema_contract_test
    anonsync_sqlite_path_security
    anonsync_sqlite_snapshot_geometry
    anonsync_sqlite_snapshot_geometry_test
    anonsync_sqlite_verification_budget
    anonsync_sqlite_verification_budget_test
    anonsync_sqlite_snapshot_seal
    anonsync_sqlite_snapshot_seal_test
    anonsync_sqlite_snapshot_geometry_binding_test
    anonsync_canonical_projection_verifier
    anonsync_sqlite_projection_decoder
    anonsync_canonical_projection_verifier_test
    anonsync_sqlite_projection_decoder_test)
  get_target_property(ANONSYNC_FOCUSED_BOUNDARY_LINK_LIBRARIES
    ${ANONSYNC_FOCUSED_BOUNDARY_TARGET} LINK_LIBRARIES)
  list(FIND ANONSYNC_FOCUSED_BOUNDARY_LINK_LIBRARIES anonsync_core_lib
    ANONSYNC_FOCUSED_BOUNDARY_CORE_LINK_INDEX)
  if(NOT ANONSYNC_FOCUSED_BOUNDARY_CORE_LINK_INDEX EQUAL -1)
    message(FATAL_ERROR
      "focused persistence boundary must not depend on anonsync_core_lib: ${ANONSYNC_FOCUSED_BOUNDARY_TARGET}")
  endif()
endforeach()
if(ANONSYNC_ENABLE_SANITIZERS AND CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
  set(ANONSYNC_SANITIZER_COMPILE_TARGETS
    anonsync_core_lib
    anonsync_peer_ingress_connection_profile
    anonsync_sqlite_exact_value
    anonsync_ingress_sender_replay_record
    anonsync_sqlite_replay_ledger_schema_contract
    anonsync_sqlite_path_security
    anonsync_sqlite_snapshot_geometry
    anonsync_sqlite_verification_budget
    anonsync_sqlite_snapshot_seal
    anonsync_canonical_projection_verifier
    anonsync_sqlite_projection_decoder
    anonsync_sqlite_runtime
    anonsync_sqlite_support
    anonsync_sqlite_exact_value_test
    anonsync_ingress_sender_replay_record_test
    anonsync_sqlite_replay_ledger_schema_contract_test
    anonsync_sqlite_snapshot_geometry_test
    anonsync_sqlite_verification_budget_test
    anonsync_sqlite_snapshot_seal_test
    anonsync_sqlite_snapshot_geometry_binding_test
    anonsync_sqlite_snapshot_sidecar_binding_test
    anonsync_sqlite_replay_ledger_schema_integrity_test
    anonsync_sqlite_ingress_sender_replay_integrity_test
    anonsync_sqlite_runtime_policy_test
    anonsync_sqlite_support_test
    anonsync_sqlite_connection_authority_test
    anonsync_sqlite_process_authority_fork_test
    anonsync_sqlite_owner_generation_borrow_test
    anonsync_core
    anonsync_fuzz_json_codec
    anonsync_fuzz_jwt_codec
    anonsync_fuzz_route_event_ledger
    anonsync_sync_peer_ingress_wire_test
    anonsync_peer_ingress_wire_adversarial_test
    anonsync_sync_peer_wire_compatibility_test
    anonsync_sqlite_runtime_payload_store_test
    anonsync_canonical_projection_verifier_test
    anonsync_sqlite_projection_decoder_test
    anonsync_peer_ingress_projection_integrity_test
    anonsync_peer_ingress_retention_integrity_test
    anonsync_peer_ingress_schema_attestation_test
    anonsync_peer_ingress_connection_profile_test)
  # Keep the multi-megabyte reviewed amalgamation out of the default C++
  # sanitizer lane. Instrumenting it dominates cloud builds and can prevent
  # the AnonSync ownership code from being exercised at all. A dedicated job
  # can still opt in when auditing the third-party boundary itself.
  if(TARGET anonsync_sqlite3 AND ANONSYNC_SANITIZE_BUNDLED_SQLITE)
    list(APPEND ANONSYNC_SANITIZER_COMPILE_TARGETS anonsync_sqlite3)
  endif()
  foreach(tgt IN LISTS ANONSYNC_SANITIZER_COMPILE_TARGETS)
    target_compile_options(${tgt} PRIVATE -fsanitize=address,undefined -fno-omit-frame-pointer)
  endforeach()
  foreach(tgt
      anonsync_core
      anonsync_fuzz_json_codec
      anonsync_fuzz_jwt_codec
      anonsync_fuzz_route_event_ledger
      anonsync_sqlite_exact_value_test
      anonsync_ingress_sender_replay_record_test
      anonsync_sqlite_replay_ledger_schema_contract_test
      anonsync_sqlite_snapshot_geometry_test
      anonsync_sqlite_verification_budget_test
      anonsync_sqlite_snapshot_seal_test
      anonsync_sqlite_snapshot_geometry_binding_test
      anonsync_sqlite_snapshot_sidecar_binding_test
      anonsync_sqlite_replay_ledger_schema_integrity_test
      anonsync_sqlite_ingress_sender_replay_integrity_test
      anonsync_sqlite_runtime_policy_test
      anonsync_sqlite_support_test
      anonsync_sqlite_connection_authority_test
      anonsync_sqlite_process_authority_fork_test
      anonsync_sqlite_owner_generation_borrow_test
      anonsync_sync_peer_ingress_wire_test
      anonsync_peer_ingress_wire_adversarial_test
      anonsync_sync_peer_wire_compatibility_test
      anonsync_sqlite_runtime_payload_store_test
      anonsync_canonical_projection_verifier_test
      anonsync_sqlite_projection_decoder_test
      anonsync_peer_ingress_projection_integrity_test
      anonsync_peer_ingress_retention_integrity_test
      anonsync_peer_ingress_schema_attestation_test
      anonsync_peer_ingress_connection_profile_test)
    target_link_options(${tgt} PRIVATE -fsanitize=address,undefined)
  endforeach()
endif()
include(CTest)
if(ANONSYNC_ENABLE_LIBFUZZER)
  add_test(NAME anonsync_fuzz_sqlite_projection_decoder_smoke
    COMMAND anonsync_fuzz_sqlite_projection_decoder
      -runs=10000 -max_len=512 -seed=789
      -print_funcs=0 -print_final_stats=1)
  add_test(NAME anonsync_fuzz_sqlite_snapshot_geometry_smoke
    COMMAND anonsync_fuzz_sqlite_snapshot_geometry
      -runs=10000 -max_len=256 -seed=798
      -print_funcs=0 -print_final_stats=1)
endif()
add_test(NAME anonsync_core_help COMMAND anonsync_core --help)
add_test(NAME anonsync_core_sync_domain_model_selftest COMMAND anonsync_core --selftest-sync-domain-model)
add_test(NAME anonsync_core_sync_peer_ingress_lifecycle_selftest COMMAND anonsync_core --selftest-sync-peer-ingress-lifecycle)
add_test(NAME anonsync_core_sync_peer_ingress_wire_codec_test COMMAND anonsync_sync_peer_ingress_wire_test)
add_test(NAME anonsync_peer_ingress_wire_adversarial_test
  COMMAND anonsync_peer_ingress_wire_adversarial_test)
add_test(NAME anonsync_sync_peer_wire_compatibility_test
  COMMAND anonsync_sync_peer_wire_compatibility_test)
add_test(NAME anonsync_sqlite_runtime_payload_store_test
  COMMAND anonsync_sqlite_runtime_payload_store_test)
add_test(NAME anonsync_canonical_projection_verifier_test
  COMMAND anonsync_canonical_projection_verifier_test)
add_test(NAME anonsync_sqlite_projection_decoder_test
  COMMAND anonsync_sqlite_projection_decoder_test)
add_test(NAME anonsync_peer_ingress_projection_integrity_test
  COMMAND anonsync_peer_ingress_projection_integrity_test)
add_test(NAME anonsync_peer_ingress_retention_integrity_test
  COMMAND anonsync_peer_ingress_retention_integrity_test)
add_test(NAME anonsync_peer_ingress_schema_attestation_test
  COMMAND anonsync_peer_ingress_schema_attestation_test)
add_test(NAME anonsync_peer_ingress_connection_profile_test
  COMMAND anonsync_peer_ingress_connection_profile_test)
find_package(Python3 COMPONENTS Interpreter QUIET)
if(Python3_Interpreter_FOUND)
  add_test(NAME anonsync_peer_ingress_connection_profile_source_audit
    COMMAND ${Python3_EXECUTABLE}
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_peer_ingress_connection_profile.py
      ${CMAKE_CURRENT_SOURCE_DIR}
      src/sync_domain.cpp)
  add_test(NAME anonsync_sqlite_scalar_extraction_source_audit
    COMMAND ${Python3_EXECUTABLE}
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_scalar_extraction.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_ingress_sender_replay_integrity_source_audit
    COMMAND ${Python3_EXECUTABLE}
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_ingress_sender_replay_integrity.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sqlite_replay_ledger_schema_contract_source_audit
    COMMAND ${Python3_EXECUTABLE}
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_replay_ledger_schema_contract.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sqlite_snapshot_seal_source_audit
    COMMAND ${Python3_EXECUTABLE}
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_snapshot_seal.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sqlite_snapshot_geometry_source_audit
    COMMAND ${Python3_EXECUTABLE}
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_snapshot_geometry.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_sqlite_verification_budget_source_audit
    COMMAND ${Python3_EXECUTABLE}
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/audit_sqlite_verification_budget.py
      --root ${CMAKE_CURRENT_SOURCE_DIR})
  add_test(NAME anonsync_active_persistence_boundary_inventory_audit
    COMMAND ${Python3_EXECUTABLE}
      ${CMAKE_CURRENT_SOURCE_DIR}/tools/rev0763_persistence_boundary_audit.py
      ${CMAKE_CURRENT_SOURCE_DIR}
      --enforce)
endif()
set_tests_properties(
  anonsync_core_sync_domain_model_selftest
  anonsync_core_sync_peer_ingress_lifecycle_selftest
  PROPERTIES RESOURCE_LOCK anonsync_peer_ingress_lifecycle_fixture)
add_test(NAME anonsync_core_json_parser_boundary_selftest COMMAND anonsync_core --selftest-json-parser)
add_test(NAME anonsync_core_sqlite_wal_verified_claims_selftest COMMAND anonsync_core --selftest-ledger-sqlite-wal)
add_test(NAME anonsync_sqlite_exact_value_test COMMAND anonsync_sqlite_exact_value_test)
add_test(NAME anonsync_ingress_sender_replay_record_test
  COMMAND anonsync_ingress_sender_replay_record_test)
add_test(NAME anonsync_sqlite_replay_ledger_schema_contract_test
  COMMAND anonsync_sqlite_replay_ledger_schema_contract_test)
add_test(NAME anonsync_sqlite_snapshot_seal_test
  COMMAND anonsync_sqlite_snapshot_seal_test)
add_test(NAME anonsync_sqlite_snapshot_geometry_test
  COMMAND anonsync_sqlite_snapshot_geometry_test)
add_test(NAME anonsync_sqlite_verification_budget_test
  COMMAND anonsync_sqlite_verification_budget_test)
add_test(NAME anonsync_sqlite_snapshot_geometry_binding_test
  COMMAND anonsync_sqlite_snapshot_geometry_binding_test)
set_tests_properties(anonsync_sqlite_snapshot_geometry_binding_test
  PROPERTIES TIMEOUT 20)
add_test(NAME anonsync_sqlite_snapshot_sidecar_binding_test
  COMMAND anonsync_sqlite_snapshot_sidecar_binding_test)
set_tests_properties(anonsync_sqlite_snapshot_sidecar_binding_test
  PROPERTIES TIMEOUT 30)
set_tests_properties(
  anonsync_sqlite_snapshot_seal_test
  anonsync_sqlite_snapshot_geometry_binding_test
  anonsync_sqlite_snapshot_sidecar_binding_test
  PROPERTIES RESOURCE_LOCK anonsync_sqlite_snapshot_staging_fixture)
add_test(NAME anonsync_sqlite_replay_ledger_schema_integrity_test
  COMMAND anonsync_sqlite_replay_ledger_schema_integrity_test)
set_tests_properties(anonsync_sqlite_replay_ledger_schema_integrity_test
  PROPERTIES TIMEOUT 30)
add_test(NAME anonsync_sqlite_ingress_sender_replay_integrity_test
  COMMAND anonsync_sqlite_ingress_sender_replay_integrity_test)
set_tests_properties(anonsync_sqlite_ingress_sender_replay_integrity_test
  PROPERTIES TIMEOUT 30)
add_test(NAME anonsync_sqlite_runtime_policy_test COMMAND anonsync_sqlite_runtime_policy_test)
add_test(NAME anonsync_sqlite_support_test COMMAND anonsync_sqlite_support_test)
add_test(NAME anonsync_sqlite_connection_authority_test
  COMMAND anonsync_sqlite_connection_authority_test)
set_tests_properties(anonsync_sqlite_connection_authority_test
  PROPERTIES TIMEOUT 15)
add_test(NAME anonsync_sqlite_process_authority_fork_test
  COMMAND anonsync_sqlite_process_authority_fork_test)
set_tests_properties(anonsync_sqlite_process_authority_fork_test
  PROPERTIES TIMEOUT 20)
add_test(NAME anonsync_sqlite_owner_generation_borrow_test
  COMMAND anonsync_sqlite_owner_generation_borrow_test)
set_tests_properties(anonsync_sqlite_owner_generation_borrow_test
  PROPERTIES TIMEOUT 20)
add_test(NAME anonsync_core_sqlite_runtime_profile_selftest COMMAND anonsync_core --selftest-ledger-host-capability-probe)
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
