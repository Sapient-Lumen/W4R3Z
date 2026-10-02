cmake_minimum_required(VERSION 3.20)

set(TOXSYNC_PROJECT_VERSION "0.7.0")
if(CMAKE_SOURCE_DIR STREQUAL CMAKE_CURRENT_SOURCE_DIR)
    project(toxsync VERSION ${TOXSYNC_PROJECT_VERSION} LANGUAGES CXX)
    include(CTest)
endif()

option(TOXSYNC_WARNINGS_AS_ERRORS "Treat toxsync warnings as errors" ON)
option(TOXSYNC_BUILD_CLI "Build the toxsync command-line tool" ON)
option(TOXSYNC_BUILD_TESTS "Build native C++ toxsync tests" ON)
option(TOXSYNC_BUILD_BENCHMARK "Build the native C++ toxsync benchmark" ON)
option(TOXSYNC_BUILD_FUZZER "Build bounded decoder fuzz targets (Clang only)" OFF)
option(TOXSYNC_ENABLE_SIMD "Enable baseline architecture SIMD acceleration" ON)
set(TOXSYNC_CRYPTO_BACKEND "AUTO" CACHE STRING "SHA-256 backend: AUTO, OPENSSL, or BUILTIN")
set_property(CACHE TOXSYNC_CRYPTO_BACKEND PROPERTY STRINGS AUTO OPENSSL BUILTIN)
string(TOUPPER "${TOXSYNC_CRYPTO_BACKEND}" TOXSYNC_CRYPTO_BACKEND_NORMALIZED)
if(NOT TOXSYNC_CRYPTO_BACKEND_NORMALIZED MATCHES "^(AUTO|OPENSSL|BUILTIN)$")
    message(FATAL_ERROR "TOXSYNC_CRYPTO_BACKEND must be AUTO, OPENSSL, or BUILTIN")
endif()
add_library(toxsync STATIC
    src/apply.cpp
    src/artifact_hasher.cpp
    src/content_availability.cpp
    src/content_fabric.cpp
    src/content_scheduler.cpp
    src/content_retention.cpp
    src/content_store.cpp
    src/hash.cpp
    src/head.cpp
    src/index.cpp
    src/index_file.cpp
    src/lane_budget.cpp
    src/planner.cpp
    src/publication.cpp
    src/multisource.cpp
    src/paged_content.cpp
    src/range_source.cpp
    src/streaming.cpp
    src/rolling_checksum.cpp
    src/treepack.cpp
    src/wire.cpp
)
add_library(toxsync::toxsync ALIAS toxsync)
target_compile_features(toxsync PUBLIC cxx_std_20)
if(NOT TOXSYNC_ENABLE_SIMD)
    target_compile_definitions(toxsync PRIVATE TOXSYNC_DISABLE_SIMD=1)
    set(TOXSYNC_SELECTED_ROLLING_BACKEND "scalar-unrolled")
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "^(x86_64|AMD64|amd64)$")
    set(TOXSYNC_SELECTED_ROLLING_BACKEND "sse2")
elseif(CMAKE_SYSTEM_PROCESSOR MATCHES "^(aarch64|arm64|ARM64)$")
    set(TOXSYNC_SELECTED_ROLLING_BACKEND "aarch64-neon")
else()
    set(TOXSYNC_SELECTED_ROLLING_BACKEND "scalar-unrolled")
endif()
message(STATUS "toxsync rolling-checksum backend: ${TOXSYNC_SELECTED_ROLLING_BACKEND}")

target_include_directories(toxsync PUBLIC
    $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
    $<INSTALL_INTERFACE:include>
)

if(NOT TOXSYNC_CRYPTO_BACKEND_NORMALIZED STREQUAL "BUILTIN")
    find_package(OpenSSL QUIET COMPONENTS Crypto)
