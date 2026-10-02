cmake_minimum_required(VERSION 3.20)

project(IoTox VERSION 0.51.0 LANGUAGES C CXX)

set(IOTOX_LINKED_TOXCORE_VARIANT "" CACHE STRING
    "Optional provenance suffix for a source-linked c-toxcore provider")

set(IOTOX_CODENAME "Freshness-Explicit Projection Recovery")
file(READ "${CMAKE_CURRENT_SOURCE_DIR}/REVISION" IOTOX_REVISION_FILE)
string(STRIP "${IOTOX_REVISION_FILE}" IOTOX_REVISION)
if(NOT IOTOX_REVISION MATCHES "^rev([0-9][0-9][0-9][0-9])$")
    message(FATAL_ERROR "REVISION must be one canonical revNNNN record")
endif()
math(EXPR IOTOX_REVISION_NUMBER "${CMAKE_MATCH_1}")

# The executable consumes release identity from this constexpr header, while
# CMake and REVISION also stamp packaging and tests. Refuse configuration when
# those copies drift so a stale binary cannot pass through a newly stamped tree.
file(READ "${CMAKE_CURRENT_SOURCE_DIR}/include/iotox/version.hpp"
    IOTOX_VERSION_HEADER)
string(REGEX MATCH "kVersion = \"([^\"]+)\"" _identity_match
    "${IOTOX_VERSION_HEADER}")
set(IOTOX_HEADER_VERSION "${CMAKE_MATCH_1}")
string(REGEX MATCH "kVersionMajor = ([0-9]+)U" _identity_match
    "${IOTOX_VERSION_HEADER}")
set(IOTOX_HEADER_VERSION_MAJOR "${CMAKE_MATCH_1}")
string(REGEX MATCH "kVersionMinor = ([0-9]+)U" _identity_match
    "${IOTOX_VERSION_HEADER}")
set(IOTOX_HEADER_VERSION_MINOR "${CMAKE_MATCH_1}")
string(REGEX MATCH "kVersionPatch = ([0-9]+)U" _identity_match
    "${IOTOX_VERSION_HEADER}")
set(IOTOX_HEADER_VERSION_PATCH "${CMAKE_MATCH_1}")
string(REGEX MATCH "kRevision = \"([^\"]+)\"" _identity_match
    "${IOTOX_VERSION_HEADER}")
set(IOTOX_HEADER_REVISION "${CMAKE_MATCH_1}")
string(REGEX MATCH "kRevisionNumber = ([0-9]+)U" _identity_match
    "${IOTOX_VERSION_HEADER}")
set(IOTOX_HEADER_REVISION_NUMBER "${CMAKE_MATCH_1}")
string(REGEX MATCH "kCodename = \"([^\"]+)\"" _identity_match
    "${IOTOX_VERSION_HEADER}")
set(IOTOX_HEADER_CODENAME "${CMAKE_MATCH_1}")

if(NOT IOTOX_HEADER_VERSION STREQUAL PROJECT_VERSION OR
   NOT IOTOX_HEADER_VERSION_MAJOR STREQUAL PROJECT_VERSION_MAJOR OR
   NOT IOTOX_HEADER_VERSION_MINOR STREQUAL PROJECT_VERSION_MINOR OR
   NOT IOTOX_HEADER_VERSION_PATCH STREQUAL PROJECT_VERSION_PATCH OR
   NOT IOTOX_HEADER_REVISION STREQUAL IOTOX_REVISION OR
   NOT IOTOX_HEADER_REVISION_NUMBER STREQUAL IOTOX_REVISION_NUMBER OR
   NOT IOTOX_HEADER_CODENAME STREQUAL IOTOX_CODENAME)
    message(FATAL_ERROR
        "IoTox product identity drift: CMake=${PROJECT_VERSION} "
        "${IOTOX_REVISION} '${IOTOX_CODENAME}', header=${IOTOX_HEADER_VERSION} "
        "${IOTOX_HEADER_REVISION} '${IOTOX_HEADER_CODENAME}'")
endif()

include(CTest)
find_package(Threads REQUIRED)
find_package(Git QUIET)

option(IOTOX_WARNINGS_AS_ERRORS "Treat compiler warnings as errors" ON)
option(IOTOX_ENABLE_ASAN "Enable AddressSanitizer" OFF)
option(IOTOX_ENABLE_UBSAN "Enable UndefinedBehaviorSanitizer" OFF)
option(IOTOX_ENABLE_TSAN "Enable ThreadSanitizer" OFF)
option(IOTOX_ENABLE_COVERAGE "Instrument project and test targets for gcov coverage" OFF)
option(IOTOX_BUILD_FUZZER "Build parser and state fuzz targets (Clang only)" OFF)
option(IOTOX_BUILD_MUTORR_RESEARCH "Build the preserved Mutorr research branch" OFF)
option(IOTOX_BUILD_RESEARCH_LAB "Build the historical research CLI (requires Mutorr)" OFF)
option(IOTOX_BUILD_BENCHMARK "Build the preserved Mutorr microbenchmark" OFF)
option(IOTOX_VALIDATE_REVISION_CUBE_LAYOUT
    "Test the historical hidden .datacube revision-package layout" OFF)
set(IOTOX_TEST_SHARD_COUNT "1" CACHE STRING
    "Split the owned unit/integration registry into this many CTest processes (1..64)")
set(IOTOX_TOXCORE_SOURCE_DIR "" CACHE PATH
    "Optional pinned c-toxcore source tree to compile into the iotox executable")
set(IOTOX_ARGON2_LIBRARY "" CACHE FILEPATH
    "Optional Argon2 library to link into iotox instead of runtime loading")
set(IOTOX_PROVENANCE_SOURCE_TREE "${CMAKE_CURRENT_SOURCE_DIR}" CACHE STRING
    "Source tree label embedded in iotox doctor binary output")
set(IOTOX_PROVENANCE_BUILD_TREE "${CMAKE_CURRENT_BINARY_DIR}" CACHE STRING
    "Build tree label embedded in iotox doctor binary output")

set(IOTOX_SOURCE_COMMIT "unknown")
set(IOTOX_SOURCE_DIRTY "unknown")
if(Git_FOUND AND EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/.git")
    execute_process(
        COMMAND "${GIT_EXECUTABLE}" rev-parse --verify HEAD
        WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
        RESULT_VARIABLE IOTOX_GIT_COMMIT_RESULT
        OUTPUT_VARIABLE IOTOX_GIT_COMMIT_OUTPUT
        ERROR_QUIET
        OUTPUT_STRIP_TRAILING_WHITESPACE)
    if(IOTOX_GIT_COMMIT_RESULT EQUAL 0 AND NOT IOTOX_GIT_COMMIT_OUTPUT STREQUAL "")
        set(IOTOX_SOURCE_COMMIT "${IOTOX_GIT_COMMIT_OUTPUT}")
    endif()
    execute_process(
        COMMAND "${GIT_EXECUTABLE}" status --porcelain=v1 --untracked-files=no
        WORKING_DIRECTORY "${CMAKE_CURRENT_SOURCE_DIR}"
        RESULT_VARIABLE IOTOX_GIT_STATUS_RESULT
        OUTPUT_VARIABLE IOTOX_GIT_STATUS_OUTPUT
        ERROR_QUIET
        OUTPUT_STRIP_TRAILING_WHITESPACE)
    if(IOTOX_GIT_STATUS_RESULT EQUAL 0)
        if(IOTOX_GIT_STATUS_OUTPUT STREQUAL "")
            set(IOTOX_SOURCE_DIRTY "0")
        else()
            set(IOTOX_SOURCE_DIRTY "1")
        endif()
    endif()
endif()

if(IOTOX_BUILD_RESEARCH_LAB AND NOT IOTOX_BUILD_MUTORR_RESEARCH)
    message(FATAL_ERROR "IOTOX_BUILD_RESEARCH_LAB requires IOTOX_BUILD_MUTORR_RESEARCH=ON")
endif()
if(IOTOX_BUILD_BENCHMARK AND NOT IOTOX_BUILD_MUTORR_RESEARCH)
    message(FATAL_ERROR "IOTOX_BUILD_BENCHMARK requires IOTOX_BUILD_MUTORR_RESEARCH=ON")
endif()

list(APPEND CMAKE_MODULE_PATH "${CMAKE_CURRENT_SOURCE_DIR}/cmake")
include(CompilerWarnings)
include(Sanitizers)

iotox_validate_sanitizers()

if(IOTOX_ENABLE_COVERAGE)
    if(NOT CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
        message(FATAL_ERROR "IOTOX_ENABLE_COVERAGE requires GCC or Clang")
    endif()
    if(IOTOX_ENABLE_ASAN OR IOTOX_ENABLE_UBSAN OR IOTOX_ENABLE_TSAN)
        message(FATAL_ERROR "Coverage and sanitizer instrumentation must use separate build trees")
    endif()
    # -O1 keeps hardened toolchains' fortify contract while retaining useful
    # source-level coverage mapping.
    add_compile_options(--coverage -O1 -g)
    add_link_options(--coverage)
endif()

add_library(iotox_core STATIC
    src/agent.cpp
    src/agent_config.cpp
    src/agent_preflight.cpp
    src/diagnostics.cpp
    src/peer_alias.cpp
    src/peer_invitation.cpp
    src/person_multidevice.cpp
    src/protected_state.cpp
    src/policy_witness.cpp
    src/rollback_witness.cpp
    src/rollback_witness_service.cpp
    src/command_engine.cpp
    src/command_store.cpp
    src/file_transfer.cpp
    src/interactive.cpp
    src/interactive_client.cpp
    src/interactive_incarnation.cpp
    src/interactive_session.cpp
    src/interactive_service.cpp
    src/latency_histogram.cpp
    src/retained_send_telemetry.cpp
    src/route_binding.cpp
    src/route_health.cpp
    src/route_inventory.cpp
    src/route_store.cpp
    src/route_worker.cpp
    src/self_swarm.cpp
    src/sync_activation.cpp
    src/sync_automation.cpp
    src/sync_attempt_store.cpp
    src/sync_authorization.cpp
    src/sync_content_acceptance.cpp
    src/sync_content_attempt_store.cpp
    src/sync_content_publication.cpp
    src/sync_content_wire.cpp
    src/sync_content.cpp
    src/sync_content_service.cpp
    src/sync_content_subscriber.cpp
    src/sync_content_workspace.cpp
    src/sync_digest.cpp
    src/sync_doctor.cpp
    src/sync_recovery_verify.cpp
    src/sync_gc.cpp
    src/sync_guarded_witness.cpp
    src/sync_tree_v2_witness.cpp
    src/sync_health.cpp
    src/sync_head.cpp
    src/sync_job.cpp
    src/sync_manifest.cpp
    src/sync_namespace.cpp
    src/sync_publication.cpp
    src/sync_policy_witness.cpp
    src/sync_replica.cpp
    src/sync_reachability.cpp
    src/sync_reconstruction.cpp
    src/sync_retention.cpp
    src/sync_rollback.cpp
    src/sync_route_selector.cpp
    src/sync_scheduler.cpp
    src/sync_service.cpp
    src/sync_source_watch.cpp
    src/sync_subscriber.cpp
    src/sync_tree.cpp
    src/sync_multiwriter.cpp
    src/sync_multiwriter_maintenance.cpp
    src/sync_multiwriter_reconcile.cpp
    src/sync_multiwriter_service.cpp
    src/sync_multiwriter_store.cpp
    src/sync_multiwriter_subscriber.cpp
    src/sync_time_machine.cpp
    src/sync_multiwriter_wire.cpp
    src/sync_multiwriter_worktree.cpp
    src/sync_multiwriter_workspace.cpp
    src/sync_transaction.cpp
    src/sync_transfer.cpp
    src/sync_wire.cpp
    src/update_bundle.cpp
    src/update_service.cpp
    src/update_state.cpp
    src/update_witness.cpp
    src/terminal_profile.cpp
    src/terminal_process.cpp
    src/terminal_cgroup.cpp
    src/terminal_posix.cpp
    src/terminal_cli.cpp
    src/terminal_admin_cli.cpp
    src/cli_registry.cpp
    src/cli.cpp
    src/local/friend_request_fifo.cpp
    src/local/peer_fifo.cpp
    src/local/control_protocol.cpp
    src/local/seqpacket_security.cpp
    src/local/control_socket.cpp
    src/local/terminal_protocol.cpp
    src/local/terminal_socket.cpp
    src/local/runtime_tree.cpp
    src/network.cpp
    src/security/random.cpp
    src/security/process_hardening.cpp
    src/security/recovery.cpp
    src/security/embedded_wordlist.cpp
    src/security/sodium.cpp
    src/security/identity.cpp
    src/security/authority.cpp
    src/security/authority_session.cpp
    src/protocol/frame.cpp
    src/protocol/ratox.cpp
    src/protocol/session.cpp
    src/protocol/command.cpp
    src/protocol/delegation.cpp
    src/state_store.cpp
    src/system_summary.cpp
    src/toxcore/bootstrap.cpp
    src/toxcore/default_nodes.cpp
    src/toxcore/dynamic_library.cpp
    src/toxcore/linked_api.cpp
    src/toxcore/transport.cpp
    components/toxsync/src/artifact_hasher.cpp
    components/toxsync/src/hash.cpp
    components/toxsync/src/index.cpp
    components/toxsync/src/index_file.cpp
    components/toxsync/src/planner.cpp
    components/toxsync/src/apply.cpp
    components/toxsync/src/content_fabric.cpp
    components/toxsync/src/content_store.cpp
    components/toxsync/src/multisource.cpp
    components/toxsync/src/paged_content.cpp
    components/toxsync/src/range_source.cpp
    components/toxsync/src/rolling_checksum.cpp
    components/toxsync/src/treepack.cpp
)
add_library(IoTox::core ALIAS iotox_core)
set_target_properties(iotox_core PROPERTIES POSITION_INDEPENDENT_CODE ON)

target_compile_features(iotox_core PUBLIC cxx_std_20)
target_include_directories(iotox_core
    PUBLIC
        $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
        $<INSTALL_INTERFACE:include>
    PRIVATE
        ${CMAKE_CURRENT_SOURCE_DIR}/components/toxsync/include
)
target_link_libraries(iotox_core PUBLIC Threads::Threads ${CMAKE_DL_LIBS})
target_compile_definitions(iotox_core PRIVATE
    TOX_HIDE_DEPRECATED=1
    IOTOX_SOURCE_COMMIT="${IOTOX_SOURCE_COMMIT}"
    IOTOX_SOURCE_DIRTY="${IOTOX_SOURCE_DIRTY}"
    IOTOX_SOURCE_TREE="${IOTOX_PROVENANCE_SOURCE_TREE}"
    IOTOX_BUILD_TREE="${IOTOX_PROVENANCE_BUILD_TREE}"
)
iotox_set_project_warnings(iotox_core)
iotox_enable_sanitizers(iotox_core)

if(IOTOX_ARGON2_LIBRARY)
    if(NOT EXISTS "${IOTOX_ARGON2_LIBRARY}")
        message(FATAL_ERROR "IOTOX_ARGON2_LIBRARY does not exist: ${IOTOX_ARGON2_LIBRARY}")
    endif()
    target_link_libraries(iotox_core PUBLIC "${IOTOX_ARGON2_LIBRARY}")
    target_compile_definitions(iotox_core PRIVATE IOTOX_LINKED_ARGON2=1)
    message(STATUS "IoTox will use linked Argon2 from ${IOTOX_ARGON2_LIBRARY}")
else()
    message(STATUS "IoTox will use runtime-loaded Argon2 (research/test provider)")
endif()

if(IOTOX_TOXCORE_SOURCE_DIR)
    if(NOT EXISTS "${IOTOX_TOXCORE_SOURCE_DIR}/CMakeLists.txt")
        message(FATAL_ERROR "IOTOX_TOXCORE_SOURCE_DIR does not contain c-toxcore CMakeLists.txt")
    endif()
    find_package(PkgConfig REQUIRED)
    pkg_check_modules(IOTOX_SODIUM REQUIRED IMPORTED_TARGET libsodium)
    set(BUILD_TOXAV OFF CACHE BOOL "" FORCE)
    set(MUST_BUILD_TOXAV OFF CACHE BOOL "" FORCE)
    set(BOOTSTRAP_DAEMON OFF CACHE BOOL "" FORCE)
    set(DHT_BOOTSTRAP OFF CACHE BOOL "" FORCE)
    set(BUILD_FUN_UTILS OFF CACHE BOOL "" FORCE)
    set(BUILD_FUZZ_TESTS OFF CACHE BOOL "" FORCE)
    set(BUILD_MISC_TESTS OFF CACHE BOOL "" FORCE)
    set(AUTOTEST OFF CACHE BOOL "" FORCE)
    set(UNITTEST OFF CACHE BOOL "" FORCE)
    set(ENABLE_SHARED OFF CACHE BOOL "" FORCE)
    set(ENABLE_STATIC ON CACHE BOOL "" FORCE)
    add_subdirectory(
        "${IOTOX_TOXCORE_SOURCE_DIR}"
        "${CMAKE_BINARY_DIR}/_deps/c-toxcore-build"
        EXCLUDE_FROM_ALL
    )
    if(NOT TARGET toxcore_static)
        message(FATAL_ERROR "pinned c-toxcore source did not define toxcore_static")
    endif()
    target_link_libraries(iotox_core PUBLIC toxcore_static PkgConfig::IOTOX_SODIUM)
    target_include_directories(iotox_core PRIVATE "${IOTOX_TOXCORE_SOURCE_DIR}")
    target_compile_definitions(iotox_core PRIVATE
        IOTOX_LINKED_TOXCORE=1
        IOTOX_LINKED_SODIUM=1
    )
    if(NOT IOTOX_LINKED_TOXCORE_VARIANT STREQUAL "")
        target_compile_definitions(iotox_core PRIVATE
            IOTOX_LINKED_TOXCORE_VARIANT="${IOTOX_LINKED_TOXCORE_VARIANT}"
        )
    endif()
    message(STATUS "IoTox will use linked c-toxcore from ${IOTOX_TOXCORE_SOURCE_DIR}")
else()
    message(STATUS "IoTox will use runtime-loaded c-toxcore (research/test provider)")
endif()

add_executable(iotox src/main.cpp)
target_compile_features(iotox PRIVATE cxx_std_20)
target_link_libraries(iotox PRIVATE IoTox::core)
iotox_set_project_warnings(iotox)
iotox_enable_sanitizers(iotox)

if(IOTOX_BUILD_MUTORR_RESEARCH)
    add_library(iotox_mutorr_research STATIC
        incubator/mutorr/src/mutorr/cube.cpp
        incubator/mutorr/src/mutorr/head.cpp
        incubator/mutorr/src/mutorr/id.cpp
    )
    add_library(IoTox::mutorr_research ALIAS iotox_mutorr_research)
    target_compile_features(iotox_mutorr_research PUBLIC cxx_std_20)
    target_include_directories(iotox_mutorr_research
        PUBLIC
            ${CMAKE_CURRENT_SOURCE_DIR}/include
            ${CMAKE_CURRENT_SOURCE_DIR}/incubator/mutorr/include
    )
    target_link_libraries(iotox_mutorr_research PUBLIC IoTox::core)
    iotox_set_project_warnings(iotox_mutorr_research)
    iotox_enable_sanitizers(iotox_mutorr_research)

    if(IOTOX_BUILD_RESEARCH_LAB)
        add_executable(iotox_lab incubator/mutorr/src/research_main.cpp)
        set_target_properties(iotox_lab PROPERTIES OUTPUT_NAME "iotox-lab")
        target_compile_features(iotox_lab PRIVATE cxx_std_20)
        target_link_libraries(iotox_lab PRIVATE IoTox::core IoTox::mutorr_research)
        iotox_set_project_warnings(iotox_lab)
        iotox_enable_sanitizers(iotox_lab)
    endif()

    if(IOTOX_BUILD_BENCHMARK)
        add_executable(iotox_bench incubator/mutorr/src/benchmark.cpp)
        target_compile_features(iotox_bench PRIVATE cxx_std_20)
        target_link_libraries(iotox_bench PRIVATE IoTox::mutorr_research)
        iotox_set_project_warnings(iotox_bench)
        iotox_enable_sanitizers(iotox_bench)
    endif()
endif()

if(BUILD_TESTING)
    if(NOT IOTOX_TEST_SHARD_COUNT MATCHES "^[1-9][0-9]*$")
        message(FATAL_ERROR
            "IOTOX_TEST_SHARD_COUNT must be an integer in the range 1..64")
    endif()
    if(IOTOX_TEST_SHARD_COUNT GREATER 64)
        message(FATAL_ERROR
            "IOTOX_TEST_SHARD_COUNT must be an integer in the range 1..64")
    endif()

    add_library(iotox_mock_argon2 SHARED tests/mock_argon2.cpp)
    target_compile_features(iotox_mock_argon2 PRIVATE cxx_std_20)
    target_include_directories(iotox_mock_argon2 PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
    set_target_properties(iotox_mock_argon2 PROPERTIES
        OUTPUT_NAME "argon2-iotox-mock"
        CXX_VISIBILITY_PRESET hidden
        VISIBILITY_INLINES_HIDDEN YES
    )
    target_compile_definitions(iotox_mock_argon2 PRIVATE IOTOX_FORCE_BUILTIN_ARGON2_ABI=1)
    iotox_set_project_warnings(iotox_mock_argon2)
    iotox_enable_sanitizers(iotox_mock_argon2)

    add_library(iotox_mock_toxcore SHARED
        tests/mock_toxcore.cpp
    )
    target_compile_features(iotox_mock_toxcore PRIVATE cxx_std_20)
    target_include_directories(iotox_mock_toxcore PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
    set_target_properties(iotox_mock_toxcore PROPERTIES
        OUTPUT_NAME "toxcore-iotox-mock"
        CXX_VISIBILITY_PRESET hidden
        VISIBILITY_INLINES_HIDDEN YES
    )
    target_compile_definitions(iotox_mock_toxcore PRIVATE
        IOTOX_MOCK_EXPORTS=1
        IOTOX_FORCE_BUILTIN_TOXCORE_ABI=1
    )
    target_link_libraries(iotox_mock_toxcore PRIVATE IoTox::core)
    iotox_set_project_warnings(iotox_mock_toxcore)
    iotox_enable_sanitizers(iotox_mock_toxcore)

    find_library(IOTOX_TEST_SODIUM_LIBRARY NAMES sodium libsodium)
    if(NOT IOTOX_TEST_SODIUM_LIBRARY)
        file(GLOB IOTOX_TEST_SODIUM_CANDIDATES
            "/nix/store/*-libsodium-*/lib/libsodium.so*"
            "/run/current-system/sw/lib/libsodium.so*"
        )
        list(SORT IOTOX_TEST_SODIUM_CANDIDATES)
        list(FILTER IOTOX_TEST_SODIUM_CANDIDATES EXCLUDE REGEX "\\.a$")
        if(IOTOX_TEST_SODIUM_CANDIDATES)
            list(GET IOTOX_TEST_SODIUM_CANDIDATES 0 IOTOX_TEST_SODIUM_LIBRARY)
        endif()
    endif()
    set(IOTOX_CTEST_RUNTIME_ENV
        "IOTOX_ARGON2_LIBRARY=$<TARGET_FILE:iotox_mock_argon2>")
    if(IOTOX_TEST_SODIUM_LIBRARY)
        list(APPEND IOTOX_CTEST_RUNTIME_ENV
            "IOTOX_SODIUM_LIBRARY=${IOTOX_TEST_SODIUM_LIBRARY}")
    endif()

    set(IOTOX_TEST_SOURCES
        tests/test_main.cpp
        tests/test_abi.cpp
        tests/test_agent.cpp
        tests/test_agent_config.cpp
        tests/test_diagnostics.cpp
        tests/test_peer_alias.cpp
        tests/test_peer_invitation.cpp
        tests/test_person_multidevice.cpp
        tests/test_policy_witness.cpp
        tests/test_protected_state.cpp
        tests/test_authority.cpp
        tests/test_authority_session.cpp
        tests/test_bootstrap.cpp
        tests/test_command.cpp
        tests/test_command_engine.cpp
        tests/test_delegation.cpp
        tests/test_friend_request_fifo.cpp
        tests/test_peer_fifo.cpp
        tests/test_command_store.cpp
        tests/test_cli.cpp
        tests/test_file_transfer.cpp
        tests/test_interactive.cpp
        tests/test_interactive_client.cpp
        tests/test_interactive_incarnation.cpp
        tests/test_latency_histogram.cpp
        tests/test_retained_send_telemetry.cpp
        tests/test_route_binding.cpp
        tests/test_route_inventory.cpp
        tests/test_route_store.cpp
        tests/test_route_worker.cpp
        tests/test_self_swarm.cpp
        tests/test_sync_activation.cpp
        tests/test_sync_automation.cpp
        tests/test_sync_attempt_store.cpp
        tests/test_sync_authorization.cpp
        tests/test_sync_content_acceptance.cpp
        tests/test_sync_content_attempt_store.cpp
        tests/test_sync_content_publication.cpp
        tests/test_sync_content.cpp
        tests/test_sync_content_service.cpp
        tests/test_sync_content_subscriber.cpp
        tests/test_sync_digest.cpp
        tests/test_sync_doctor.cpp
        tests/test_sync_recovery_verify.cpp
        tests/test_sync_gc.cpp
        tests/test_sync_guarded_witness.cpp
        tests/test_sync_tree_v2_witness.cpp
        tests/test_sync_health.cpp
        tests/test_sync_head.cpp
        tests/test_sync_job.cpp
        tests/test_sync_manifest.cpp
        tests/test_sync_namespace.cpp
        tests/test_sync_publication.cpp
        tests/test_sync_replica.cpp
        tests/test_sync_reachability.cpp
        tests/test_sync_reconstruction.cpp
        tests/test_sync_retention.cpp
        tests/test_sync_rollback.cpp
        tests/test_sync_route_selector.cpp
        tests/test_sync_scheduler.cpp
        tests/test_sync_service.cpp
        tests/test_sync_source_watch.cpp
        tests/test_sync_subscriber.cpp
        tests/test_sync_tree.cpp
        tests/test_sync_multiwriter.cpp
        tests/test_sync_multiwriter_maintenance.cpp
        tests/test_sync_multiwriter_reconcile.cpp
        tests/test_sync_multiwriter_service.cpp
        tests/test_sync_multiwriter_store.cpp
        tests/test_sync_time_machine.cpp
        tests/test_sync_multiwriter_wire.cpp
        tests/test_sync_multiwriter_worktree.cpp
        tests/test_sync_multiwriter_workspace.cpp
        tests/test_sync_transaction.cpp
        tests/test_sync_transfer.cpp
        tests/test_sync_wire.cpp
        tests/test_update_bundle.cpp
        tests/test_update_service.cpp
        tests/test_update_state.cpp
        tests/test_update_witness.cpp
        tests/test_interactive_service.cpp
        tests/test_terminal_profile.cpp
        tests/test_terminal_process.cpp
        tests/test_terminal_cgroup.cpp
        tests/test_local_control_protocol.cpp
        tests/test_local_control_socket.cpp
        tests/test_terminal_protocol.cpp
        tests/test_terminal_socket.cpp
        tests/test_network.cpp
        tests/test_protocol.cpp
        tests/test_session.cpp
        tests/test_recovery.cpp
        tests/test_rollback_witness.cpp
        tests/test_rollback_witness_service.cpp
        tests/test_process_hardening.cpp
        tests/test_runtime_tree.cpp
        tests/test_state_store.cpp
        tests/test_toxcore_transport.cpp
    )
    if(IOTOX_BUILD_MUTORR_RESEARCH)
        list(APPEND IOTOX_TEST_SOURCES
            incubator/mutorr/tests/test_mutorr_cube.cpp
            incubator/mutorr/tests/test_mutorr_head.cpp
            incubator/mutorr/tests/test_mutorr_id.cpp
        )
    endif()

    add_executable(iotox_tests ${IOTOX_TEST_SOURCES})
    add_executable(
        iotox_update_service_fixture
        tests/update_service_fixture.cpp
    )
    target_compile_features(iotox_update_service_fixture PRIVATE cxx_std_20)
    target_link_libraries(iotox_update_service_fixture PRIVATE IoTox::core)
    iotox_set_project_warnings(iotox_update_service_fixture)
    iotox_enable_sanitizers(iotox_update_service_fixture)
    target_compile_definitions(iotox_tests PRIVATE
        "IOTOX_UPDATE_SERVICE_FIXTURE_PATH=\"$<TARGET_FILE:iotox_update_service_fixture>\""
    )
    target_compile_features(iotox_tests PRIVATE cxx_std_20)
    target_include_directories(iotox_tests PRIVATE
        tests
        components/toxsync/include
    )
    target_link_libraries(iotox_tests PRIVATE IoTox::core)
    if(IOTOX_BUILD_MUTORR_RESEARCH)
        target_link_libraries(iotox_tests PRIVATE IoTox::mutorr_research)
    endif()
    iotox_set_project_warnings(iotox_tests)
    # GCC 15's -O3 null-dereference pass does not carry the throwing test
    # harness checks into later std::vector mutation sites. Keep the warning
    # enabled for product targets; sanitizer lanes validate the test mutations.
    if(CMAKE_CXX_COMPILER_ID STREQUAL "GNU" AND
       CMAKE_CXX_COMPILER_VERSION VERSION_GREATER_EQUAL 15)
        target_compile_options(iotox_tests PRIVATE
            -Wno-null-dereference
            -Wno-array-bounds
        )
    endif()
    iotox_enable_sanitizers(iotox_tests)

    add_executable(iotox_terminal_pty_fixture tests/terminal_pty_fixture.cpp)
    target_compile_features(iotox_terminal_pty_fixture PRIVATE cxx_std_20)
    target_include_directories(iotox_terminal_pty_fixture PRIVATE include)
    target_link_libraries(iotox_terminal_pty_fixture PRIVATE Threads::Threads)
    iotox_set_project_warnings(iotox_terminal_pty_fixture)
    # This executable is the sandboxed payload, not the code under test. The
    # PTY profile deliberately installs a finite RLIMIT_AS before fexecve;
    # shadow-memory sanitizers cannot reserve their large virtual mappings
    # under that limit. Keep the controller/helper sanitized while leaving the
    # tiny payload native so the resource-limit boundary remains exercised.

    add_executable(
        iotox_terminal_posix_process_tests
        tests/test_terminal_posix_process.cpp
    )
    target_compile_features(iotox_terminal_posix_process_tests PRIVATE cxx_std_20)
    target_link_libraries(iotox_terminal_posix_process_tests PRIVATE IoTox::core)
    iotox_set_project_warnings(iotox_terminal_posix_process_tests)
    iotox_enable_sanitizers(iotox_terminal_posix_process_tests)
    if(IOTOX_ENABLE_ASAN OR IOTOX_ENABLE_TSAN)
        # The process test re-executes the sanitizer-instrumented product binary
        # as the privileged PTY setup helper. A finite RLIMIT_AS cannot coexist
        # with ASan or TSan shadow mappings, so only these instrumented helper
        # lanes disable that one profile limit; normal/release lanes enforce it.
        target_compile_definitions(iotox_terminal_posix_process_tests PRIVATE
            IOTOX_TEST_LARGE_SHADOW_HELPER=1
        )
    endif()

    add_executable(
        iotox_terminal_cgroup_recovery_process_tests
        tests/test_terminal_cgroup_recovery_process.cpp
    )
    target_compile_features(
        iotox_terminal_cgroup_recovery_process_tests PRIVATE cxx_std_20)
    target_link_libraries(
        iotox_terminal_cgroup_recovery_process_tests PRIVATE IoTox::core)
    iotox_set_project_warnings(iotox_terminal_cgroup_recovery_process_tests)
    iotox_enable_sanitizers(iotox_terminal_cgroup_recovery_process_tests)

    add_executable(
        iotox_terminal_controller_process_tests
        tests/test_terminal_controller_process.cpp
    )
    target_compile_features(
        iotox_terminal_controller_process_tests PRIVATE cxx_std_20)
    target_link_libraries(
        iotox_terminal_controller_process_tests PRIVATE IoTox::core)
    iotox_set_project_warnings(iotox_terminal_controller_process_tests)
    iotox_enable_sanitizers(iotox_terminal_controller_process_tests)

    add_executable(iotox_cli_process_tests tests/test_cli_process.cpp)
    target_compile_features(iotox_cli_process_tests PRIVATE cxx_std_20)
    iotox_set_project_warnings(iotox_cli_process_tests)
    iotox_enable_sanitizers(iotox_cli_process_tests)
    set(IOTOX_BINARY_PROCESS_TEST_TIMEOUT 120)
    if(IOTOX_ENABLE_TSAN)
        # This oracle deliberately forks many separately instrumented product
        # processes and then waits for asynchronous transport callbacks to be
        # durably projected. ThreadSanitizer can multiply both process startup
        # and callback latency under host contention without changing product
        # ordering. Expand only the bounded harness deadlines; assertions and
        # expected records remain byte-identical.
        target_compile_definitions(iotox_cli_process_tests PRIVATE
            IOTOX_PROCESS_TEST_TIMEOUT_MULTIPLIER=6
        )
        set(IOTOX_BINARY_PROCESS_TEST_TIMEOUT 420)
    elseif(IOTOX_ENABLE_ASAN)
        target_compile_definitions(iotox_cli_process_tests PRIVATE
            IOTOX_PROCESS_TEST_TIMEOUT_MULTIPLIER=3
        )
        set(IOTOX_BINARY_PROCESS_TEST_TIMEOUT 240)
    endif()

    add_executable(
        iotox_cli_authority_process_tests
        tests/test_cli_authority_process.cpp
    )
    target_compile_features(iotox_cli_authority_process_tests PRIVATE cxx_std_20)
    target_link_libraries(iotox_cli_authority_process_tests PRIVATE IoTox::core)
    iotox_set_project_warnings(iotox_cli_authority_process_tests)
    iotox_enable_sanitizers(iotox_cli_authority_process_tests)

    add_executable(
        iotox_ratox_restart_process_tests
        tests/test_ratox_restart_process.cpp
    )
    target_compile_features(iotox_ratox_restart_process_tests PRIVATE cxx_std_20)
    target_link_libraries(iotox_ratox_restart_process_tests PRIVATE IoTox::core)
    iotox_set_project_warnings(iotox_ratox_restart_process_tests)
    iotox_enable_sanitizers(iotox_ratox_restart_process_tests)

    add_executable(
        iotox_sync_publication_process_tests
        tests/test_sync_publication_process.cpp
    )
    target_compile_features(
        iotox_sync_publication_process_tests PRIVATE cxx_std_20)
    target_link_libraries(
        iotox_sync_publication_process_tests PRIVATE IoTox::core)
    iotox_set_project_warnings(iotox_sync_publication_process_tests)
    iotox_enable_sanitizers(iotox_sync_publication_process_tests)

    add_executable(
        iotox_sync_retention_process_tests
        tests/test_sync_retention_process.cpp
    )
    target_compile_features(
        iotox_sync_retention_process_tests PRIVATE cxx_std_20)
    target_link_libraries(
        iotox_sync_retention_process_tests PRIVATE IoTox::core)
    iotox_set_project_warnings(iotox_sync_retention_process_tests)
    iotox_enable_sanitizers(iotox_sync_retention_process_tests)

    add_executable(
        iotox_sync_transaction_process_tests
        tests/test_sync_transaction_process.cpp
    )
    target_compile_features(
        iotox_sync_transaction_process_tests PRIVATE cxx_std_20)
    target_link_libraries(
        iotox_sync_transaction_process_tests PRIVATE IoTox::core)
    iotox_set_project_warnings(iotox_sync_transaction_process_tests)
    iotox_enable_sanitizers(iotox_sync_transaction_process_tests)

    add_executable(
        iotox_sync_rollback_process_tests
        tests/test_sync_rollback_process.cpp
    )
    target_compile_features(
        iotox_sync_rollback_process_tests PRIVATE cxx_std_20)
    target_link_libraries(
        iotox_sync_rollback_process_tests PRIVATE IoTox::core)
    iotox_set_project_warnings(iotox_sync_rollback_process_tests)
    iotox_enable_sanitizers(iotox_sync_rollback_process_tests)

    add_executable(
        iotox_sync_tree_process_tests
        tests/test_sync_tree_process.cpp
    )
    target_compile_features(
        iotox_sync_tree_process_tests PRIVATE cxx_std_20)
    target_link_libraries(
        iotox_sync_tree_process_tests PRIVATE IoTox::core)
    iotox_set_project_warnings(iotox_sync_tree_process_tests)
    iotox_enable_sanitizers(iotox_sync_tree_process_tests)

    function(iotox_add_owned_registry_test test_name)
        add_test(
            NAME ${test_name}
            COMMAND iotox_tests
                --mock-toxcore $<TARGET_FILE:iotox_mock_toxcore>
                --mock-argon2 $<TARGET_FILE:iotox_mock_argon2>
                --wordlist ${CMAKE_CURRENT_SOURCE_DIR}/third_party/eff_large_wordlist_2016-07-18.txt
                ${ARGN}
        )
        set_tests_properties(${test_name} PROPERTIES
            LABELS "owned-registry"
            ENVIRONMENT "${IOTOX_CTEST_RUNTIME_ENV}"
            PROCESSORS 1
            TIMEOUT 360
        )
    endfunction()

    if(IOTOX_TEST_SHARD_COUNT EQUAL 1)
        iotox_add_owned_registry_test(iotox.unit-and-integration)
    else()
        math(EXPR IOTOX_TEST_LAST_SHARD "${IOTOX_TEST_SHARD_COUNT} - 1")
        foreach(IOTOX_TEST_SHARD_INDEX RANGE 0 ${IOTOX_TEST_LAST_SHARD})
            iotox_add_owned_registry_test(
                iotox.unit-and-integration.shard-${IOTOX_TEST_SHARD_INDEX}
                --shard-index ${IOTOX_TEST_SHARD_INDEX}
                --shard-count ${IOTOX_TEST_SHARD_COUNT}
            )
        endforeach()
    endif()
    add_test(
        NAME iotox.terminal-posix-process
        COMMAND iotox_terminal_posix_process_tests
            $<TARGET_FILE:iotox>
            $<TARGET_FILE:iotox_terminal_pty_fixture>
    )
    set_tests_properties(iotox.terminal-posix-process PROPERTIES TIMEOUT 20)

    add_test(
        NAME iotox.sync-publication-process
        COMMAND iotox_sync_publication_process_tests
    )
    set_tests_properties(iotox.sync-publication-process PROPERTIES TIMEOUT 30)

    add_test(
        NAME iotox.sync-retention-process
        COMMAND iotox_sync_retention_process_tests
    )
    set_tests_properties(iotox.sync-retention-process PROPERTIES TIMEOUT 30)

    add_test(
        NAME iotox.sync-transaction-process
        COMMAND iotox_sync_transaction_process_tests
    )
    set_tests_properties(iotox.sync-transaction-process PROPERTIES TIMEOUT 30)

    add_test(
        NAME iotox.sync-rollback-process
        COMMAND iotox_sync_rollback_process_tests
    )
    set_tests_properties(iotox.sync-rollback-process PROPERTIES TIMEOUT 30)

    add_test(
        NAME iotox.sync-tree-process
        COMMAND iotox_sync_tree_process_tests
    )
    set_tests_properties(iotox.sync-tree-process PROPERTIES TIMEOUT 30)

    add_test(
        NAME iotox.terminal-cgroup-recovery-process
        COMMAND iotox_terminal_cgroup_recovery_process_tests --lifecycle
    )
    set_tests_properties(iotox.terminal-cgroup-recovery-process PROPERTIES
        SKIP_RETURN_CODE 77
        TIMEOUT 30
    )

    add_test(
        NAME iotox.terminal-cgroup-memory-resource-process
        COMMAND iotox_terminal_cgroup_recovery_process_tests --memory-resource
    )
    set_tests_properties(iotox.terminal-cgroup-memory-resource-process PROPERTIES
        SKIP_RETURN_CODE 77
        TIMEOUT 30
    )

    add_test(
        NAME iotox.terminal-cgroup-cpu-resource-process
        COMMAND iotox_terminal_cgroup_recovery_process_tests --cpu-resource
    )
    set_tests_properties(iotox.terminal-cgroup-cpu-resource-process PROPERTIES
        SKIP_RETURN_CODE 77
        TIMEOUT 30
    )

    add_test(
        NAME iotox.terminal-cgroup-io-resource-process
        COMMAND iotox_terminal_cgroup_recovery_process_tests --io-resource
    )
    set_tests_properties(iotox.terminal-cgroup-io-resource-process PROPERTIES
        SKIP_RETURN_CODE 77
        TIMEOUT 45
    )

    add_test(
        NAME iotox.terminal-cgroup-pressure-admission-process
        COMMAND iotox_terminal_cgroup_recovery_process_tests --pressure-admission
    )
    set_tests_properties(iotox.terminal-cgroup-pressure-admission-process PROPERTIES
        SKIP_RETURN_CODE 77
        TIMEOUT 30
    )

    add_test(
        NAME iotox.terminal-controller-process
        COMMAND iotox_terminal_controller_process_tests $<TARGET_FILE:iotox>
    )
    set_tests_properties(iotox.terminal-controller-process PROPERTIES TIMEOUT 20)

    add_test(
        NAME iotox.binary-process-lifecycle
        COMMAND iotox_cli_process_tests
            $<TARGET_FILE:iotox>
            $<TARGET_FILE:iotox_mock_toxcore>
    )
    set_tests_properties(iotox.binary-process-lifecycle PROPERTIES
        ENVIRONMENT "${IOTOX_CTEST_RUNTIME_ENV}"
        TIMEOUT ${IOTOX_BINARY_PROCESS_TEST_TIMEOUT}
    )
    if(IOTOX_ENABLE_ASAN OR IOTOX_ENABLE_TSAN)
        # Shadow-runtime instrumentation materially changes scheduler cost. Keep
        # this timing-sensitive whole-binary coalescing oracle isolated so a
        # parallel CTest invocation measures product behavior, not CPU theft
        # from unrelated instrumented registries.
        set_tests_properties(iotox.binary-process-lifecycle PROPERTIES
            RUN_SERIAL TRUE
        )
    endif()
    add_test(
        NAME iotox.ratox-restart-fence-process
        COMMAND iotox_ratox_restart_process_tests
            $<TARGET_FILE:iotox>
            $<TARGET_FILE:iotox_mock_toxcore>
    )
    set_tests_properties(iotox.ratox-restart-fence-process PROPERTIES
        ENVIRONMENT "${IOTOX_CTEST_RUNTIME_ENV}"
        TIMEOUT 60
    )
    add_test(
        NAME iotox.cli-authority-ceremony
        COMMAND iotox_cli_authority_process_tests $<TARGET_FILE:iotox>
    )
    set_tests_properties(iotox.cli-authority-ceremony PROPERTIES
        ENVIRONMENT "${IOTOX_CTEST_RUNTIME_ENV}"
    )
    add_test(NAME iotox.client-version COMMAND iotox --version)
    set_tests_properties(iotox.client-version PROPERTIES
        PASS_REGULAR_EXPRESSION "IoTox 0.51.0 rev0051"
    )
    add_test(NAME iotox.client-help COMMAND iotox --help)
    set_tests_properties(iotox.client-help PROPERTIES
        PASS_REGULAR_EXPRESSION "own your machines from an ordinary shell"
    )
    add_test(
        NAME iotox.repo-release-plan
        COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/tools/iotox-repo.sh
            release-plan founder-preview
    )
    set_tests_properties(iotox.repo-release-plan PROPERTIES
        PASS_REGULAR_EXPRESSION "iotox-release-plan-v1"
        TIMEOUT 10
    )
    add_test(
        NAME iotox.repo-stable-evidence-plan
        COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/tools/iotox-repo.sh
            stable-evidence-plan
    )
    set_tests_properties(iotox.repo-stable-evidence-plan PROPERTIES
        PASS_REGULAR_EXPRESSION "iotox-stable-evidence-plan-v1"
        TIMEOUT 10
    )
    add_test(NAME iotox.bootstrap-seeds COMMAND iotox bootstrap-seeds)
    set_tests_properties(iotox.bootstrap-seeds PROPERTIES
        PASS_REGULAR_EXPRESSION "snapshot-date=2026-08-13"
    )
    add_test(
        NAME iotox.recall-generate
        COMMAND ${CMAKE_COMMAND}
            -DIOTOX_EXECUTABLE=$<TARGET_FILE:iotox>
            -P ${CMAKE_CURRENT_SOURCE_DIR}/cmake/CheckRecallGenerate.cmake
    )
    set_tests_properties(iotox.recall-generate PROPERTIES
        PASS_REGULAR_EXPRESSION "phrase suppressed"
    )
    add_test(
        NAME iotox.client-absent-daemon
        COMMAND iotox --runtime /tmp/iotox-ctest-deliberately-absent ping
    )
    set_tests_properties(iotox.client-absent-daemon PROPERTIES
        WILL_FAIL TRUE
    )
    add_test(
        NAME iotox.terminal-invalid-key
        COMMAND iotox terminal 00
    )
    set_tests_properties(iotox.terminal-invalid-key PROPERTIES
        WILL_FAIL TRUE
    )
    add_test(
        NAME iotox.terminal-absent-daemon
        COMMAND iotox --runtime /tmp/iotox-terminal-ctest-deliberately-absent
            terminal 5252525252525252525252525252525252525252525252525252525252525252
    )
    set_tests_properties(iotox.terminal-absent-daemon PROPERTIES
        WILL_FAIL TRUE
    )
    find_package(Python3 QUIET COMPONENTS Interpreter)
    if(Python3_Interpreter_FOUND)
        add_test(
            NAME iotox.human-cli
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_human_cli.py
                $<TARGET_FILE:iotox>
        )
        set_tests_properties(iotox.human-cli PROPERTIES
            ENVIRONMENT "${IOTOX_CTEST_RUNTIME_ENV}"
            PASS_REGULAR_EXPRESSION "IoTox human CLI process test: PASS"
            TIMEOUT 20
        )
        add_test(
            NAME iotox.docs-coherence
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_docs_coherence.py
                ${CMAKE_CURRENT_SOURCE_DIR}
                $<TARGET_FILE:iotox>
        )
        set_tests_properties(iotox.docs-coherence PROPERTIES
            PASS_REGULAR_EXPRESSION "IoTox docs coherence test: PASS"
            TIMEOUT 20
        )
        add_test(
            NAME iotox.socks5-forwarder
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_socks5_forwarder.py
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/run-socks5-forwarder.py
        )
        set_tests_properties(iotox.socks5-forwarder PROPERTIES TIMEOUT 15)
        add_test(
            NAME iotox.socks5-adversary
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_socks5_adversary.py
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/run-socks5-forwarder.py
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/run-socks5-adversary.py
        )
        set_tests_properties(iotox.socks5-adversary PROPERTIES TIMEOUT 15)
        add_test(
            NAME iotox.i2p-sam-socks-adapter
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_i2p_sam_socks.py
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/run-i2p-sam-socks.py
        )
        set_tests_properties(iotox.i2p-sam-socks-adapter PROPERTIES TIMEOUT 30)
        add_test(
            NAME iotox.i2p-sam-service-forward
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_i2p_sam_forward.py
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/run-i2p-sam-forward.py
        )
        set_tests_properties(iotox.i2p-sam-service-forward PROPERTIES TIMEOUT 30)
        add_test(
            NAME iotox.i2p-sam-two-router-smoke
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/run-i2p-sam-smoke.py
                --self-test
        )
        set_tests_properties(iotox.i2p-sam-two-router-smoke PROPERTIES TIMEOUT 15)
        add_test(
            NAME iotox.i2p-tox-fronts
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/run-i2p-tox-fronts.py
                --self-test
        )
        set_tests_properties(iotox.i2p-tox-fronts PROPERTIES
            PASS_REGULAR_EXPRESSION "I2P Tox fronts self-test: PASS"
            TIMEOUT 15
        )
        add_test(
            NAME iotox.i2p-sam-smoke-verifier
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify-i2p-sam-smoke.py
                ${CMAKE_CURRENT_SOURCE_DIR}/artifacts/rev0045/i2p-sam-two-router-smoke.json
        )
        set_tests_properties(iotox.i2p-sam-smoke-verifier PROPERTIES TIMEOUT 15)
        add_test(
            NAME iotox.route-target-process
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_route_target_process.py
                $<TARGET_FILE:iotox>
                $<TARGET_FILE:iotox_mock_toxcore>
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/run-socks5-forwarder.py
        )
        set_tests_properties(iotox.route-target-process PROPERTIES TIMEOUT 30)
        add_test(
            NAME iotox.operator-tor-smoke
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/run-tox-operator-tor-smoke.py
                --self-test
        )
        set_tests_properties(iotox.operator-tor-smoke PROPERTIES
            PASS_REGULAR_EXPRESSION "iotox operator Tor smoke self-test: PASS"
            TIMEOUT 15
        )
        add_test(
            NAME iotox.operator-tor-receipt-verifier
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify-tox-operator-tor-smoke.py
                --self-test
        )
        set_tests_properties(iotox.operator-tor-receipt-verifier PROPERTIES
            PASS_REGULAR_EXPRESSION
                "iotox operator Tor receipt verifier self-test: PASS"
            TIMEOUT 15
        )
        add_test(
            NAME iotox.workspace-cleaner
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/clean-workspace.py
                --self-test
        )
        set_tests_properties(iotox.workspace-cleaner PROPERTIES
            PASS_REGULAR_EXPRESSION "iotox workspace cleaner self-test: PASS"
            TIMEOUT 60
        )
        add_test(
            NAME iotox.sandwurm-vm-smoke-verifier
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify-sandwurm-vm-smoke.py
                --self-test
        )
        set_tests_properties(iotox.sandwurm-vm-smoke-verifier PROPERTIES
            PASS_REGULAR_EXPRESSION "sandwurm-vm-smoke verifier self-test: PASS"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-three-writer-sandwurm-verifier
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify-sync-three-writer-sandwurm.py
                --self-test
        )
        set_tests_properties(iotox.sync-three-writer-sandwurm-verifier PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-three-writer Sandwurm verifier self-test: PASS"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-three-writer-sandwurm-exporter
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/export-sync-three-writer-sandwurm.py
                --self-test
        )
        set_tests_properties(iotox.sync-three-writer-sandwurm-exporter PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-three-writer Sandwurm exporter self-test: PASS"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-three-writer-soak-status
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/inspect-sync-three-writer-soak.py
                --self-test
        )
        set_tests_properties(iotox.sync-three-writer-soak-status PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-three-writer soak status self-test: PASS"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-three-writer-soak-watch
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/watch-sync-three-writer-soak.py
                --self-test
        )
        set_tests_properties(iotox.sync-three-writer-soak-watch PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-three-writer soak watch self-test: PASS"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.massive-soak-runner
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/run-massive-soak.py
                --self-test
        )
        set_tests_properties(iotox.massive-soak-runner PROPERTIES
            PASS_REGULAR_EXPRESSION
                "iotox-massive-soak-self-test=pass"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-power-cut-rehearsal-runner
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/run-sync-power-cut-rehearsal.py
                --self-test
        )
        set_tests_properties(iotox.sync-power-cut-rehearsal-runner PROPERTIES
            PASS_REGULAR_EXPRESSION "sync-power-cut-rehearsal-self-test=pass"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-power-cut-sandwurm-runner
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/run-sync-power-cut-sandwurm.py
                --self-test
        )
        set_tests_properties(iotox.sync-power-cut-sandwurm-runner PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-power-cut-sandwurm-runner-self-test=pass"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-power-cut-sandwurm-verifier
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify-sync-power-cut-sandwurm.py
                --self-test
        )
        set_tests_properties(iotox.sync-power-cut-sandwurm-verifier PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-power-cut-sandwurm-verifier-self-test=pass"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-power-cut-sandwurm-exporter
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/export-sync-power-cut-sandwurm.py
                --self-test
        )
        set_tests_properties(iotox.sync-power-cut-sandwurm-exporter PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-power-cut-sandwurm-exporter-self-test=pass"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-metadata-corruption-rehearsal
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/run-sync-metadata-corruption-rehearsal.py
                --self-test
        )
        set_tests_properties(iotox.sync-metadata-corruption-rehearsal PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-metadata-corruption-rehearsal-self-test=pass"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-metadata-corruption-sandwurm-verifier
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify-sync-metadata-corruption-sandwurm.py
                --self-test
        )
        set_tests_properties(
            iotox.sync-metadata-corruption-sandwurm-verifier PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-metadata-corruption-sandwurm-verifier-self-test=pass"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-metadata-corruption-sandwurm-exporter
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/export-sync-metadata-corruption-sandwurm.py
                --self-test
        )
        set_tests_properties(
            iotox.sync-metadata-corruption-sandwurm-exporter PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-metadata-corruption-sandwurm-exporter-self-test=pass"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-dishonest-storage-runner
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/run-sync-dishonest-storage-drill.py
                --self-test
        )
        set_tests_properties(
            iotox.sync-dishonest-storage-runner PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-dishonest-storage-drill-runner-self-test=pass"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-dishonest-storage-verifier
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify-sync-dishonest-storage-drill.py
                --self-test
        )
        set_tests_properties(
            iotox.sync-dishonest-storage-verifier PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-dishonest-storage-drill-verifier-self-test=pass"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-dishonest-storage-matrix-runner
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/run-sync-dishonest-storage-matrix.py
                --self-test
        )
        set_tests_properties(
            iotox.sync-dishonest-storage-matrix-runner PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-dishonest-storage-matrix-runner-self-test=pass"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-dishonest-storage-matrix-verifier
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify-sync-dishonest-storage-matrix.py
                --self-test
        )
        set_tests_properties(
            iotox.sync-dishonest-storage-matrix-verifier PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-dishonest-storage-matrix-verifier-self-test=pass"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-log-writes-prefix-replay-runner
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/run-sync-log-writes-prefix-replay.py
                --self-test
        )
        set_tests_properties(
            iotox.sync-log-writes-prefix-replay-runner PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-log-writes-prefix-replay-runner-self-test=pass"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-log-writes-prefix-replay-verifier
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify-sync-log-writes-prefix-replay.py
                --self-test
        )
        set_tests_properties(
            iotox.sync-log-writes-prefix-replay-verifier PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-log-writes-prefix-replay-verifier-self-test=pass"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-production-prefix-replay-runner
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/run-sync-production-prefix-replay.py
                --self-test
        )
        set_tests_properties(
            iotox.sync-production-prefix-replay-runner PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-production-prefix-replay-runner-self-test=pass"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-production-prefix-replay-verifier
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify-sync-production-prefix-replay.py
                --self-test
        )
        set_tests_properties(
            iotox.sync-production-prefix-replay-verifier PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-production-prefix-replay-verifier-self-test=pass"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-backup-custody-verifier
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify-sync-backup-custody.py
                --self-test
        )
        set_tests_properties(
            iotox.sync-backup-custody-verifier PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-backup-custody-verifier-self-test=pass"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.storage-readiness
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/qualify-storage-readiness.py
                --self-test
        )
        set_tests_properties(
            iotox.storage-readiness PROPERTIES
            PASS_REGULAR_EXPRESSION
                "iotox-storage-readiness-self-test=pass"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-precious-data-gates-plan
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/plan-sync-precious-data-gates.py
                --self-test
        )
        set_tests_properties(
            iotox.sync-precious-data-gates-plan PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-precious-data-gates-plan-self-test=pass"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-projection-descriptor-rehearsal
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/run-sync-projection-descriptor-rehearsal.py
                --self-test
        )
        set_tests_properties(
            iotox.sync-projection-descriptor-rehearsal PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-projection-descriptor-rehearsal-self-test=pass"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-projection-descriptor-sandwurm-verifier
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify-sync-projection-descriptor-sandwurm.py
                --self-test
        )
        set_tests_properties(
            iotox.sync-projection-descriptor-sandwurm-verifier PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-projection-descriptor-sandwurm-verifier-self-test=pass"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-shadow-runner
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/run-sync-shadow.py
                --self-test
        )
        set_tests_properties(iotox.sync-shadow-runner PROPERTIES
            PASS_REGULAR_EXPRESSION "sync-shadow self-test: PASS"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-shadow-sandwurm-verifier
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify-sync-shadow-sandwurm.py
                --self-test
        )
        set_tests_properties(iotox.sync-shadow-sandwurm-verifier PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-shadow Sandwurm verifier self-test: PASS"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sync-shadow-sandwurm-exporter
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/export-sync-shadow-sandwurm.py
                --self-test
        )
        set_tests_properties(iotox.sync-shadow-sandwurm-exporter PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sync-shadow Sandwurm exporter self-test: PASS"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.route-policy-campaign
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/qualify-route-policy-campaign.py
                --self-test
        )
        set_tests_properties(iotox.route-policy-campaign PROPERTIES
            PASS_REGULAR_EXPRESSION "route-policy campaign self-test: PASS"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.spdx-sbom
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/generate-sbom.py
                --self-test
        )
        set_tests_properties(iotox.spdx-sbom PROPERTIES
            PASS_REGULAR_EXPRESSION "iotox SPDX SBOM self-test: PASS"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sandwurm-pair-verifier
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify-sandwurm-pair.py
                --self-test
        )
        set_tests_properties(iotox.sandwurm-pair-verifier PROPERTIES
            PASS_REGULAR_EXPRESSION "sandwurm-pair verifier self-test: PASS"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sandwurm-pair-exporter
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/export-sandwurm-pair.py
                --self-test
        )
        set_tests_properties(iotox.sandwurm-pair-exporter PROPERTIES
            PASS_REGULAR_EXPRESSION "sandwurm-pair exporter self-test: PASS"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.actual-tor-path-population-analyzer
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/analyze-actual-tor-path-population.py
                --self-test
        )
        set_tests_properties(iotox.actual-tor-path-population-analyzer PROPERTIES
            PASS_REGULAR_EXPRESSION
                "actual-Tor path-population analyzer self-test: PASS"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.content-lane-counterbalance-analyzer
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/analyze-content-lane-counterbalance.py
                --self-test
        )
        set_tests_properties(iotox.content-lane-counterbalance-analyzer PROPERTIES
            PASS_REGULAR_EXPRESSION
                "content-lane counterbalance analyzer self-test: PASS"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sandwurm-pair-runner
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/run-sandwurm-pair.py
                --self-test
        )
        set_tests_properties(iotox.sandwurm-pair-runner PROPERTIES
            PASS_REGULAR_EXPRESSION "sandwurm-pair runner self-test: PASS"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.sandwurm-provider-rolling-verifier
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/verify-sandwurm-provider-rolling.py
                --self-test
        )
        set_tests_properties(iotox.sandwurm-provider-rolling-verifier PROPERTIES
            PASS_REGULAR_EXPRESSION
                "sandwurm-provider-rolling verifier self-test: PASS"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.ratox-r7-analyzer
            COMMAND ${CMAKE_COMMAND} -E env
                "PYTHONPATH=${CMAKE_CURRENT_SOURCE_DIR}/tools"
                ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/analyze-ratox-r7.py
                --self-test
        )
        set_tests_properties(iotox.ratox-r7-analyzer PROPERTIES
            PASS_REGULAR_EXPRESSION "ratox-r7-analyzer self-test: PASS"
            TIMEOUT 60
        )
        add_test(
            NAME iotox.ratox-terminal-probe
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/ratox-terminal-probe.py
                --self-test
        )
        set_tests_properties(iotox.ratox-terminal-probe PROPERTIES
            PASS_REGULAR_EXPRESSION "ratox-terminal probe self-test: PASS"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.ratox-cli-reconnect-probe
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/ratox-cli-reconnect-probe.py
                --self-test
        )
        set_tests_properties(iotox.ratox-cli-reconnect-probe PROPERTIES
            PASS_REGULAR_EXPRESSION
                "ratox CLI reconnect probe self-test: PASS"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.content-ratox-latency-summarizer
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/summarize-content-ratox-latency.py
                --self-test
        )
        set_tests_properties(iotox.content-ratox-latency-summarizer PROPERTIES
            PASS_REGULAR_EXPRESSION
                "summarize-content-ratox-latency self-test passed"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.ratox-route-impairment-analyzer
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/analyze-ratox-route-impairment.py
                --self-test
        )
        set_tests_properties(iotox.ratox-route-impairment-analyzer PROPERTIES
            PASS_REGULAR_EXPRESSION
                "ratox route-impairment analyzer self-test: PASS"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.ratox-route-loss-analyzer
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/analyze-ratox-route-loss.py
                --self-test
        )
        set_tests_properties(iotox.ratox-route-loss-analyzer PROPERTIES
            PASS_REGULAR_EXPRESSION
                "ratox route-loss analyzer self-test: PASS"
            TIMEOUT 30
        )
        add_test(
            NAME iotox.process-resource-capture
            COMMAND ${Python3_EXECUTABLE}
                ${CMAKE_CURRENT_SOURCE_DIR}/tools/capture-process-resources.py
                --self-test
        )
        set_tests_properties(iotox.process-resource-capture PROPERTIES
            PASS_REGULAR_EXPRESSION "process resource capture self-test: PASS"
            TIMEOUT 30
        )
        if(IOTOX_ENABLE_ASAN OR IOTOX_ENABLE_TSAN)
            # The analyzer intentionally drives a dense Python model and can
            # starve concurrently scheduled shadow-runtime registries. Keep
            # the oracle exact and isolate its scheduler budget instead of
            # weakening either the sanitizer shards or analyzer timeout.
            set_tests_properties(iotox.ratox-r7-analyzer PROPERTIES
                RUN_SERIAL TRUE
            )
        endif()
    endif()
    if(IOTOX_VALIDATE_REVISION_CUBE_LAYOUT)
        add_test(
            NAME iotox.lone-entrance-layout
            COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/tools/check-lone-entrance.sh
        )
    endif()

    if(IOTOX_BUILD_MUTORR_RESEARCH AND IOTOX_BUILD_RESEARCH_LAB)
        add_test(
            NAME iotox.research-cube-demo
            COMMAND iotox_lab cube-demo --nodes 30 --neighbors 4 --replicas 3 --namespaces 1024
        )
        set_tests_properties(iotox.research-cube-demo PROPERTIES
            PASS_REGULAR_EXPRESSION "cube-edges=60.*full-mesh-edges=435"
        )
    endif()

    if(IOTOX_BUILD_MUTORR_RESEARCH AND IOTOX_BUILD_BENCHMARK)
        add_test(
            NAME iotox.research-benchmark-smoke
            COMMAND iotox_bench --nodes 30 --namespaces 1000 --rounds 1
        )
        set_tests_properties(iotox.research-benchmark-smoke PROPERTIES
            PASS_REGULAR_EXPRESSION "custodian-select-ops-per-second="
        )
    endif()

    get_property(IOTOX_CONFIGURED_TESTS DIRECTORY PROPERTY TESTS)
    foreach(IOTOX_CONFIGURED_TEST IN LISTS IOTOX_CONFIGURED_TESTS)
        set_property(TEST ${IOTOX_CONFIGURED_TEST} APPEND PROPERTY
            ENVIRONMENT "${IOTOX_CTEST_RUNTIME_ENV}")
    endforeach()

    if(IOTOX_BUILD_FUZZER)
        if(NOT CMAKE_CXX_COMPILER_ID MATCHES "Clang")
            message(FATAL_ERROR "IOTOX_BUILD_FUZZER requires Clang")
        endif()
        add_executable(iotox_frame_fuzzer
            tests/fuzz_frame.cpp
            src/protocol/frame.cpp
            src/protocol/session.cpp
        )
        add_executable(iotox_session_fuzzer
            tests/fuzz_session.cpp
            src/protocol/frame.cpp
            src/protocol/session.cpp
        )
        add_executable(iotox_local_control_fuzzer
            tests/fuzz_local_control.cpp
            src/local/control_protocol.cpp
        )
        add_executable(iotox_terminal_protocol_fuzzer
            tests/fuzz_terminal_protocol.cpp
            src/local/terminal_protocol.cpp
        )
        add_executable(iotox_command_fuzzer
            tests/fuzz_command.cpp
        )
        target_link_libraries(iotox_command_fuzzer PRIVATE IoTox::core)
        add_executable(iotox_terminal_profile_fuzzer
            tests/fuzz_terminal_profile.cpp
        )
        target_link_libraries(iotox_terminal_profile_fuzzer PRIVATE IoTox::core)
        add_executable(iotox_terminal_cgroup_fuzzer
            tests/fuzz_terminal_cgroup.cpp
        )
        target_link_libraries(iotox_terminal_cgroup_fuzzer PRIVATE IoTox::core)
        add_executable(iotox_update_bundle_fuzzer
            tests/fuzz_update_bundle.cpp
        )
        target_link_libraries(iotox_update_bundle_fuzzer PRIVATE IoTox::core)
        # The command parser lives in the product library. Instrument the
        # archive without supplying a second fuzzer main so this target sees
        # coverage and sanitizer checks across the exact production code.
        target_compile_options(iotox_core PRIVATE
            -fsanitize=fuzzer-no-link,address,undefined)
        # iotox_core is a static archive. Every executable or shared object that
        # consumes its instrumented objects must also link the ASan/UBSan
        # runtimes, even when that consumer is an ordinary test or the product
        # binary rather than a libFuzzer target. Keep the fuzzer main private to
        # the dedicated targets below while exporting only the sanitizer runtime
        # requirement through the archive's link interface.
        target_link_options(iotox_core INTERFACE
            -fsanitize=address,undefined)

        add_executable(iotox_authority_fuzzer
            tests/fuzz_authority.cpp
            src/security/authority.cpp
            src/security/authority_session.cpp
            src/security/identity.cpp
            src/security/random.cpp
            src/security/sodium.cpp
            src/protocol/frame.cpp
            src/protocol/session.cpp
            src/state_store.cpp
        )
        add_executable(iotox_ratox_frame_fuzzer
            tests/fuzz_ratox_frame.cpp
            src/protocol/ratox.cpp
        )
        add_executable(iotox_interactive_state_fuzzer
            tests/fuzz_interactive_state.cpp
            src/interactive.cpp
            src/interactive_session.cpp
        )
        add_executable(iotox_interactive_service_fuzzer
            tests/fuzz_interactive_service.cpp
        )
        target_link_libraries(iotox_interactive_service_fuzzer PRIVATE
            IoTox::core)
        target_link_libraries(iotox_authority_fuzzer PRIVATE
            Threads::Threads
            ${CMAKE_DL_LIBS}
        )
        set(IOTOX_FUZZ_TARGETS
            iotox_frame_fuzzer
            iotox_session_fuzzer
            iotox_local_control_fuzzer
            iotox_terminal_protocol_fuzzer
            iotox_command_fuzzer
            iotox_terminal_profile_fuzzer
            iotox_terminal_cgroup_fuzzer
            iotox_update_bundle_fuzzer
            iotox_authority_fuzzer
            iotox_ratox_frame_fuzzer
            iotox_interactive_state_fuzzer
            iotox_interactive_service_fuzzer
        )

        if(IOTOX_BUILD_MUTORR_RESEARCH)
            add_executable(iotox_mutorr_head_fuzzer
                incubator/mutorr/tests/fuzz_mutorr_head.cpp
                incubator/mutorr/src/mutorr/head.cpp
                incubator/mutorr/src/mutorr/id.cpp
            )
            target_include_directories(iotox_mutorr_head_fuzzer PRIVATE
                ${CMAKE_CURRENT_SOURCE_DIR}/incubator/mutorr/include
            )
            list(APPEND IOTOX_FUZZ_TARGETS iotox_mutorr_head_fuzzer)
        endif()

        foreach(fuzzer_target IN LISTS IOTOX_FUZZ_TARGETS)
            target_compile_features(${fuzzer_target} PRIVATE cxx_std_20)
            target_include_directories(${fuzzer_target} PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/include)
            target_compile_options(${fuzzer_target} PRIVATE -fsanitize=fuzzer,address,undefined)
            target_link_options(${fuzzer_target} PRIVATE -fsanitize=fuzzer,address,undefined)
            iotox_set_project_warnings(${fuzzer_target})
        endforeach()
    endif()
endif()

# The installed product surface is deliberately one executable. Optional research
# programs are build/test instruments and never enter the install graph.
install(TARGETS iotox RUNTIME DESTINATION bin)