endif()
if(OpenSSL_FOUND AND NOT TOXSYNC_CRYPTO_BACKEND_NORMALIZED STREQUAL "BUILTIN")
    target_compile_definitions(toxsync PRIVATE TOXSYNC_HAVE_OPENSSL=1)
    target_link_libraries(toxsync PRIVATE OpenSSL::Crypto)
    set(TOXSYNC_SELECTED_CRYPTO_BACKEND "openssl-evp")
    set(TOXSYNC_SIGNING_AVAILABLE ON)
elseif(TOXSYNC_CRYPTO_BACKEND_NORMALIZED STREQUAL "OPENSSL")
    message(FATAL_ERROR "TOXSYNC_CRYPTO_BACKEND=OPENSSL requested, but OpenSSL::Crypto was not found")
else()
    set(TOXSYNC_SELECTED_CRYPTO_BACKEND "builtin-cpp")
    set(TOXSYNC_SIGNING_AVAILABLE OFF)
endif()
message(STATUS "toxsync SHA-256 backend: ${TOXSYNC_SELECTED_CRYPTO_BACKEND}")


function(toxsync_warnings target)
    if(MSVC)
        target_compile_options(${target} PRIVATE /W4)
        if(TOXSYNC_WARNINGS_AS_ERRORS)
            target_compile_options(${target} PRIVATE /WX)
        endif()
    else()
        target_compile_options(${target} PRIVATE -Wall -Wextra -Wshadow -Wconversion -Wsign-conversion)
        if(TOXSYNC_WARNINGS_AS_ERRORS)
            target_compile_options(${target} PRIVATE -Werror)
        endif()
    endif()
endfunction()
function(toxsync_integrate_parent target)
    if(COMMAND iotox_enable_sanitizers)
        iotox_enable_sanitizers(${target})
    endif()
    if(COMMAND iotox_configure_optimization)
        iotox_configure_optimization(${target})
    endif()
endfunction()
toxsync_warnings(toxsync)
toxsync_integrate_parent(toxsync)

if(TOXSYNC_BUILD_FUZZER)
    if(NOT CMAKE_CXX_COMPILER_ID MATCHES "Clang")
        message(FATAL_ERROR "TOXSYNC_BUILD_FUZZER requires Clang")
    endif()
    target_compile_options(toxsync PRIVATE
        -fsanitize=fuzzer-no-link,address,undefined)
    target_link_options(toxsync INTERFACE -fsanitize=address,undefined)
endif()

if(TOXSYNC_BUILD_CLI)
    add_executable(toxsync_cli tools/toxsync.cpp)
    set_target_properties(toxsync_cli PROPERTIES OUTPUT_NAME toxsync)
    target_compile_features(toxsync_cli PRIVATE cxx_std_20)
    target_link_libraries(toxsync_cli PRIVATE toxsync::toxsync)
    toxsync_warnings(toxsync_cli)
    toxsync_integrate_parent(toxsync_cli)
endif()

if(TOXSYNC_BUILD_TESTS AND BUILD_TESTING)
    add_executable(toxsync_tests
        tests/test_main.cpp
        tests/test_apply.cpp
        tests/test_content_availability.cpp
        tests/test_content_fabric.cpp
        tests/test_content_retention.cpp
        tests/test_content_scheduler.cpp
        tests/test_content_store.cpp
        tests/test_head.cpp
        tests/test_multisource.cpp
        tests/test_paged_content.cpp
        tests/test_hash.cpp
        tests/test_index.cpp
        tests/test_index_file.cpp
        tests/test_lane_budget.cpp
        tests/test_planner.cpp
        tests/test_publication.cpp
        tests/test_streaming.cpp
        tests/test_treepack.cpp
        tests/test_wire.cpp
    )
    target_compile_features(toxsync_tests PRIVATE cxx_std_20)
    target_include_directories(toxsync_tests PRIVATE tests)
    target_link_libraries(toxsync_tests PRIVATE toxsync::toxsync)
    toxsync_warnings(toxsync_tests)
    toxsync_integrate_parent(toxsync_tests)
    add_test(NAME toxsync.unit-and-integration COMMAND toxsync_tests)

    if(TOXSYNC_BUILD_CLI)
        add_test(NAME toxsync.cli-version COMMAND toxsync_cli version)
        set_tests_properties(toxsync.cli-version PROPERTIES PASS_REGULAR_EXPRESSION "toxsync ${TOXSYNC_PROJECT_VERSION}")
        add_test(
            NAME toxsync.cli-transaction
            COMMAND ${CMAKE_COMMAND}
                "-DTOXSYNC_CLI=$<TARGET_FILE:toxsync_cli>"
                "-DTOXSYNC_TEST_ROOT=${CMAKE_CURRENT_BINARY_DIR}/toxsync-cli-transaction"
                "-DTOXSYNC_SIGNING_AVAILABLE=${TOXSYNC_SIGNING_AVAILABLE}"
                -P ${CMAKE_CURRENT_SOURCE_DIR}/tests/test_cli.cmake
        )
    endif()
endif()

if(TOXSYNC_BUILD_BENCHMARK)
    add_executable(toxsync_bench bench/benchmark.cpp)
    target_compile_features(toxsync_bench PRIVATE cxx_std_20)
    target_link_libraries(toxsync_bench PRIVATE toxsync::toxsync)
    toxsync_warnings(toxsync_bench)
    toxsync_integrate_parent(toxsync_bench)
endif()

if(TOXSYNC_BUILD_FUZZER)
    add_executable(toxsync_wire_fuzzer tests/fuzz_wire.cpp)
    add_executable(toxsync_metadata_fuzzer tests/fuzz_metadata.cpp)
    add_executable(toxsync_files_fuzzer tests/fuzz_files.cpp)
    foreach(fuzzer_target IN ITEMS
            toxsync_wire_fuzzer
            toxsync_metadata_fuzzer
            toxsync_files_fuzzer)
        target_compile_features(${fuzzer_target} PRIVATE cxx_std_20)
        target_link_libraries(${fuzzer_target} PRIVATE toxsync::toxsync)
        target_compile_options(${fuzzer_target} PRIVATE
            -fsanitize=fuzzer,address,undefined)
        target_link_options(${fuzzer_target} PRIVATE
            -fsanitize=fuzzer,address,undefined)
        toxsync_warnings(${fuzzer_target})
    endforeach()
endif()

if(TOXSYNC_BUILD_BENCHMARK)
    add_executable(toxsync_content_bench bench/content_benchmark.cpp)
    target_compile_features(toxsync_content_bench PRIVATE cxx_std_20)
    target_link_libraries(toxsync_content_bench PRIVATE toxsync::toxsync)
    toxsync_warnings(toxsync_content_bench)
    toxsync_integrate_parent(toxsync_content_bench)
endif()

if(TOXSYNC_BUILD_BENCHMARK)
    add_executable(toxsync_large_bench bench/large_benchmark.cpp)
    target_compile_features(toxsync_large_bench PRIVATE cxx_std_20)
    target_link_libraries(toxsync_large_bench PRIVATE toxsync::toxsync)
    toxsync_warnings(toxsync_large_bench)
    toxsync_integrate_parent(toxsync_large_bench)
endif()

if(TOXSYNC_BUILD_BENCHMARK)
    add_executable(toxsync_fabric_bench bench/fabric_benchmark.cpp)
    target_compile_features(toxsync_fabric_bench PRIVATE cxx_std_20)
    target_link_libraries(toxsync_fabric_bench PRIVATE toxsync::toxsync)
    toxsync_warnings(toxsync_fabric_bench)
    toxsync_integrate_parent(toxsync_fabric_bench)
endif()

install(TARGETS toxsync
    ARCHIVE DESTINATION lib
    LIBRARY DESTINATION lib
    RUNTIME DESTINATION bin
)
if(TOXSYNC_BUILD_CLI)
    install(TARGETS toxsync_cli RUNTIME DESTINATION bin)
endif()
install(DIRECTORY include/ DESTINATION include)
